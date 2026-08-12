import os
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

TOKEN = os.environ.get('GITHUB_TOKEN', '')
USER = 'mikhailedwin'

def gh(path):
    url = f'https://api.github.com{path}'
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def clean_op(msg):
    msg = msg.split('\n')[0].strip()
    msg = re.sub(r'[^a-zA-Z0-9 ._/-]', '', msg)
    msg = msg.upper().replace(' ', '_')[:28]
    return msg or 'SIGNAL_LOST'

try:
    user = gh(f'/users/{USER}')
    repos = user.get('public_repos', 0)
    followers = user.get('followers', 0)
except Exception:
    repos = 0
    followers = 0

last_op = 'SIGNAL_LOST'
try:
    # Fetch latest commit from the repo directly — catches bot-authored commits too
    commits = gh(f'/repos/{USER}/{USER}.github.io/commits?sha=claude/f00f&per_page=1')
    if commits:
        last_op = clean_op(commits[0].get('commit', {}).get('message', ''))
except Exception:
    pass

out = {
    'last_op': last_op,
    'repos': repos,
    'followers': followers,
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
}

with open('status.json', 'w') as f:
    json.dump(out, f)

print(f'[status] last_op={last_op} repos={repos} followers={followers}')
