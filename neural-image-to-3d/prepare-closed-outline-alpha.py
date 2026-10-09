"""Declared sketch mask hypothesis: enclosed white regions are object interior.

Not learned segmentation and not color repainting; original source RGB pixels
stay exact. The new alpha is retained separately and its assumption is recorded.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes,binary_closing
p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();root=Path(a.root);rp=root/'input-provenance.json';d=json.loads(rp.read_text())
for key in ['fish-stroke','owl-stroke']:
 src=root/f'{key}-input.png';rgba=np.asarray(Image.open(src).convert('RGBA'));line=np.min(rgba[:,:,:3],axis=2)<200;closed=binary_closing(line,structure=np.ones((5,5),bool));mask=binary_fill_holes(closed)|line;out=rgba.copy();out[:,:,3]=mask.astype('uint8')*255;id=key+'-closed-alpha';dst=root/f'{id}-input.png';Image.fromarray(out).save(dst);mp=root/f'{id}-mask.png';Image.fromarray(out[:,:,3]).save(mp)
 assert np.array_equal(np.asarray(Image.open(dst))[:,:,:3],rgba[:,:,:3]);d['items']=[x for x in d['items'] if x['id']!=id];d['items'].append(dict(id=id,input=dst.name,input_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),source_input=src.name,source_input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),mask=mp.name,mask_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),foreground_pixels=int(mask.sum()),provenance='Original authored stroke fixture plus DECLARED nonlearned alpha mask: pixels<200,5x5 binary closing,fill enclosed holes,union original strokes. OriginalRGB pixels exact. Assumes enclosed whitepaper area is object interior; not learned segmentation or human sketch. No procedural mesh supplied.'))
rp.write_text(json.dumps(d,indent=2));print('Prepared two closed-outline alpha hypotheses; sourceRGB exact')
