#!/bin/zsh
# QA666: 1 bounded pair for 1 model. Usage: run_smoke.sh RUN_NAME MODEL [SCHEMA]
set -u
U=9026ECA9-77DB-4AE6-8FE6-BB239E9571FA
W=${NUIAK_TTR_ROOT:-$HOME/Developer/TVTestRig}/.local-work/qa666-qa-improvements
A=$W/.local-work/qa666-build/DerivedData/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv
R=$W/.local-work/qa666-runs
NU="${0:A:h:h:h}"
[ -e "$R/$1" ] && { echo "exists $R/$1"; exit 2; }
xcrun simctl terminate $U com.showblender.TVTestRigFixture 2>/dev/null; sleep 2
python3 -c "
import json,datetime;d=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(dict(model='$2',repetitions=1,maxCalls=8,maxTokens=20000,maxPresses=24,outputSchema='${3:-v2}',deadline=d,**({'think':False} if '${4:-}'=='nothink' else {}),approvedBy='Joe in chat 2026-11-19: Run both models'),open('$R/budget-$1.json','w'))"
cd $W && QA666_TTR_ROOT=$W TTR_FRAMEWORK_DIGEST=$(cat $NU/.build/qa666-restore/new-fixture-sha256.txt) timeout 1000 ruby $NU/scripts/qa666/run_local_pair.rb "$A" $U $R/$1 $R/budget-$1.json > $R/$1.log 2>&1
echo "exit $?"
grep -v "^com.showblender" $R/$1.log | tail -3 | cut -c1-200
python3 -c "
import json,glob;d=json.load(open('$R/$1/provider-ledger.json'));print({k:d[k] for k in ('calls','tokens','presses','usageUnknown')})
for f in sorted(glob.glob('$R/$1/rep-1-*/call-1/response.json')): r=json.load(open(f)); print(f.split('/')[-3], r['promptTokens'], r['outputTokens'], r['latencySeconds'], r['reply'].replace(chr(10),'').replace(' ','')[:120])"
