"""Experimental difference-only change head; ordered RGB geometry stays intact."""
from focus_spatial_transition import make_model as spatial_model


def make_model(torch):
    nn=torch.nn
    base=spatial_model(torch,True)
    decode=type(base).forward

    class TemporalTransition(nn.Module):
        def __init__(self,original):
            super().__init__()
            self.encoder=original.encoder;self.cells=original.cells
            self.geometry=original.geometry;self.context=original.context
            self.change=nn.Sequential(nn.Conv2d(3,8,3,2,1),nn.ReLU(),
                nn.Conv2d(8,16,3,2,1),nn.ReLU(),nn.Conv2d(16,24,3,1,1),nn.ReLU(),
                nn.AdaptiveAvgPool2d((4,6)),nn.Flatten(),nn.Linear(24*4*6,32),nn.ReLU(),nn.Linear(32,1))

        def fields(self,images):
            features=self.encoder(images)
            context=self.context(features).reshape(-1,10,16,24)
            cells=self.cells(features)+context[:,:2]
            geometry=self.geometry(features)+context[:,2:]
            change=self.change((images[:,3:]-images[:,:3]).abs())
            return cells,geometry.reshape(-1,2,4,16,24),change

        def forward(self,images):return decode(self,images)

    return TemporalTransition(base)
