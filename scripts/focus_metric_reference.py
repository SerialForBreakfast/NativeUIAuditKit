"""Bounded reference ranker; consumes encoded candidates, never inference labels."""
import numpy as np

VERSION = 'focus-metric-reference-v1'
WIDTH = 770
MAX_REFERENCES = 8192
MAX_QUERIES = 80
BLOCK = 512


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_tensor(value, maximum):
    require(isinstance(value, np.ndarray) and value.dtype == np.float32 and
            value.ndim == 2 and value.shape[1] == WIDTH and
            0 < len(value) <= maximum, 'metric_shape_or_dtype')
    require(np.isfinite(value).all() and (value >= 0).all() and
            (value <= 1).all(), 'metric_nonfinite_or_range')


class ReferenceScorer:
    """Training labels belong only to the frozen bank, not query arguments.

    One query at a time and BLOCK references bound distance scratch space.
    Direct float64 subtraction preserves very small distances; dot-product
    distance identities can cancel them. Reference ties use stable IDs.
    """
    def __init__(self, tensor, members):
        validate_tensor(tensor, MAX_REFERENCES)
        require(len(members) == len(tensor), 'metric_membership')
        keys = []
        for member in members:
            require(member.get('role') == 'train' and
                    type(member.get('positive')) is bool and
                    all(isinstance(member.get(k), str) and member[k]
                        for k in ('frameID', 'candidateID', 'ancestry')),
                    'metric_reference_role_or_provenance')
            keys.append((member['frameID'], member['candidateID']))
        require(len(set(keys)) == len(keys), 'metric_duplicate_reference')
        order = sorted(range(len(keys)), key=keys.__getitem__)
        self.tensor = tensor[order].copy()
        self.tensor.flags.writeable = False
        self.members = tuple(dict(members[i]) for i in order)
        self.frames = np.array([v['frameID'] for v in self.members])
        self.positive = np.array([v['positive'] for v in self.members])
        require(self.positive.any() and (~self.positive).any(), 'metric_missing_class')

    def score(self, queries, frame_ids, *, exclude_same_frame=False):
        validate_tensor(queries, MAX_QUERIES)
        require(len(frame_ids) == len(queries) and
                all(isinstance(v, str) and v for v in frame_ids), 'metric_query_identity')
        output = []
        for query, frame in zip(queries, frame_ids):
            distances, neighbors = [], []
            for positive in (True, False):
                eligible = np.flatnonzero((self.positive == positive) &
                    (self.frames != frame if exclude_same_frame else True))
                require(len(eligible) > 0, 'metric_no_eligible_reference')
                best, neighbor = float('inf'), None
                for start in range(0, len(eligible), BLOCK):
                    indices = eligible[start:start + BLOCK]
                    delta = self.tensor[indices].astype(np.float64)
                    delta -= query
                    np.square(delta, out=delta)
                    values = np.mean(delta, axis=1)
                    index = int(np.argmin(values))
                    if values[index] < best:
                        best, neighbor = float(values[index]), int(indices[index])
                distances.append(float(np.sqrt(best)))
                neighbors.append(neighbor)
            output.append(dict(score=distances[1] - distances[0],
                positiveRMS=distances[0], negativeRMS=distances[1],
                positiveReference=neighbors[0], negativeReference=neighbors[1]))
        return output
