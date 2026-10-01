"""Native-body changed-data protocol and separately approved feature encoding.

Preflight has no torch imports. Training reuses caches; it never encodes implicitly.
"""
import argparse
import hashlib
import importlib.metadata
import re
import time

import human_annotation_review as h
import focus_native_body_assembly as assembly
import focus_review_continuation as reviewed

VERSION = 'focus-native-body-full-fit-v1'
INPUT_VERSION = 'focus-native-body-experiment-input-v1'
ARM = 'native-body-full-fit'
FEATURES = 'focus-native-body-features-v1'
ENCODING_APPROVAL = 'focus-native-body-encoding-approval-v1'
RUN_APPROVAL = 'focus-native-body-run-approval-v1'


def read_ref(ref):
    return h.read(h.checked(h.ROOT, ref), limit=assembly.ASSEMBLY_MAX_BYTES)


def verified_assembly(ref):
    doc = read_ref(ref)
    h.require(doc.get('version') == assembly.VERSION and
              doc.get('protocolSHA256') == h.digest({k:v for k,v in doc.items() if k != 'protocolSHA256'}),
              'changed_native_assembly')
    h.require(doc == assembly.assemble(doc['inputs']), 'changed_native_assembly_inputs')
    return doc


def budget(value, count):
    h.require(set(value) == {'maxSeconds','maxControls','batchSize','maxOutputBytes'}, 'encoding_budget_fields')
    h.require(all(type(v) is int for v in value.values()), 'encoding_budget_integers')
    h.require(0 < value['maxSeconds'] <= 300 and 0 < value['maxControls'] <= 2048
              and count <= value['maxControls'] and value['batchSize'] == 32
              and max(65536, count * 577 * 4) <= value['maxOutputBytes'] <= 32*1024*1024,
              'encoding_budget_limits')


def receipt_check(receipt, doc):
    h.require(receipt.get('version') == FEATURES and receipt.get('members') == doc['encodingPlan']['members']
              and receipt.get('representation') == doc['representation']
              and receipt.get('featureStateSHA256') == doc['encodingPlan']['featureStateSHA256']
              and receipt.get('backboneUnchanged') is True
              and receipt.get('assembly') == doc['inputs']['assembly']
              and receipt.get('budget') == doc['inputs']['encodingBudget'], 'changed_native_feature_receipt')
    h.require(re.fullmatch('[0-9a-f]{64}', receipt.get('featureSHA256','')) is not None, 'missing_feature_digest')
    # An encoding receipt must point back to the pre-cache protocol and approval.
    encoded = read_ref(receipt['encodingProtocol'])
    # The caller already revalidated the assembly. Reconstruct the pre-cache
    # view from that result instead of decoding the whole corpus a second time.
    before = {k:v for k,v in doc.items() if k != 'protocolSHA256'}
    before.update(inputs={**doc['inputs'], 'newFeatures':None},
                  blockers=doc['blockers']+['missing_native_feature_cache'])
    # Encoded bytes bind the encoder/members/preprocessing, not the subsequent
    # trainer source revision. Retain and verify the original runtime receipt.
    before['runtime'] = encoded['runtime']
    before['protocolSHA256'] = h.digest(before)
    h.require(encoded == before, 'changed_encoding_protocol')
    approved = read_ref(receipt['approval'])
    check_encoding_approval(encoded, approved, receipt['output'])


def make_protocol(spec):
    h.require(spec.get('version') == INPUT_VERSION and
              set(spec) <= {'version','assembly','encodingBudget','newFeatures','reweightPolicy'}, 'native_experiment_inputs')
    policy = spec.get('reweightPolicy')
    h.require(policy in (None,assembly.CONTINUITY_POLICY), 'unsupported_weight_policy')
    # Validate the unchanged encoding contract first; weighting affects the head
    # objective, never the cached encoder output or its historical approval.
    if policy is not None:
        original = make_protocol({k:v for k,v in spec.items() if k!='reweightPolicy'})
        base = read_ref(original['baseline'])
        additions = [r for r in original['samples'] if r['split']=='train'][original['baselineTraining']:]
        original['inputs']['reweightPolicy'] = policy
        original['fullFit'] = {**original['fullFit'], 'weights':assembly.continuous_weights(base,additions)}
        original.pop('protocolSHA256')
        original['protocolSHA256'] = h.digest(original)
        return original
    native = verified_assembly(spec['assembly'])
    base = read_ref(native['baseline'])
    h.require(base['version'] == reviewed.VERSION and base['protocolSHA256'] == assembly.BASE_SEAL,
              'wrong_native_baseline')
    budget(spec['encodingBudget'], native['counts']['added'])
    plan = native['encodingPlan']
    train = [r for r in native['samples'] if r['split'] == 'train']
    val = [r for r in native['samples'] if r['split'] == 'validation']
    n = native['counts']['baselineTraining']
    members = [dict(id=r['id'], label=r['label'], crop=r['crop']) for r in train[n:]]
    h.require(members == plan['members'] and
              [r['id'] for r in train[:n]] == plan['reuseTrainingIDs'] and
              [r['id'] for r in val] == plan['reuseEvaluationIDs'] and len(train)+len(val) == len(native['samples']),
              'native_execution_membership')
    blockers = [b for b in native['blockers'] if b not in
                ('encoding_budget_and_approval_required','changed_data_experiment_contract_required')]
    runtime = reviewed.full.s.rep.retention.runtime_identity()
    runtime['packages']['torchvision'] = importlib.metadata.version('torchvision')
    runtime['code'] += [h.ref(h.ROOT/'scripts'/name) for name in
                       ('focus_native_body_experiment.py','focus_native_body_assembly.py',
                        'focus_review_continuation.py','focus_pretrained_experiment.py','focus_full_fit_experiment.py',
                        'focus_paired_experiment.py','focus_representative_experiment.py',
                        'focus_representative_validation.py','human_focus_evaluation.py','human_focus_roles.py')]
    doc = dict(version=VERSION, inputs={**spec, 'newFeatures':spec.get('newFeatures')},
               samples=native['samples'], encodingPlan=plan, baseline=native['baseline'],
               baseCachedInputs=base['baseCachedInputs'], reviewedExtension=base['inputs']['newFeatures'],
               baselineTraining=n, warmCheckpoint=None, runtime=runtime,
               counts={**native['counts'], 'development':base['counts']['development'], 'retention':base['counts']['retention']},
               **{k:native[k] for k in ('configuration','selection','representation','fullFit','evaluationMembershipSHA256')},
               unmetQualificationBlockers=base['unmetQualificationBlockers'], releaseEligible=False, blockers=blockers)
    if spec.get('newFeatures'):
        refs = spec['newFeatures']
        h.require(set(refs) == {'cache','receipt'}, 'native_feature_refs')
        path = h.checked(h.ROOT, refs['cache'])
        h.require(path.stat().st_size <= spec['encodingBudget']['maxOutputBytes'], 'feature_cache_size_limit')
        receipt_check(read_ref(refs['receipt']), doc)
    else:
        blockers.append('missing_native_feature_cache')
    doc['blockers'] = blockers
    doc['protocolSHA256'] = h.digest(doc)
    return doc


def load_document(path):
    doc = h.read(h.local(path), limit=assembly.ASSEMBLY_MAX_BYTES)
    h.require(doc.get('version') == VERSION and doc.get('protocolSHA256') ==
              h.digest({k:v for k,v in doc.items() if k != 'protocolSHA256'}), 'changed_native_protocol')
    h.require(doc == make_protocol(doc['inputs']), 'changed_native_protocol_inputs')
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    doc = load_document(path)
    h.require(arm == ARM and isinstance(run_name,str) and
              re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name), 'native_experiment_arm_or_name')
    out = h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers = list(doc['blockers']); approval_ref = None
    if approval_path:
        approval_ref = h.ref(h.local(approval_path)); approval = read_ref(approval_ref)
        h.require(approval.get('version') == RUN_APPROVAL and approval.get('approved') is True
                  and approval.get('protocolSHA256') == doc['protocolSHA256'] and approval.get('arm') == ARM
                  and approval.get('runName') == run_name and approval.get('scope') == 'one-run-no-export-no-promotion',
                  'native_run_approval_binding')
        h.checked(h.ROOT, approval['authorizationReference'])
    else:
        blockers.append('missing_run_approval')
    rows = [dict(r,path=h.checked(h.ROOT,r['crop'])) for r in doc['samples']]
    return dict(formatVersion='focus-representative-preflight-v1', protocolVersion=VERSION,
                configurationValid=True, executionAuthorized=False, launchEligible=not blockers,
                releaseEligible=False, blockers=blockers, protocolFile=h.ref(h.local(path)), approval=approval_ref,
                arm=arm, nativeExtension=doc['inputs']['newFeatures'],
                **{k:doc[k] for k in ('configuration','selection','representation','warmCheckpoint','runtime',
                                      'counts','fullFit','protocolSHA256','unmetQualificationBlockers',
                                      'baseCachedInputs','reviewedExtension','baselineTraining')}), rows


def check_encoding_approval(doc, approval, output):
    h.require(doc['counts']['added'] > 0 and doc['blockers'] == ['missing_native_feature_cache'],
              'native_encoding_data_not_ready')
    target = str(h.local(output).relative_to(h.ROOT))
    h.require(approval.get('version') == ENCODING_APPROVAL and approval.get('approved') is True
              and approval.get('protocolSHA256') == doc['protocolSHA256']
              and approval.get('scope') == 'encode-admitted-native-only-no-training'
              and approval.get('output') == target and approval.get('budget') == doc['inputs']['encodingBudget'],
              'native_encoding_approval_binding')
    h.checked(h.ROOT, approval['authorizationReference'])


def validate_tensors(cache, receipt, members):
    import torch
    h.require(set(cache) == {'receipt','train'} and cache['receipt'] == receipt, 'native_cache_receipt')
    x,y = cache['train']
    h.require(x.dtype == torch.float32 and y.dtype == torch.float32 and x.shape == (len(members),576)
              and y.shape == (len(members),1) and bool(torch.isfinite(x).all())
              and torch.equal(y,torch.tensor([[r['label']] for r in members],dtype=torch.float32)),
              'native_cache_tensors')
    h.require(hashlib.sha256(x.contiguous().numpy().tobytes()).hexdigest() == receipt['featureSHA256'],
              'native_cache_feature_digest')
    return x,y


def prepare_features(report, train, validation, device, output):
    """Reuse the baseline's two-cache join, then append only the native extension."""
    import torch
    n = report['baselineTraining']
    head, baseline, val = reviewed.prepare_features(report,train[:n],validation,device,output)
    refs = report['nativeExtension']; receipt = read_ref(refs['receipt'])
    members = [dict(id=r['id'],label=r['label'],crop=r['crop']) for r in train[n:]]
    h.require(receipt['members'] == members and receipt['representation'] == report['representation']
              and receipt['featureStateSHA256'] == read_ref(report['baseCachedInputs']['receipt'])['featureStateSHA256'],
              'changed_native_cache_membership')
    cache = torch.load(h.checked(h.ROOT,refs['cache']),map_location='cpu',weights_only=True)
    x,y = validate_tensors(cache,receipt,members)
    joined = torch.utils.data.TensorDataset(torch.cat([baseline.tensors[0],x]),torch.cat([baseline.tensors[1],y]))
    h.write(output/'native-feature-receipt.json',dict(encoderLoaded=False,baselineTraining=n,
            added=len(members),training=len(train),evaluation=len(validation),nativeFeatures=refs))
    return head,joined,val


def encode_new(protocol, approval, output):
    doc = load_document(protocol); approval_ref = h.ref(h.local(approval))
    check_encoding_approval(doc,read_ref(approval_ref),output)
    out = h.fresh(output)
    rep = doc['representation']; rows = doc['encodingPlan']['members']; limits = doc['inputs']['encodingBudget']
    from focus_pretrained_experiment import encode, WEIGHTS_SHA, state_digest
    h.require(rep['weights']['sha256'] == WEIGHTS_SHA, 'wrong_encoder_weights')
    weights = h.checked(h.ROOT,rep['weights'])
    # All eligibility, scope, output and byte checks precede heavyweight imports.
    started = time.monotonic()
    import torch
    import numpy as np
    from PIL import Image
    from torchvision.models import mobilenet_v3_small
    h.require(torch.backends.mps.is_available(), 'native_encoding_requires_mps')
    class Crops(torch.utils.data.Dataset):
        def __len__(self): return len(rows)
        def __getitem__(self,index):
            with Image.open(h.checked(h.ROOT,rows[index]['crop'])) as im:
                h.require(im.size == (256,256), 'native_encoding_crop_dimensions')
                x = torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1).float()/255
            return x,torch.tensor([rows[index]['label']],dtype=torch.float32)
    network = mobilenet_v3_small(weights=None)
    network.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True),strict=True)
    features = torch.nn.Sequential(network.features,network.avgpool).to('mps')
    h.require(state_digest(features) == doc['encodingPlan']['featureStateSHA256'], 'wrong_encoder_state')
    encoded,state = encode(features,Crops(),torch.device('mps'),started+limits['maxSeconds'])
    elapsed = time.monotonic()-started
    h.require(elapsed <= limits['maxSeconds'], 'native_encoding_time_cap')
    h.require(state == doc['encodingPlan']['featureStateSHA256'], 'encoder_changed')
    receipt = dict(version=FEATURES,members=rows,representation=rep,backboneUnchanged=True,
        featureStateSHA256=state,featureSHA256=hashlib.sha256(encoded.tensors[0].contiguous().numpy().tobytes()).hexdigest(),
        assembly=doc['inputs']['assembly'],encodingProtocol=h.ref(h.local(protocol)),approval=approval_ref,
        output=str(out.relative_to(h.ROOT)),budget=limits,elapsedSeconds=elapsed,device='mps',
        currentAllocatedBytes=torch.mps.current_allocated_memory(),driverAllocatedBytes=torch.mps.driver_allocated_memory())
    cache = dict(receipt=receipt,train=encoded.tensors)
    validate_tensors(cache,receipt,rows)
    # Serialize in memory, enforce the authorized output cap before file creation.
    import io
    buffer = io.BytesIO(); torch.save(cache,buffer)
    h.require(buffer.tell() <= limits['maxOutputBytes'], 'native_encoding_output_cap')
    h.require(time.monotonic()-started <= limits['maxSeconds'], 'native_encoding_time_cap')
    out.mkdir(parents=True)
    with (out/'features.pt').open('xb') as stream: stream.write(buffer.getbuffer())
    h.write(out/'receipt.json',receipt)
    h.write(out/'features-reference.json',dict(cache=h.ref(out/'features.pt'),receipt=h.ref(out/'receipt.json')))
    return out/'features-reference.json'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inputs'); mode.add_argument('--encode-protocol')
    p.add_argument('--encoding-approval'); p.add_argument('--output',required=True)
    args = p.parse_args()
    try:
        if args.encode_protocol:
            h.require(args.encoding_approval, 'encoding_approval_required')
            print(encode_new(args.encode_protocol,args.encoding_approval,args.output)); return 0
        h.require(not args.encoding_approval, 'unexpected_encoding_approval')
        out = h.fresh(args.output); doc = make_protocol(h.read(h.local(args.inputs)))
        out.mkdir(parents=True); h.write(out/'protocol.json',doc)
        print(dict(counts=doc['counts'],blockers=doc['blockers'])); return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Native experiment rejected: '+str(error)); return 2


if __name__ == '__main__': raise SystemExit(main())
