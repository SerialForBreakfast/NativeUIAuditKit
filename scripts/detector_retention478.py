"""Keep last and best checkpoints without changing the fixed training comparison."""
import detector_training419 as training
import research_queue as q

OUT = None


def apply_retention(trainer):
    """Use the resident trainer callback before the first training epoch."""
    q.require(trainer.save_period == 1 and trainer.args.save_period == 1,
              'detector_retention_source_changed')
    trainer.save_period = -1
    trainer.args.save_period = -1
    q.save(OUT / 'checkpoint-retention.json', dict(
        version='detector-checkpoint-retention-v1',
        originalSavePeriod=1, savePeriod=-1,
        retained=['last.pt', 'best.pt', 'final.pt'],
        epochsUnchanged=True, resumeQualified=False))


def run():
    # This registry belongs to the isolated job process. Restore it after execution.
    from ultralytics.utils.callbacks import default_callbacks
    callbacks = default_callbacks['on_pretrain_routine_end']
    callbacks.append(apply_retention)
    training.OUT = OUT
    try:
        training.run()
    finally:
        callbacks.remove(apply_retention)
