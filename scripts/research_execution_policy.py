"""Exact runtime exceptions approved by the maintainer. No scope expansion."""

# USB386 preserves the approved HCF375D recipe and its 2 h detector limit.
TRAINING_EXCEPTIONS = {
    '6dec71bd728b7e5c5fc2a8000dd5b20490a5731779139fd11feb6144fbb16d6c': 7200,
    # HCF388 resolves early stopping while retaining the approved 30-epoch study.
    'f7ae94240dc3193471a1e2d31e1ff3efe19f00f788c8a5368a674c528df94608': 7200,
}


def seconds(spec_hash, authority, diagnostic_seconds):
    if authority == 'export':
        return 1800
    if authority == 'training':
        return TRAINING_EXCEPTIONS.get(spec_hash, 1800)
    return diagnostic_seconds
