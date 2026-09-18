import json

with open('reports/tvos_settings_hierarchy.json') as f:
    h = json.load(f)

lines = []
lines.append("```mermaid")
lines.append("flowchart LR")
lines.append('    Root["⚙️ tvOS Settings (tvOS 26.6 / 18.x)"]')

for c in h['children']:
    c_id = c['id']
    c_name = c['name'].replace('&', 'and').replace('"', '')
    item_preview = ", ".join(c['items'][:3])
    lines.append(f'    Root --> {c_id}["{c_name}"]')
    for s in c.get('subsections', []):
        s_id = s['id'].replace('>', '').replace(' ', '_').replace("'", "").replace('&', 'and')
        s_name = s['name'].replace('&', 'and').replace('"', '')
        lines.append(f'    {c_id} --> {s_id}["{s_name}"]')

lines.append("```")
print("\n".join(lines))
