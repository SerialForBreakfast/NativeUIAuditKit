"""Return from a verified Settings child before the existing HCF route runs."""
import time
import research_queue as q
from qualify_hcf362 import Client as BaseClient, TTR, TARGET


def page(report):
    frame=report['frames'][0]
    titles={r['text'] for r in frame['features']['text']
            if r['confidence']>=0.5 and r['bounds']['x']<0.5}
    known=titles & {'Settings','Accessibility','Display','Focus Style'}
    q.require(len(known)==1, 'settings_page_uncertain')
    return next(iter(known))


class Client(BaseClient):
    def call(self,name,*args,**kwargs):
        if args[:2]==('route','hcf'):
            session=args[args.index('--session')+1]
            self.normalize(session)
        return super().call(name,*args,**kwargs)

    def observe_page(self,session):
        native=super().call('native-page','simulator','remote','observe',
            '--simulator-udid',TARGET,'--session',session)
        observation=native.get('observation',{})
        q.require(native['operationID']==session and native['simulatorID']==TARGET and
            observation.get('bundleID')=='com.apple.TVSettings' and observation.get('foreground'),
            'settings_not_foreground')
        receipt=super().call('page-snapshot','simulator','remote','snapshot',
            '--simulator-udid',TARGET,'--session',session)
        relative=f'SimulatorDiagnostics/{session.lower()}/remote-snapshot-{receipt["sequence"]}.png'
        q.require(receipt.get('screenshotReference')==relative,'snapshot_identity')
        image=TTR/'Diagnostics/Runtime'/relative
        output=TTR/'.local-work/nuiak-hcf362/hcf-map'/f'page-{session.lower()}-{receipt["sequence"]}.json'
        super().call('page-analysis','vision','preprocess-pair','--before',str(image),
                     '--after',str(image),'--output',str(output))
        report=q.load(output)
        value=page(report)
        q.save(self.output/f'page-{self.count:03d}.json',dict(page=value,report=report,receipt=receipt))
        return value

    def normalize(self,session):
        # Back changes navigation only. Selection remains inside TTR's HCF route.
        for _ in range(3):
            first=self.observe_page(session);time.sleep(.2)
            second=self.observe_page(session)
            q.require(first==second,'settings_page_changed')
            if second in ('Settings','Accessibility'):return
            q.require(second in ('Display','Focus Style'),'unexpected_settings_page')
            receipt=super().call('page-back','simulator','remote','press',
                '--simulator-udid',TARGET,'--session',session,'--button','back')
            q.require(receipt.get('state')=='delivered','back_not_delivered')
            time.sleep(.35)
            after=self.observe_page(session)
            q.require(after=={'Display':'Accessibility','Focus Style':'Display'}[second],
                      'settings_parent_unverified')
        raise ValueError('settings_navigation_limit')
