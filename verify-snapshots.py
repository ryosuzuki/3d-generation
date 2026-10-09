from pathlib import Path
import json,hashlib,ast
r=Path(__file__).parent;count=0
for source in json.loads((r/'provenance.json').read_text()):
 for f in source['files']:
  p=r/source['folder']/f['path']; b=p.read_bytes()
  assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],str(p)
  if p.suffix=='.py':ast.parse(b,filename=str(p))
  count+=1
print(f'PASS: {count} source files byte hashes and Python syntax; 4 methods')
