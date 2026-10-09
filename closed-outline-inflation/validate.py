"""Geometry invariants and closed-stroke preservation, not category recognition."""
import json,argparse
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon
from inflate import inflate,examples
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).parent/'output/2026-10-09');out=parser.parse_args().output
for name,points in examples().items():
    poly=Polygon(points);scale=max(np.ptp(points,axis=0));expected=np.asarray(points)-np.asarray(poly.centroid.coords[0]);expected/=scale
    for ext in ['obj','glb']:
        m=trimesh.load(out/f'{name}.{ext}',force='mesh');assert m.is_watertight and m.is_winding_consistent and m.volume>0
        assert m.euler_number==2 and len(m.split())==1
        assert np.isfinite(m.vertex_normals).all() and np.allclose(np.linalg.norm(m.vertex_normals,axis=1),1,atol=1e-5)
        assert np.all(m.area_faces>1e-13),'degenerate triangles'
        for p in expected:assert np.min(np.linalg.norm(m.vertices[:,:2]-p,axis=1))<1e-6,'lost original boundary point'
        t=m.triangles[:,:,:2];areas=np.abs((t[:,1,0]-t[:,0,0])*(t[:,2,1]-t[:,0,1])-(t[:,1,1]-t[:,0,1])*(t[:,2,0]-t[:,0,0]))/2
        assert np.isclose(areas.sum()/2,poly.area/scale**2,rtol=1e-6),'projected area mismatch'
for points in [[[0,0],[1,1],[0,1],[1,0]],[[0,0],[1,0],[2,0]]]:
    try:inflate(points)
    except ValueError:pass
    else:raise AssertionError('Invalid input silently accepted')
# Arbitrary unsampled star-shaped outline (not a model selected by category).
a=np.linspace(0,2*np.pi,37,endpoint=False);r=.8+.12*np.sin(7*a)+.04*np.cos(3*a);m=inflate(np.c_[r*np.cos(a),r*np.sin(a)],subdivisions=2);assert m.is_watertight
print('PASS: 6 interchange meshes topology, unit normals, zero degenerates, original boundary vertex retention and projected area; invalid input rejection; arbitrary 37-point new silhouette.')
