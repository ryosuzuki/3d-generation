"""Declared non-learned source projection onto genuinely inferred geometry.

This is NOT Hunyuan Paint or an inferred backside texture. The same visible
source colors project through the object; unseen-side coloring is an authored
display convention. Originals remain intact.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np,trimesh
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('ids',nargs='+');a=p.parse_args();root=Path(a.root);items=[]
for key in a.ids:
 src=root/f'{key}-hunyuan-mps-s30-r256-seed42-mobile.glb';imagepath=root/f'{key}-input.png';mesh=trimesh.load(src,force='mesh',process=False);rgba=np.asarray(Image.open(imagepath).convert('RGBA'));rgb=rgba[:,:,:3].astype(float)*rgba[:,:,3:4]/255+255*(1-rgba[:,:,3:4]/255)
 # Use declared image foreground bbox, not any learned texture/part estimator.
 foreground=rgba[:,:,3]>128 if np.any(rgba[:,:,3]<128) else np.min(rgb,axis=2)<245
 yy,xx=np.where(foreground);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];texture=Image.fromarray(rgb.astype('uint8')).crop(tuple(bbox));v=mesh.vertices;lo=mesh.bounds[0];hi=mesh.bounds[1];uv=(v[:,:2]-lo[:2])/(hi[:2]-lo[:2]);material=trimesh.visual.material.PBRMaterial(baseColorTexture=texture,metallicFactor=0,roughnessFactor=.8,alphaMode='OPAQUE',doubleSided=True);mesh.visual=trimesh.visual.texture.TextureVisuals(uv=uv,material=material);dest=root/f'{key}-hunyuan-mps-s30-r256-seed42-source-projected.glb';mesh.export(dest);check=trimesh.load(dest,force='mesh',process=False)
 assert len(check.faces)==len(mesh.faces) and np.isfinite(check.vertices).all();assert np.allclose(check.vertices,mesh.vertices,atol=2e-7)
 items.append(dict(id=key,source_glb=src.name,source_glb_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_image=imagepath.name,source_image_sha256=hashlib.sha256(imagepath.read_bytes()).hexdigest(),output_glb=dest.name,output_glb_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),geometry_faces=len(mesh.faces),projection='XY planar UV from inferred bounds to cropped visible source image; projects through whole object. Same visible colors on unseen back by authored convention, NOT neural Paint/inferred backside.',foreground_bbox=bbox,texture_pixels=list(texture.size),shape_inference=True,texture_inference=False,geometry_unchanged_float32_export_tolerance=2e-7))
(root/'source-texture-projection-receipt.json').write_text(json.dumps(dict(status='declared-source-projection-complete',items=items,limits=['Front-view texture approximate, perspective/material correspondence not recovered','Unseen surfaces receive mirrored projected source colors, not recovered truth','Source foreground bbox uses existing alpha or declared white threshold245']),indent=2));print(json.dumps(items,indent=2))
