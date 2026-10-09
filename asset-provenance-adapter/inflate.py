"""Independent closed-stroke inflation baseline; not a Teddy/Monster Mash reproduction."""
import argparse,json,time
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,Point
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def inflate(points, thickness=.32, subdivisions=4):
    if not np.isfinite(thickness) or thickness<=0: raise ValueError("Thickness must be finite and positive")
    points=np.asarray(points,float)
    if len(points)<3 or not np.isfinite(points).all(): raise ValueError('Need finite closed polygon vertices')
    poly=Polygon(points)
    if not poly.is_valid or poly.area<=1e-10: raise ValueError('Stroke must form a simple closed nonzero-area silhouette; no silent repair')
    center=np.asarray(poly.centroid.coords[0]); scale=max(np.ptp(points,axis=0)); poly=shapely.affinity.translate(poly,-center[0],-center[1]); poly=shapely.affinity.scale(poly,1/scale,1/scale,origin=(0,0))
    tris=[np.asarray(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(poly).geoms]
    subdivisions=min(subdivisions,max(0,int(np.log(max(1,120000/(12*len(tris))))/np.log(4))))
    for _ in range(subdivisions):
        refined=[]
        for a,b,c in tris:
            ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
            refined.extend([np.array([a,ab,ca]),np.array([ab,b,bc]),np.array([ca,bc,c]),np.array([ab,bc,ca])])
        tris=refined
    # Insert interior centers: avoid coincident front/back corner triangles.
    tris=[t for a,b,c in tris for t in [np.array([u,v,(a+b+c)/3]) for u,v in [(a,(a+b)/2),((a+b)/2,b),(b,(b+c)/2),((b+c)/2,c),(c,(c+a)/2),((c+a)/2,a)]]]
    verts=[]; faces=[]; index={}
    def vertex(xy,z):
        key=tuple(np.round([*xy,z],12))
        if key not in index: index[key]=len(verts);verts.append([*xy,z])
        return index[key]
    heights={}
    for tri in tris:
        for xy in tri:
            k=tuple(np.round(xy,12))
            if k not in heights:
                d=poly.boundary.distance(Point(xy));heights[k]=0 if d<1e-10 else thickness*np.sqrt(d)
        # all 2d triangles counterclockwise: front faces point +Z
        if ((tri[1,0]-tri[0,0])*(tri[2,1]-tri[0,1])-(tri[1,1]-tri[0,1])*(tri[2,0]-tri[0,0]))<0: tri=tri[[0,2,1]]
        top=[vertex(xy,heights[tuple(np.round(xy,12))]) for xy in tri]
        bottom=[vertex(xy,-heights[tuple(np.round(xy,12))]) for xy in tri]
        faces.extend([top,bottom[::-1]])
    mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
    mesh.remove_unreferenced_vertices();mesh.fix_normals()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume<=0: raise RuntimeError(f'Topology/normals validation failed: watertight={mesh.is_watertight}, winding={mesh.is_winding_consistent}, volume={mesh.volume}, euler={mesh.euler_number}, edges={np.unique(np.bincount(mesh.edges_unique_inverse),return_counts=True)}')
    mesh.visual.vertex_colors=[103,170,219,255]
    return mesh

def preview(mesh, points, path):
    fig=plt.figure(figsize=(12,4),facecolor='white')
    ax=fig.add_subplot(131);p=np.asarray(points);ax.plot(*np.vstack([p,p[0]]).T,c='#151515',lw=3);ax.set_title('Original closed stroke');ax.axis('equal');ax.axis('off')
    ax=fig.add_subplot(132,projection='3d'); coll=Poly3DCollection(mesh.triangles,linewidth=0); normals=mesh.face_normals;light=np.array([.3,-.5,.8]);light/=np.linalg.norm(light);shade=.4+.6*np.maximum(0,normals@light);coll.set_facecolor(np.c_[.38*shade,.7*shade,.9*shade,np.ones(len(shade))]);ax.add_collection3d(coll);ax.set_xlim(-.6,.6);ax.set_ylim(-.6,.6);ax.set_zlim(-.3,.3);ax.view_init(28,-68);ax.set_box_aspect((1,1,.5));ax.axis('off');ax.set_title('Actual inflated 3D mesh')
    ax=fig.add_subplot(133); az=np.deg2rad(-35);el=np.deg2rad(22);view=np.array([np.sin(az)*np.cos(el),-np.cos(az)*np.cos(el),np.sin(el)]);right=np.cross(view,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,view);projection=mesh.vertices@np.stack([right,up]).T
    adjacency=mesh.face_adjacency; dot=mesh.face_normals@view
    edges=mesh.face_adjacency_edges[(dot[adjacency[:,0]]*dot[adjacency[:,1]])<0]
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(projection[edges],colors='#171717',linewidths=1.3));ax.autoscale();ax.axis('equal');ax.axis('off');ax.set_title('View-dependent contour lines')
    fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def export(points,out,name,thickness=.32):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();m=inflate(points,thickness)
    m.export(out/f'{name}.glb');m.export(out/f'{name}.obj');preview(m,points,out/f'{name}-preview.png')
    # Independently reload both interchange formats, fail on regressions.
    for ext in ['glb','obj']:
        r=trimesh.load(out/f'{name}.{ext}',force='mesh');assert r.is_watertight and r.is_winding_consistent and r.volume>0
    result={'name':name,'vertices':len(m.vertices),'faces':len(m.faces),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'euler_number':int(m.euler_number),'components':len(m.split()),'volume':float(m.volume),'finite_unit_normals':bool(np.isfinite(m.vertex_normals).all() and np.allclose(np.linalg.norm(m.vertex_normals,axis=1),1)),'seconds_including_export_preview':time.perf_counter()-start}
    (out/f'{name}-stroke.json').write_text(json.dumps({'points':points,'thickness':thickness},indent=2));return result

def examples():
    fish=[[-1,0],[-.68,.38],[-.16,.48],[.25,.35],[.55,.16],[1,.47],[.85,0],[1,-.47],[.55,-.16],[.25,-.35],[-.16,-.48],[-.68,-.38]]
    leaf=[[0,1],[.26,.71],[.42,.43],[.46,.1],[.29,-.25],[.08,-.55],[.07,-1],[-.07,-1],[-.08,-.55],[-.3,-.25],[-.45,.1],[-.39,.45],[-.24,.76]]
    octopus=[[-.65,.2],[-.58,.65],[-.32,.95],[0,1.03],[.35,.92],[.61,.62],[.64,.2],[.93,-.19],[.95,-.57],[.81,-.72],[.76,-.51],[.72,-.23],[.49,.02],[.55,-.52],[.43,-.89],[.27,-.9],[.31,-.55],[.19,-.14],[.13,-.72],[0,-1],[-.15,-.99],[-.12,-.65],[-.23,-.12],[-.35,-.51],[-.3,-.88],[-.47,-.89],[-.62,-.56],[-.49,-.01],[-.73,-.22],[-.79,-.52],[-.82,-.72],[-.98,-.57],[-.95,-.19]]
    return {'fish':fish,'octopus':octopus,'leaf':leaf}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stroke',type=Path);p.add_argument('--output',type=Path,default=Path('output/2026-10-09'));p.add_argument('--name',default='custom');p.add_argument('--thickness',type=float);args=p.parse_args()
    if args.stroke:
        data=json.loads(args.stroke.read_text());res=[export(data['points'],args.output,args.name,args.thickness if args.thickness is not None else data.get('thickness',.32))]
    else: res=[export(v,args.output,k,args.thickness if args.thickness is not None else .32) for k,v in examples().items()]
    (args.output/'validation.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
