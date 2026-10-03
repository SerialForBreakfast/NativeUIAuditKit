"""Prepare v2 draft and qualify immutable inputs; never admits or trains."""
import time
import human_annotation_review as h
import train_fullscreen_focus as runner


def main():
    base=h.ROOT/'reports/work/FULLSCREEN-READTHROUGH-40'
    old=h.ROOT/'reports/work/CONTROL-ELIGIBILITY-39/fullscreen/run-draft.json'
    doc=h.read(old);doc.update(version='fullscreen-focus-run-v2',storage='read-through',
        evaluationPolicy='terminal-last-checkpoint')
    out=base/'run-draft-v2.json';h.write(out,doc)
    start=time.monotonic();_,checked=runner.validate(out,inputs_only=True)
    h.write(base/'qualified-inputs.json',checked)
    try:runner.validate(out)
    except ValueError as error:
        h.require(str(error)=='membership_not_admitted','unexpected_admission_failure')
    else:raise ValueError('draft_execution_accepted')
    h.write(base/'input-result.json',dict(inputReady=True,executionReady=False,
        frames=len(checked['frames']),stagingBytes=checked['stagingBytes'],
        groups=checked['groups'],seconds=time.monotonic()-start,
        remaining='Exact full-screen admission is still a draft; this check grants no training authority.'))
    print('Qualified',len(checked['frames']),'frames; zero image copies.')


if __name__=='__main__':main()
