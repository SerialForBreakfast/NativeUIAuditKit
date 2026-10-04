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


def geometry_loss(torch, logits, truth, use_logits=False,logit_regression=False):
    if logit_regression:
        return torch.nn.functional.smooth_l1_loss(logits,torch.logit(truth.clamp(1e-4,1-1e-4)),beta=1.)
    if use_logits:
        return torch.nn.functional.binary_cross_entropy_with_logits(logits,truth)
    return torch.nn.functional.l1_loss(logits.sigmoid(),truth)


def decode_geometry(torch,indices,values,height,width):
    centers=torch.stack(((indices%width+values[:,:,0])/width,
                         (indices//width+values[:,:,1])/height),dim=2)
    return torch.cat((centers,values[:,:,2:]),dim=2)


def giou_loss(torch,predicted,truth):
    p,t=predicted.reshape(-1,4),truth.reshape(-1,4)
    plo,phi=p[:,:2]-p[:,2:]/2,p[:,:2]+p[:,2:]/2
    tlo,thi=t[:,:2]-t[:,2:]/2,t[:,:2]+t[:,2:]/2
    intersection=(torch.minimum(phi,thi)-torch.maximum(plo,tlo)).clamp(min=0).prod(1)
    union=p[:,2:].prod(1)+t[:,2:].prod(1)-intersection
    enclosure=(torch.maximum(phi,thi)-torch.minimum(plo,tlo)).clamp(min=0).prod(1)
    return (1-intersection/union.clamp(min=1e-8)+(enclosure-union)/enclosure.clamp(min=1e-8)).mean()


def loss(torch, net, images, labels, geometry_logits=False,overlap=False,logit_regression=False):
    cells, geometry, change = net.fields(images)
    indices, truth = targets(torch,labels[:,:8],cells.shape[2],cells.shape[3])
    predicted = geometry.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3)
    total=(torch.nn.functional.cross_entropy(cells.flatten(2).reshape(-1,cells.shape[2]*cells.shape[3]),indices.reshape(-1))
            + geometry_loss(torch,predicted,truth,geometry_logits,logit_regression)
            + torch.nn.functional.binary_cross_entropy_with_logits(change[:,0],labels[:,8]))
    if overlap:
        total=total+giou_loss(torch,decode_geometry(torch,indices,predicted.sigmoid(),cells.shape[2],cells.shape[3]),labels[:,:8])
    return total
