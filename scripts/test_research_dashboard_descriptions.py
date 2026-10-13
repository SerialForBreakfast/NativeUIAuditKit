"""Check display descriptions without starting or changing the research runner."""
import copy
import json
import re
import shutil
import subprocess
import unittest

from generate_research_dashboard import render_html
from research_dashboard_descriptions import describe, describe_jobs


class DescriptionTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(job='focus359-lossless-6', task='FOCUS359', state='pending',
                   hypothesis='Registered hypothesis', decisionRule='Registered decision rule',
                   modelAcceptance='not-assessed', evidenceKind='cached-diagnostic')
        row.update(changes)
        return row

    def test_descriptions_do_not_mutate_snapshot(self):
        data = {'jobs': [self.row()]}
        original = copy.deepcopy(data)
        description = describe_jobs(data)['focus359-lossless-6']
        self.assertIn('exact decoded pixels', description['test'])
        self.assertIn('save enough space', description['answers'])
        render_html(data)
        self.assertEqual(data, original)

    def test_native_plans_have_specific_questions(self):
        row = self.row(job='focus359-plan-02-selected-tab', state='blocked')
        description = describe(row)
        self.assertIn('selected but unfocused', description['test'])
        self.assertIn('selection styling', description['answers'])
        self.assertEqual(description['source'], 'job')

    def test_hcf_generation_and_classifier_have_different_questions(self):
        generation = describe(self.row(job='hcf358-plan-generate-1000', task='HCF358'))
        classifier = describe(self.row(job='hcf358-plan-classifier-1000', task='HCF358'))
        self.assertIn('Generate', generation['test'])
        self.assertIn('Train', classifier['test'])
        self.assertIn('proposals', classifier['answers'])
        self.assertNotEqual(generation['answers'], classifier['answers'])

    def test_unknown_jobs_do_not_get_invented_explanations(self):
        description = describe(self.row(task='FUTURE999', job='future999'))
        self.assertEqual(description['source'], 'unreviewed')
        self.assertEqual(description['test'], 'Registered hypothesis')
        self.assertIn('not available', description['answers'])

    def test_html_escapes_description_text(self):
        row = self.row(task='FUTURE999', hypothesis='</script><script>alert(1)</script>')
        page = render_html({'jobs': [row]})
        self.assertNotIn('</script><script>alert', page)
        self.assertIn('What this tests:', page)
        self.assertIn('What the result tells us:', page)
        self.assertIn('Technical details and registered decision rule', page)

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable for the JavaScript rendering check.')
    def test_javascript_rows_active_inspector_search_and_refresh(self):
        row = self.row(state='running')
        page = render_html({'jobs': [row], 'current': row['job']})
        script = re.search(r'<script>(.*?)</script>', page, re.S)[1]
        harness = r'''
const vm=require('vm');
class Element {
 constructor(){this.children=[];this.textContent='';this.value='';this.className='';}
 append(e){this.children.push(e);}
 replaceChildren(){this.children=[];this.textContent='';}
 showModal(){this.open=true;}
 close(){this.open=false;}
}
const nodes={};
global.document={getElementById:id=>nodes[id]||(nodes[id]=new Element()),createElement:()=>new Element()};
function text(e){return e.textContent+e.children.map(text).join(' ');}
function check(condition){if(!condition)throw Error('Dashboard display assertion failed');}
vm.runInThisContext(SCRIPT);
check(text(nodes.rows).includes('What this tests:'));
check(text(nodes.rows).includes('save enough space'));
check(text(nodes['active-description']).includes('exact decoded pixels'));
check(text(nodes['active-answer']).includes('save enough space'));
vm.runInThisContext('show(data.jobs[0])');
check(text(nodes['detail-description']).includes('What the result tells us:'));
check(text(nodes.detail).includes('Registered decision rule'));
nodes.search.value='decoding cost';nodes.search.oninput();check(nodes.rows.children.length===1);
nodes.search.value='not a matching question';nodes.search.oninput();check(nodes.rows.children.length===0);
nodes.search.value='';
vm.runInThisContext('data.jobs[0].state="complete";data.current=null;render()');
check(nodes['active-answer'].textContent==='');
check(nodes.rows.children.length===0);
check(text(nodes['completed-rows']).includes('save enough space'));
check(nodes['completed-count'].textContent.includes('1 total'));
nodes.search.value='not a matching question';nodes.search.oninput();check(nodes['completed-rows'].children.length===0);
nodes.search.value='';nodes.search.oninput();
vm.runInThisContext('data.jobs.push({job:"new-job",state:"blocked",hypothesis:"A new test",decisionRule:"A new rule"});render()');
check(text(nodes.rows).includes('New experiment — description needs review'));
check(text(nodes.rows).includes('Blocked: this is a planned test'));
'''
        result = subprocess.run([shutil.which('node'), '-e',
                                 'const SCRIPT=' + json.dumps(script) + ';\n' + harness],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
