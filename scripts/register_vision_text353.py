"""Register 4 fixed OCR configurations and their comparison."""
import research_queue as q
from research_campaign340 import pin
from compare351 import validate_capture


def main():
    folder=q.ROOT/'Research/ResearchSpecs/VISION353'
    path=q.ROOT/'reports/work/DATASET351/capture/capture.json'
    validate_capture(q.load(path),path.parent)
    binary=pin(q.ROOT/'.build/vision353/probe-ocr')
    refs=[pin(p) for p in sorted(path.parent.iterdir()) if p.is_file()]
    refs += [binary,*[pin(q.ROOT/'scripts'/name) for name in ('vision_text353.py','vision_annotation_probe.swift','compare351.py')]]
    settings=[('accurate-correct',dict(ocrLevel='accurate',languageCorrection=True)),
        ('accurate-raw',dict(ocrLevel='accurate',languageCorrection=False)),
        ('fast-correct',dict(ocrLevel='fast',languageCorrection=True)),
        ('small-text',dict(ocrLevel='accurate',languageCorrection=True,minimumTextHeight=.005))]
    dependencies=[]
    for i,(name,setting) in enumerate(settings,5):
        ident=f'vision353-{i:02d}-{name}';cp=folder/(ident+'-config.json')
        q.save(cp,dict(settings=setting,inputs=refs,capture=pin(path),binary=binary))
        spec=dict(version=q.SPEC_VERSION,id=ident,task='VISION353',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='OCR settings alter text stability under native focus effects and content changes.',
            decisionRule='Report exact text agreement, empty observations, and latency. Do not claim OCR accuracy without reviewed labels.',
            inputs=refs,stage=[{'from':pin(cp),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['vision_text353.run'],outputAttributes=['vision_text353.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        sp=folder/(ident+'.json');q.save(sp,spec);print(ident,q.submit(sp))
        dependencies.append(dict(job=ident,specSHA256=q.text_digest(spec),outputs=['diagnostic.json']))
    spec=dict(version=q.SPEC_VERSION,id='vision353-09-text-comparison',task='VISION353',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Text anchors need stable observations before they can support navigation checks.',
        decisionRule='Identify empty output and inconsistent anchors; do not select production settings from unreviewed text.',
        inputs=[pin(q.ROOT/'scripts/vision_text353.py')],dependencies=dependencies,
        adapter=dict(type='python-callable',steps=['vision_text353.summarize'],outputAttributes=['vision_text353.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    sp=folder/(spec['id']+'.json');q.save(sp,spec);print(spec['id'],q.submit(sp))


if __name__=='__main__':main()
