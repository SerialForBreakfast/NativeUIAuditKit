"""Check typed scientific conditions within the existing research queue."""
import research_queue as q

OUTCOMES = {'supported', 'contradicted', 'inconclusive'}


def validate_conditions(spec):
    conditions = spec.get('conditions', [])
    q.require(isinstance(conditions, list) and len(conditions) <= 10, 'condition_limit')
    dependencies = {d['job']: d for d in spec.get('dependencies', [])}
    seen = set()
    for item in conditions:
        q.require(isinstance(item, dict) and set(item) == {'job', 'output', 'outcome'}, 'condition_fields')
        q.require(item['job'] in dependencies, 'condition_dependency_missing')
        q.require(item['output'] in dependencies[item['job']]['outputs'], 'condition_output_missing')
        q.require(item['outcome'] in OUTCOMES - {'inconclusive'}, 'condition_outcome')
        key = (item['job'], item['output'])
        q.require(key not in seen, 'condition_duplicate')
        seen.add(key)


def check_conditions(spec, resolved, root):
    validate_conditions(spec)
    by_job = {d['job']: d for d in resolved}
    for item in spec.get('conditions', []):
        dep = next(d for d in spec['dependencies'] if d['job'] == item['job'])
        ref = by_job[item['job']]['outputs'][dep['outputs'].index(item['output'])]
        path = q.local_path(root, ref['path'])
        q.require(path.stat().st_size <= 1_000_000, 'condition_report_limit')
        q.require(q.digest(path) == ref['sha256'], 'condition_report_changed')
        doc = q.load(path)
        q.require(doc.get('version') == 'research-condition-v1', 'condition_report_version')
        q.require(doc.get('outcome') in OUTCOMES, 'condition_report_outcome')
        q.require(isinstance(doc.get('reason'), str) and doc['reason'].strip(), 'condition_report_reason')
        q.require(isinstance(doc.get('evidence'), list) and doc['evidence'], 'condition_report_evidence')
        for pin in doc['evidence']:
            evidence = q.local_path(root, q.check_pin(pin)['path'])
            q.require(q.digest(evidence) == pin['sha256'], 'condition_evidence_changed')
        q.require(doc['outcome'] == item['outcome'],
                  'condition_not_met:' + item['job'] + ':' + doc['outcome'] + ':' + doc['reason'])


def validate_graph(graph, queue=q.QUEUE):
    q.require(graph.get('version') == 'research-graph-v1', 'graph_version')
    q.require(isinstance(graph.get('id'), str) and q.ID.fullmatch(graph['id']), 'graph_id')
    nodes = graph.get('nodes')
    q.require(isinstance(nodes, list) and 1 <= len(nodes) <= 100, 'graph_nodes')
    by_id = {}
    for node in nodes:
        q.require(set(node) == {'job', 'specSHA256', 'question', 'kind'}, 'graph_node_fields')
        q.require(node['job'] not in by_id, 'graph_duplicate')
        q.require(node['kind'] in {'producer', 'qualification', 'experiment', 'decision'}, 'graph_kind')
        q.require(isinstance(node['question'], str) and node['question'].strip(), 'graph_question')
        path = q.local_path(queue, 'jobs/' + node['job'] + '/spec.json')
        spec = q.load(path)
        q.require(q.text_digest(spec) == node['specSHA256'], 'graph_spec_changed')
        by_id[node['job']] = spec
    visiting, visited = set(), set()
    def visit(ident):
        q.require(ident not in visiting, 'graph_cycle')
        if ident in visited:
            return
        visiting.add(ident)
        for dep in by_id[ident].get('dependencies', []):
            q.require(dep['job'] in by_id, 'graph_dependency_outside_revision')
            q.require(q.text_digest(by_id[dep['job']]) == dep['specSHA256'], 'graph_edge_changed')
            visit(dep['job'])
        visiting.remove(ident)
        visited.add(ident)
    for ident in by_id:
        visit(ident)
    return dict(jobs=len(nodes), maximumSeconds=sum(s['limits']['timeoutSeconds'] for s in by_id.values()),
                maximumBytes=sum(s['limits']['maxOutputBytes'] for s in by_id.values()))
