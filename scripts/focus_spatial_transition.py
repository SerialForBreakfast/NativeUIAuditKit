"""Spatial paired-image experimental head. Ground truth is used only by loss()."""


def make_model(torch, global_context=False):
    nn = torch.nn

    class SpatialTransition(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(nn.Conv2d(6,8,3,2,1),nn.ReLU(),
                nn.Conv2d(8,16,3,2,1),nn.ReLU(),nn.Conv2d(16,24,3,1,1),nn.ReLU())
            self.cells = nn.Conv2d(24,2,1)
            self.geometry = nn.Conv2d(24,8,1)
            self.change = nn.Sequential(nn.Flatten(),nn.Linear(24*16*24,64),nn.ReLU(),nn.Linear(64,1))
            if global_context:
                self.context = nn.Sequential(nn.AdaptiveAvgPool2d((4,6)),nn.Flatten(),
                    nn.Linear(24*4*6,64),nn.ReLU(),nn.Linear(64,10*16*24))

        def fields(self, images):
            features = self.encoder(images)
            cells, geometry = self.cells(features), self.geometry(features)
            if hasattr(self,'context'):
                context = self.context(features).reshape(-1,10,16,24)
                cells, geometry = cells+context[:,:2], geometry+context[:,2:]
            return cells, geometry.reshape(-1,2,4,16,24), self.change(features)

        def forward(self, images):
            cells, geometry, change = self.fields(images)
            batch, _, height, width = cells.shape
            indices = cells.flatten(2).argmax(2)
            values = geometry.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3).sigmoid()
            centers = torch.stack(((indices % width + values[:,:,0])/width,
                                   (indices // width + values[:,:,1])/height),dim=2)
            boxes = torch.cat((centers,values[:,:,2:]),dim=2).reshape(batch,8)
            return torch.cat((torch.logit(boxes.clamp(1e-6,1-1e-6)),change),dim=1)

    return SpatialTransition()


def targets(torch, boxes, height=16, width=24):
    boxes = boxes.reshape(-1,2,4)
    scaled = boxes[:,:,:2] * boxes.new_tensor([width,height])
    xy = scaled.floor().long()
    xy[:,:,0].clamp_(0,width-1);xy[:,:,1].clamp_(0,height-1)
    indices = xy[:,:,1]*width+xy[:,:,0]
    geometry = torch.cat((scaled-xy,boxes[:,:,2:]),dim=2)
    return indices, geometry


def loss(torch, net, images, labels):
    cells, geometry, change = net.fields(images)
    indices, truth = targets(torch,labels[:,:8],cells.shape[2],cells.shape[3])
    predicted = geometry.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3).sigmoid()
    return (torch.nn.functional.cross_entropy(cells.flatten(2).reshape(-1,384),indices.reshape(-1))
            + torch.nn.functional.l1_loss(predicted,truth)
            + torch.nn.functional.binary_cross_entropy_with_logits(change[:,0],labels[:,8]))
