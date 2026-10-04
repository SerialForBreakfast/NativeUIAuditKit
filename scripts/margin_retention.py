"""Correctness-gate slack for the existing experimental radial retention head."""
import math
import numpy as np
import retention134 as r

VERSION='correctness-slack-v1'
BOUNDARY=math.log(.85/.15)


def model(features,labels):
    net=r.constrained_model(features,labels)
    signs=2*labels.astype(np.float64)-1
    gap=signs*features[:,0]-BOUNDARY
    r.h.require(np.isfinite(gap).all() and (gap>1e-6).all(),'near_boundary_constraint_requires_review')
    slack=gap-np.minimum(.001,gap/2)
    r.h.require((slack>0).all(),'nonpositive_slack')
    net.change.slack.copy_(r.a.r.d.torch_runtime().from_numpy(slack))
    return net


def preflight(features,labels,x,y):
    torch=r.a.r.d.torch_runtime();net=model(features,labels)
    loss=torch.nn.functional.binary_cross_entropy_with_logits(net.change(torch.from_numpy(x)).flatten(),torch.from_numpy(y))
    loss.backward();gradient=net.change.linear.weight.grad.detach().clone()
    r.h.require(torch.isfinite(gradient).all() and float(gradient.norm())>0,'missing_gradient')
    initial=float(loss.detach());slack=float(net.change.slack.min())
    # Analytical first Adam step with the trainer's default beta/epsilon and lr.01.
    with torch.no_grad():net.change.linear.weight.copy_(-.01*gradient/(gradient.abs()+1e-8))
    net.zero_grad();after=torch.nn.functional.binary_cross_entropy_with_logits(net.change(torch.from_numpy(x)).flatten(),torch.from_numpy(y))
    after.backward();radius=float(net.change.effective()[1].detach());norm=float(net.change.linear.weight.grad.norm())
    r.h.require(radius>0 and math.isfinite(norm) and norm>0,'frozen_first_step')
    return dict(minimumSlack=slack,initialLoss=initial,initialGradientNorm=float(gradient.norm()),
                firstStepRadius=radius,firstStepLoss=float(after.detach()),nextGradientNorm=norm)
