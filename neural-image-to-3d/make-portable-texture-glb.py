"""Lossless decoded-WebP→PNG derivative; learned geometry/PBR semantics untouched."""
from pathlib import Path
import argparse,struct,json,hashlib,io,time,copy
import numpy as np,trimesh
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('files',nargs='+');a=p.parse_args();root=Path(a.root);rows=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for filename in a.files:
 src=root/filename;t=time.perf_counter();b=src.read_bytes();magic,version,total=struct.unpack_from('<4sII',b);assert magic==b'glTF' and version==2 and total==len(b);n,typ=struct.unpack_from('<II',b,12);assert typ==0x4e4f534a;d=json.loads(b[20:20+n]);original_json=copy.deepcopy(d);off=20+n;bl,bt=struct.unpack_from('<II',b,off);assert bt==0x004e4942;data=b[off+8:off+8+bl];assert len(d['buffers'])==1 and 'uri' not in d['buffers'][0];replacements={};checks=[]
 for i,im in enumerate(d.get('images',[])):
  if im.get('mimeType')!='image/webp':continue
  vi=im['bufferView'];view=d['bufferViews'][vi];old=data[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];image=Image.open(io.BytesIO(old));image.load();buf=io.BytesIO();image.save(buf,format='PNG');new=buf.getvalue();assert np.array_equal(np.asarray(image.convert('RGBA')),np.asarray(Image.open(io.BytesIO(new)).convert('RGBA')));assert vi not in replacements;replacements[vi]=new;im['mimeType']='image/png';checks.append(dict(image_index=i,width=image.width,height=image.height,decoded_RGBA_exact=True))
 assert replacements,'No WebP texture found';out=bytearray()
 for i,view in enumerate(d['bufferViews']):
  assert view['buffer']==0
  segment=data[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];segment=replacements.get(i,segment)
  out.extend(b'\0'*((-len(out))%4));view['byteOffset']=len(out);view['byteLength']=len(segment);out.extend(segment)
  if i not in replacements:assert bytes(out[view['byteOffset']:view['byteOffset']+view['byteLength']])==segment
 for tex in d.get('textures',[]):
  ex=tex.get('extensions',{})
  if 'EXT_texture_webp' in ex:tex['source']=ex.pop('EXT_texture_webp')['source']
  if not ex:tex.pop('extensions',None)
 for k in ['extensionsUsed','extensionsRequired']:
  if k in d:
   d[k]=[v for v in d[k] if v!='EXT_texture_webp']
   if not d[k]:d.pop(k)
 d['buffers'][0]['byteLength']=len(out);out.extend(b'\0'*((-len(out))%4));jb=json.dumps(d,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);payload=struct.pack('<4sII',b'glTF',2,12+8+len(jb)+8+len(out))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(out),0x004e4942)+out;dst=src.with_name(src.stem+'-portablepng.glb');dst.write_bytes(payload);written=dst.read_bytes();jn=struct.unpack_from('<I',written,12)[0];serialized_json=json.loads(written[20:20+jn]);serialized_bin=written[20+jn+8:];assert serialized_json.get('materials')==original_json.get('materials');assert serialized_json.get('accessors')==original_json.get('accessors');
 for vi,oldview in enumerate(original_json['bufferViews']):
  if vi in replacements:continue
  newview=serialized_json['bufferViews'][vi];oldsegment=data[oldview.get('byteOffset',0):oldview.get('byteOffset',0)+oldview['byteLength']];newsegment=serialized_bin[newview.get('byteOffset',0):newview.get('byteOffset',0)+newview['byteLength']];assert oldsegment==newsegment,vi
 m0=trimesh.load(src,force='mesh',process=False);m1=trimesh.load(dst,force='mesh',process=False);assert np.array_equal(m0.vertices,m1.vertices) and np.array_equal(m0.faces,m1.faces);rows.append(dict(source=src.name,source_sha256=sha(src),output=dst.name,output_sha256=sha(dst),source_bytes=len(b),output_bytes=len(payload),faces=len(m1.faces),vertices=len(m1.vertices),geometry_arrays_exact=True,nonimage_bufferview_bytes_exact=True,texture_checks=checks,seconds=time.perf_counter()-t,method='Serialization derivative only: decode original inferredWebP and losslessly encode exactRGBA PNG; no new inference, recoloring, geometry, UV, or PBRparameters authored. Remove mandatory EXT_texture_webp dependency. OriginalGLB retained.'))
(root/'trellis2-portable-texture-derivative-receipt.json').write_text(json.dumps(dict(status='verified-serialization-derivatives-not-new-inference',items=rows),indent=2)+'\n');print(json.dumps(rows,indent=2))
