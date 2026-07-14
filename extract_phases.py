import json
import sys

canvas_path = '/home/adhish/Productivity/AMSCUP/obsidianVault/Canvas.canvas'
with open(canvas_path, 'r') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
edges = data.get('edges', [])

# Helper: check if node inside group
def inside_group(node, group):
    nx = node.get('x', 0)
    ny = node.get('y', 0)
    gx = group.get('x', 0)
    gy = group.get('y', 0)
    gw = group.get('width', 0)
    gh = group.get('height', 0)
    return gx <= nx <= gx + gw and gy <= ny <= gy + gh

# Find groups by label
groups = {n['id']: n for n in nodes if n['type'] == 'group'}
label_to_gid = {}
for gid, g in groups.items():
    label = g.get('label', '').strip()
    if label:
        label_to_gid[label] = gid

# Target groups
target_labels = ['Phase 1', 'Phase 2', 'Phase 3', 'Data Flow']
target_gids = [label_to_gid[l] for l in target_labels if l in label_to_gid]

# Collect nodes belonging to any target group
selected_nodes = []
for n in nodes:
    if n['type'] == 'group':
        continue
    for gid in target_gids:
        if inside_group(n, groups[gid]):
            selected_nodes.append(n)
            break

# Build node id set
selected_ids = {n['id'] for n in selected_nodes}
# Select edges where both ends in selected_ids
selected_edges = [e for e in edges if e['fromNode'] in selected_ids and e['toNode'] in selected_ids]

print(json.dumps({
    'nodes': selected_nodes,
    'edges': selected_edges
}, indent=2))
