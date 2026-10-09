"""Rasterize original vector stroke fixtures; record authorship honestly."""
from pathlib import Path
import argparse,hashlib,json
import cairosvg
p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();root=Path(a.root);src=Path(__file__).parent;rp=root/'input-provenance.json';d=json.loads(rp.read_text())
for key in ['fish-stroke','owl-stroke']:
 svg=src/f'{key}-fixture.svg';out=root/f'{key}-input.png';cairosvg.svg2png(url=str(svg),write_to=str(out),output_width=768,output_height=768);d['items']=[x for x in d['items'] if x['id']!=key];d['items'].append(dict(id=key,input=out.name,input_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source=svg.name,source_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),provenance='Original experiment-authored 2D black stroke SVG fixture, rasterized on opaque whitepaper; NOT a human drawing. Not derived from previous richimage/mesh. No authored3D geometry supplied to inference.'))
rp.write_text(json.dumps(d,indent=2));print('Two original stroke inputs rasterized')
