"""Prepare verified direct-transition inputs once; no training or capture."""
import argparse
import time
import inspect
import numpy as np
import focus_direct_transition as d
import human_annotation_review as h
from focus_translation_training import banks,TRAIN_CONDITIONS
from focus_pair_translation import DEFAULT_POLICY,POLICIES

VERSION='prepared-transition-inputs-v2'
SCOPED_VERSION='prepared-transition-inputs-v3'
ARRAY_LIMIT=256*1024*1024


def input_pins():
    """Model architecture/optimizer changes cannot invalidate identical input tensors."""
    functions=('geometry','pixels','encode','target_box','admitted','collect','record','baseline_change')
    return dict(functions={name:h.digest(inspect.getsource(getattr(d,name))) for name in functions},
        decodedHash=h.digest(inspect.getsource(d.old.decoded_hash)),
        dimensions={k:d.CONFIG[k] for k in ('width','height')},
        code=[h.ref(h.ROOT/'scripts'/name) for name in (
            'prepare_transition_inputs.py','focus_translation_training.py','focus_pair_translation.py',
            'focus_corrected_transition_audit.py','focus_structural_transition_audit.py',
            'focus_recorded_semantics.py','focus_recorded_readiness.py','human_annotation_review.py',
            'artifact_storage.py','focus_dataset_contract.py','photos_focus_pilot.py',
            'synth05_intake.py','fixture_owned_pairs.py','inventory_transition_sources.py')],
        dependencies={name:d.dependency_version(name) for name in ('numpy','pillow')},python=d.sys.version)


def references(corpus):
    refs=list(corpus['sources'].values())
    for row in corpus['records']:refs.extend(row['images']+row['evidence'])
    result={}
    for ref in refs:
        h.require(ref['path'] not in result or result[ref['path']]==ref,'conflicting_source_hash')
        result[ref['path']]=ref
    return [result[k] for k in sorted(result)]


def manifest(path):
    doc=h.read(h.local(path))
    h.require(doc.get('version') in (SCOPED_VERSION,VERSION,'prepared-transition-inputs-v1') and
        doc.get('seal')==h.digest({k:v for k,v in doc.items() if k!='seal'}),'prepared_manifest_changed')
    h.require(doc['pins']==(input_pins() if doc['version']==SCOPED_VERSION else d.pins()),'prepared_code_or_runtime_changed')
    h.require(doc.get('policy',DEFAULT_POLICY) in POLICIES and
        (doc['version'] in (VERSION,SCOPED_VERSION) or doc.get('policy',DEFAULT_POLICY)==DEFAULT_POLICY),'prepared_policy')
    h.require(doc['version']=='prepared-transition-inputs-v1' or 'policy' in doc,'missing_prepared_policy')
    corpus=h.read(h.checked(h.ROOT,doc['corpus']))
    h.require(corpus['corpusSHA256']==h.digest({k:v for k,v in corpus.items() if k!='corpusSHA256'}),
        'prepared_corpus_changed')
    rows=d.admitted(corpus,h.read(h.checked(h.ROOT,doc['admission'])))
    h.require(doc['sourceReferences']==references(corpus),'prepared_source_accounting')
    for ref in doc['sourceReferences']:h.checked(h.ROOT,ref)
    train=[r for r in rows if r['split']=='train']
    h.require(0<len(train)<=256 and doc['trainingRowsSHA256']==h.digest(train),'prepared_membership_changed')
    return doc,corpus,rows


def load(path,rows,policy=DEFAULT_POLICY):
    doc,_,all_rows=manifest(path)
    h.require(doc.get('policy',DEFAULT_POLICY)==policy,'prepared_policy_mismatch')
    h.require(rows==[r for r in all_rows if r['split']=='train'],'prepared_training_rows_changed')
    arrays=[]
    for name in ('x','y'):
        array=np.load(h.checked(h.ROOT,doc[name],ARRAY_LIMIT),allow_pickle=False,mmap_mode='r')
        h.require(isinstance(array,np.ndarray) and array.dtype==np.float32,'invalid_prepared_array')
        arrays.append(array)
    x,y=arrays;n=len(doc['entries'])
    h.require(0<n<=len(rows)*5 and x.shape==(n,6,64,96) and y.shape==(n,9) and
        np.isfinite(x).all() and np.isfinite(y).all() and
        ((x>=0)&(x<=1)).all() and ((y>=0)&(y<=1)).all(),'prepared_array_shape_or_range')
    options=doc['options'];h.require(len(options)==len(rows),'prepared_options')
    used=[]
    for row,indices in zip(rows,options):
        h.require(indices and all(type(i)is int and 0<=i<n for i in indices),'prepared_indices')
        entries=[doc['entries'][i] for i in indices]
        h.require(entries[0]==dict(id=row['id'],condition='baseline') and
            all(e['id']==row['id'] and e['condition'] in TRAIN_CONDITIONS for e in entries) and
            len({e['condition'] for e in entries})==len(entries),'prepared_entry_binding')
        h.require(all(y[i,8]==float(row['changed']) for i in indices),'prepared_label_changed')
        used.extend(indices)
    h.require(sorted(used)==list(range(n)),'prepared_bank_accounting')
    return x.copy(),y.copy(),options,doc['entries'],doc['rejected']


def prepare(corpus_path,admission_path,output,scoped=False):
    return prepare_many(corpus_path,admission_path,{DEFAULT_POLICY:output},scoped=scoped)


def prepare_many(corpus_path,admission_path,outputs,scoped=False):
    h.require(outputs and set(outputs)<=set(POLICIES),'prepared_policies')
    start=time.monotonic();destinations={policy:h.fresh(path) for policy,path in outputs.items()}
    h.require(len(set(destinations.values()))==len(destinations),'duplicate_prepared_destination')
    saved=h.read(h.local(corpus_path));corpus=d.collect(saved['sources'])
    h.require(saved==corpus,'cold_corpus_changed')
    rows=d.admitted(corpus,h.read(h.local(admission_path)))
    train=[r for r in rows if r['split']=='train']
    intake=time.monotonic()-start
    prepared=banks(train,list(outputs));build=time.monotonic()-start-intake
    results={}
    for policy,out in destinations.items():
        results[policy]=publish_bank(corpus_path,admission_path,out,corpus,train,prepared[policy],policy,scoped)
    return dict(intakeSeconds=intake,bankBuildSeconds=build,totalSeconds=time.monotonic()-start,results=results)


def publish_bank(corpus_path,admission_path,out,corpus,train,arrays,policy,scoped=False):
    start=time.monotonic();x,y,options,entries,rejected=arrays
    h.require(x.nbytes+y.nbytes<=ARRAY_LIMIT,'prepared_size_limit')
    out.mkdir(parents=True)
    np.save(out/'x.npy',x,allow_pickle=False);np.save(out/'y.npy',y,allow_pickle=False)
    doc=dict(version=SCOPED_VERSION if scoped else VERSION,policy=policy,pins=input_pins() if scoped else d.pins(),corpus=h.ref(h.local(corpus_path)),
        admission=h.ref(h.local(admission_path)),sourceReferences=references(corpus),
        trainingRowsSHA256=h.digest(train),options=options,entries=entries,rejected=rejected,
        x=h.ref(out/'x.npy'),y=h.ref(out/'y.npy'),executionAuthorized=False)
    h.write(out/'manifest.json',doc,sealed=True);cold=time.monotonic()-start
    start=time.monotonic();warm=load(out/'manifest.json',train,policy);elapsed=time.monotonic()-start
    h.require(np.array_equal(x,warm[0]) and np.array_equal(y,warm[1]) and
        (options,entries,rejected)==warm[2:],'prepared_parity_failed')
    h.write(out/'verification.json',dict(version='prepared-transition-parity-v1',
        manifest=h.ref(out/'manifest.json'),publicationSeconds=cold,warmSeconds=elapsed,
        tensorBytes=x.nbytes+y.nbytes,trainPairs=len(train),bankEntries=len(entries),
        exactTensorParity=True,trainingLaunched=False),sealed=True)
    result=dict(policy=policy,publicationSeconds=cold,warmSeconds=elapsed,trainPairs=len(train),bankEntries=len(entries),rejected=len(rejected))
    print(result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','admission','output'):p.add_argument('--'+name,required=True)
    p.add_argument('--scoped-input-pins',action='store_true')
    a=p.parse_args();prepare(a.corpus,a.admission,a.output,a.scoped_input_pins)
