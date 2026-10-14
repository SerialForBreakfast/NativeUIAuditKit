"""Reject incomplete training state before proposing a continuation."""


def assess(checkpoint):
    required = ('optimizer', 'scheduler', 'random_state')
    missing = [name for name in required if checkpoint.get(name) is None]
    epoch = checkpoint.get('epoch')
    if type(epoch) is not int or epoch < 0:
        missing.append('epoch')
    return dict(completedEpochs=epoch + 1 if type(epoch) is int and epoch >= 0 else None,
                missing=missing, stateComplete=not missing, resumeQualified=False,
                decision='fresh-fixed-run' if missing else 'requires-resume-parity-test')
