"""Require the complete fixed-epoch comparison without changing the trainer."""
import research_queue as q
import hcf_training375

OUT = None


def validate_completion(report):
    q.require(report.get('epochs') == 30, 'detector_epochs_incomplete')


def detector():
    hcf_training375.OUT = OUT
    hcf_training375.detector()
    validate_completion(q.load(OUT / 'fit.json'))
    history = q.load(OUT / 'history.json')
    q.require([row['epoch'] for row in history] == list(range(1, 31)), 'detector_epoch_sequence')
    import torch
    checkpoint = torch.load(OUT / 'detector/weights/last.pt', map_location='cpu', weights_only=False)
    q.require(checkpoint.get('epoch') in (-1, 29), 'detector_terminal_checkpoint_epoch')
    q.require(checkpoint.get('train_results', {}).get('epoch') == list(range(1, 31)),
              'detector_terminal_checkpoint_history')
    q.save(OUT / 'completion.json', dict(epochs=30, terminalCheckpointSHA256=q.digest(OUT / 'detector/weights/last.pt'),
                                       modelAccepted=False))
