"""Package a verified consumer-only update, reusing unchanged DTM030 model bytes."""
import shutil
from pathlib import Path
import benchmark_shadow120 as b
from package_transition_shadow106 import main as package

h=b.h


def main():
    comparison=h.read(b.BASE/'comparison.json')
    h.require(comparison['exactParity'] and comparison['preprocessingRatio']<.8 and comparison['totalRatio']<.9,
              'measured_benefit_required')
    root=h.fresh(b.BASE/'package');root.mkdir()
    for name in ('bundle','export'):
        shutil.copytree(b.SOURCE/name,root/name)
    # Reuse the same model, not an export or recompilation.
    h.require(b.v.tree(root/'bundle/FocusTransitionChange.mlmodelc')[0]==comparison['modelTreeSHA256'],'model_changed')
    (root/'parity-final').mkdir()
    shutil.copyfile(b.BASE/'optimized/parity.json',root/'parity-final/parity.json')
    inputs=root/'parity-inputs';inputs.mkdir()
    ref=h.read(b.SOURCE/'parity-inputs/reference.json')
    for row in ref['examples']:
        if row['id'].startswith('synthetic-'):
            for side in ('before','after'):
                origin=Path(row[side]['path']);h.require(origin.parent==b.SOURCE/'parity-inputs','synthetic_source')
                dest=inputs/origin.name;shutil.copyfile(origin,dest);row[side]['path']=str(dest)
    h.write(inputs/'reference.json',ref)
    package(base=root,model_id='focus-transition-experimental-dtm030-change-v1',expected_pairs=438,
            archive_name='nuiak-transition-shadow-dtm030-consumer-v2.zip')


if __name__=='__main__':main()
