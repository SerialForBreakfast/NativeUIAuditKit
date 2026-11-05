"""Verify exact YOLO initialization before the first optimizer step."""
import torch
import research_queue as q


class InitializerGuard:
    def __init__(self, model, seed, output):
        q.require(type(seed) is int and seed in (42,371),'detector_seed')
        self.reference={key:value.detach().cpu().float().clone() for key,value in model.state_dict().items()}
        self.seed,self.output,self.calls=seed,output,0

    def verify(self, trainer):
        state=trainer.model.state_dict()
        q.require(trainer.args.seed==self.seed,'detector_initializer_seed')
        q.require(set(state)==set(self.reference),'detector_initializer_keys')
        changed=[key for key,value in state.items() if not torch.equal(value.detach().cpu().float(),self.reference[key])]
        q.require(not changed,'detector_initializer_changed:'+','.join(changed[:5]))
        self.calls+=1
        q.save(self.output/'initialization.json',dict(version='detector-initialization567-v1',seed=self.seed,
            tensors=len(state),verifiedBeforeFirstOptimizerStep=True,allTensorsPreserved=True,modelAccepted=False))
