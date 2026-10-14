"""Test a fixed longer training budget with the existing matched trainer."""
import position355 as p
OUT = None


def training():
    p.OUT = OUT
    original_fit = p.a.b.trainer.fit
    original_emit = p.m.emit

    def fit(net, x, y, settings, progress, **kwargs):
        settings['epochs'] = 30
        return original_fit(net, x, y, settings, progress, **kwargs)

    def emit(step, done, total):
        if step.startswith('Train '):
            total = 30
        if step == 'Training complete; comparisons required':
            done = total = 30
        return original_emit(step, done, total)

    p.a.b.trainer.fit = fit
    p.m.emit = emit
    try:
        p.training()
    finally:
        p.a.b.trainer.fit = original_fit
        p.m.emit = original_emit


def collect():
    p.OUT = OUT
    p.collect()
    doc = p.q.load(OUT/'summary.json')
    decisions = {}
    for arm in ('control', 'position'):
        rows = [r for r in doc['summaryRows'] if r['job'].startswith('focus358-'+arm+'-')]
        lost = sum(r['counts'].get('lost', 0) for r in rows)
        gained = sum(r['counts'].get('gained', 0) for r in rows if r['job'].endswith('-movement'))
        decisions[arm] = dict(comparisons=len(rows), complete=len(rows)==24,
            lostPrevious=lost, gainedNativeMovement=gained,
            passesDevelopmentRule=len(rows)==24 and lost==0 and gained>0)
    doc['decisions'] = decisions
    p.q.save(OUT/'summary.json', doc, replace=True)
