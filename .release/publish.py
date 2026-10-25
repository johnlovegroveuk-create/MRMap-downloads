"""Publish only the signed APK whose hash was supplied in the release manifest."""
import base64, gzip, hashlib, json, os
from pathlib import Path
import subprocess, tempfile, urllib.request

manifest = json.loads(Path('.release/release.json').read_text())
repository = os.environ['GITHUB_REPOSITORY']
assert repository.lower() == 'johnlovegroveuk-create/mrmap-downloads'
version = manifest['version']
assert version == '0.3.1'
tag = 'v' + version
existing = subprocess.run(['gh', 'release', 'view', tag, '--json', 'assets'], capture_output=True, text=True)
if existing.returncode == 0:
    assets = json.loads(existing.stdout)['assets']
    assert any(a['name'] == 'MRMap-Android-' + version + '.apk' and a.get('digest') == 'sha256:' + manifest['apk_sha256'] for a in assets), 'Existing release does not match the verified APK'
    print('The verified release is already published.')
    raise SystemExit(0)

chunks = []
for part in manifest['chunks']:
    request = urllib.request.Request('https://api.github.com/repos/' + repository + '/git/blobs/' + part['sha'],
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = base64.b64decode(json.load(response)['content'])
    assert len(data) == part['size']
    chunks.append(data)
packed = b''.join(chunks)
assert hashlib.sha256(packed).hexdigest() == manifest['packed_sha256']
apk = gzip.decompress(packed)
assert len(apk) == manifest['apk_size'] and hashlib.sha256(apk).hexdigest() == manifest['apk_sha256']
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / ('MRMap-Android-' + version + '.apk')
    path.write_bytes(apk)
    notes = Path(directory) / 'notes.md'
    notes.write_text('\n'.join('- ' + note for note in manifest['notes']) + '\n\nRequires an MRMap radio number and password supplied by your team administrator.\n')
    subprocess.run(['gh', 'release', 'create', tag, str(path), '--title', 'MRMap ' + version,
                    '--target', 'main', '--notes-file', str(notes)], check=True)
print('Published APK SHA-256: ' + manifest['apk_sha256'])
