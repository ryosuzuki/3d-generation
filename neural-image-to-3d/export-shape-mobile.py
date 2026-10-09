"""Decimate inferred Hunyuan shapes, preserving originals and coordinates."""
from pathlib import Path
import argparse,hashlib,json,time
import trimesh,numpy as np
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('files',nargs='+');p.add_argument('--faces',type=int,default=18000);a=p.parse_args();root=Path(a.root);items=[]
for file in a.files:
 src=root/file;mesh=trimesh.load(src,force='mesh',process=False);t=time.perf_counter();small=mesh.simplify_quadric_decimation(face_count=a.faces) if len(mesh.faces)>a.faces else mesh.copy();assert np.isfinite(small.vertices).all();dst=root/(src.stem+'-mobile.glb');small.export(dst)
 items.append(dict(source=src.name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),mobile=dst.name,mobile_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),original_faces=len(mesh.faces),mobile_faces=len(small.faces),vertices=len(small.vertices),seconds=time.perf_counter()-t,method='Actual learned shape quadric edge-collapse derivative. No geometry authored; original full shape retained. Original Y-up coordinates, no normalization baked.',texture=False,bounds=small.bounds.tolist()))
rp=root/'shape-mobile-derivative-receipt.json';old=json.loads(rp.read_text()) if rp.exists() else {'items':[]};names={x['source'] for x in items};old['items']=[x for x in old['items'] if x['source'] not in names]+items;rp.write_text(json.dumps(old,indent=2));print(json.dumps(items,indent=2))
