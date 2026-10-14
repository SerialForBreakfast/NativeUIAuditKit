"""Replay a pinned resident entry point through the existing queue contract.

Keep original outputs unchanged. Add typed evidence for the current queue checks.
The queue compares original outputs with explicit field exclusions in the specification.
"""
import importlib
import math

import research_queue as q

OUT = None


def prediction_rows(document):
    if 'sets' in document:
        collections = document['sets']
    elif 'variants' in document:
        collections = document['variants']
    else:
        collections = {'main': document}
    result = []
    for name, collection in collections.items():
        rows, values = collection['rows'], collection['probabilities']
        q.require(len(rows) == len(values) and rows, 'replay_prediction_membership')
        for row, value in zip(rows, values):
            q.require(math.isfinite(value) and 0 <= value <= 1, 'replay_probability')
            q.require(row['changed'] in (0, 1), 'replay_label')
            result.append(dict(id=name + ':' + row['id'], probability=value,
                               label=row['changed'], group=row['group']))
    q.require(len({row['id'] for row in result}) == len(result), 'replay_duplicate_prediction')
    return result


def run():
    config = q.load(OUT / 'replay-config.json')
    module_name, function = config['step'].split('.')
    module = importlib.import_module(module_name)
    module.OUT = OUT
    getattr(module, function)()
    if config['jobKind'] == 'training':
        fit = q.load(OUT / 'fit.json')
        history = [dict(epoch=index + 1, trainLoss=row['loss'])
                   for index, row in enumerate(fit['history'])]
        q.save(OUT / 'epoch-evidence.json', history)
        q.save(OUT / 'training-evidence.json', dict(epochs=len(history)))
    elif config['jobKind'] == 'evaluation':
        q.save(OUT / 'prediction-evidence.json', dict(rows=prediction_rows(q.load(OUT / config['result']))))
    else:
        dependencies = q.load(OUT / 'dependencies.json')
        q.save(OUT / 'sources.json', [item for dep in dependencies for item in dep['outputs']])
