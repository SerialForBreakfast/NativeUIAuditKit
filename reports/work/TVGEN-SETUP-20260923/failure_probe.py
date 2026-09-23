"""One passive post-failure observation and diagnostic screenshot; no input/retry."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import direct_tvos_capture as d
HERE=Path(__file__).resolve().parent
target='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
binding=d.bind_target(target,'http://127.0.0.1:8080')
snapshot=d.Fixture(binding['endpoint']).snapshot()
d.write_json(HERE/'kitchen-passive.json',{'binding':binding,'snapshot':snapshot,'diagnosticOnly':True})
d.run(['xcrun','simctl','io',target,'screenshot','--type=png',str(HERE/'kitchen-diagnostic.png')],15)
scene=snapshot['scene']
print(json.dumps({'sceneSize':[scene['scene_width'],scene['scene_height']],
                  'recipe':scene['recipe'],'diagnostics':scene.get('observation_diagnostics')},indent=2))
