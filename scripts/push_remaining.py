
# push_remaining.py - run after:  = 'ghp_...'
import json, os, base64, urllib.request
from pathlib import Path

TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
assert TOKEN, 'Set GITHUB_TOKEN'
OWNER, REPO, BRANCH = 'zhanhuiinhk', 'world-electronic-components', 'main'
ROOT = Path(__file__).resolve().parents[1]  # repo root (C:\world-electronic-components)

def api(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        return json.load(r)

# get ref
ref = api('GET', f'https://api.github.com/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}')
commit_sha = ref['object']['sha']
commit = api('GET', f'https://api.github.com/repos/{OWNER}/{REPO}/git/commits/{commit_sha}')
base_tree = commit['tree']['sha']

paths = []
for base in ['scripts/collectors/map_to_wec.py','docs/assets/data-manifest.json','docs/assets/manufacturers.json','docs/assets/catalog.json']:
    paths.append(base)
for p in (ROOT/'data').rglob('*.json'):
    paths.append(p.relative_to(ROOT).as_posix())
for p in (ROOT/'manufacturers').rglob('*.json'):
    if p.name.startswith('_'): continue
    paths.append(p.relative_to(ROOT).as_posix())

# unique
seen=set(); paths=[x for x in paths if not (x in seen or seen.add(x))]

tree = []
for rel in paths:
    content = (ROOT/rel).read_text(encoding='utf-8')
    blob = api('POST', f'https://api.github.com/repos/{OWNER}/{REPO}/git/blobs',
               json.dumps({'content': content, 'encoding': 'utf-8'}).encode())
    tree.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    print('blob', rel)

new_tree = api('POST', f'https://api.github.com/repos/{OWNER}/{REPO}/git/trees',
    json.dumps({'base_tree': base_tree, 'tree': tree}).encode())
new_commit = api('POST', f'https://api.github.com/repos/{OWNER}/{REPO}/git/commits',
    json.dumps({
        'message': 'Sync local DigiKey collect: map_to_wec + expanded component data (180 parts)',
        'tree': new_tree['sha'],
        'parents': [commit_sha]
    }).encode())
api('PATCH', f'https://api.github.com/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}',
    json.dumps({'sha': new_commit['sha']}).encode())
print('DONE', new_commit['sha'])
