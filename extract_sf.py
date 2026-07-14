import json
canvas_path = '/home/adhish/Productivity/AMSCUP/obsidianVault/Canvas.canvas'
with open(canvas_path, 'r') as f:
    data = json.load(f)
nodes = data.get('nodes', [])
edges = data.get('edges', [])
def inside_group(node, group):
    nx = node.get('x', 0); ny = node.get('y', 0)
    gx = group.get('x', 0); gy = group.get('y', 0)
    gw = group.get('width', 0); gh = group.get('height', 0)
    return gx <= nx <= gx + gw and gy <= ny <= gy + gh
groups = {n['id']: n for n in nodes if n['type'] == 'group'}
sf_gid = None
for gid, g in groups.items():
    if g.get('label') == 'Sensor Fusion':
        sf_gid = gid
        break
if sf_gid is None:
    print('Sensor Fusion group not found')
    exit(1)
sf_group = groups[sf_gid]
sf_nodes = [n for n in nodes if n['type'] != 'group' and inside_group(n, sf_group)]
sf_node_ids = {n['id'] for n in sf_nodes}
sf_edges = [e for e in edges if e['fromNode'] in sf_node_ids and e['toNode'] in sf_node_ids]
print(json.dumps({
    'nodes': sf_nodes,
    'edges': sf_edges,
    'group': sf_group
}, indent=2))
