"""Use the recorded frozen-backbone architecture for the FDR021 diagnostic."""
import numpy as np
from PIL import Image
import research_queue as q
import hcf361_baseline as baseline

OUT = None


def predict(weights, rows):
    import torch
    import focus_visual_experiment as visual
    config = q.load(OUT/'config.json')
    rep = q.load(q.ROOT/config['preflight']['path'])['representation']
    q.require(rep['kind'] == 'mobilenet_v3_small_frozen' and rep['features'] == 576
              and rep['inputSize'] == [256, 256] and rep['centerCrop'] is False, 'wrong_representation')
    q.require(q.digest(q.ROOT/rep['weights']['path']) == rep['weights']['sha256'], 'backbone_changed')
    network = visual.make_network(rep).features.eval()
    head = torch.nn.Linear(576, 1).eval()
    checkpoint = torch.load(weights, map_location='cpu', weights_only=True)
    head.load_state_dict(checkpoint['state_dict'], strict=True)
    mean = torch.tensor(rep['normalization']['mean'])[None, :, None, None]
    std = torch.tensor(rep['normalization']['std'])[None, :, None, None]
    result = []
    with torch.no_grad():
        for row in rows:
            with Image.open(row['path']) as image:
                q.require(image.size == (256, 256), 'crop_size')
                x = torch.from_numpy(np.array(image.convert('RGB'), copy=True)).permute(2, 0, 1).float()[None]/255
            features = network((x-mean)/std).mean((-2, -1))
            result.append(float(torch.sigmoid(head(features)).item()))
    return result


def run():
    baseline.OUT = OUT
    baseline.predict_torch = predict
    baseline.run()
