"""CPU orthographic silhouette renderer with a triangle depth buffer (not Freestyle)."""
import argparse
import numpy as np
import trimesh
from PIL import Image,ImageDraw

def render(mesh,path,size=640,azimuth=-25,elevation=28):
    az,el=np.deg2rad([azimuth,elevation]);view=np.array([np.sin(az)*np.cos(el),-np.cos(az)*np.cos(el),np.sin(el)])
    right=np.cross(view,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,view)
    uv=mesh.vertices@np.stack([right,up]).T;lo=uv.min(0);span=max(np.ptp(uv,axis=0));px=(uv-lo)/span*(size-60)+30;px[:,1]=size-px[:,1]
    depths=mesh.vertices@view;zbuf=np.full((size,size),-np.inf)
    for face in mesh.faces:
        t=px[face];z=depths[face];xmin,ymin=np.maximum(0,np.floor(t.min(0))).astype(int);xmax,ymax=np.minimum(size-1,np.ceil(t.max(0))).astype(int)
        if xmax<xmin or ymax<ymin:continue
        x,y=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        a,b,c=t;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w2=1-w0-w1
        zz=w0*z[0]+w1*z[1]+w2*z[2];visible=(w0>=-1e-5)&(w1>=-1e-5)&(w2>=-1e-5)
        target=zbuf[ymin:ymax+1,xmin:xmax+1];np.maximum(target,np.where(visible,zz,-np.inf),out=target)
    adj=mesh.face_adjacency;dot=mesh.face_normals@view;edges=mesh.face_adjacency_edges[(dot[adj[:,0]]*dot[adj[:,1]])<0]
    im=Image.new('RGB',(size,size),'white');draw=ImageDraw.Draw(im)
    for a,b in edges:
        # Draw only short portions whose interpolated depth reaches the visible surface.
        steps=max(3,int(np.linalg.norm(px[a]-px[b])*2));ts=np.linspace(0,1,steps)
        xy=px[a][None,:]*(1-ts[:,None])+px[b][None,:]*ts[:,None];z=depths[a]*(1-ts)+depths[b]*ts
        ids=np.clip(np.rint(xy).astype(int),0,size-1)
        local=np.minimum.reduce([zbuf[np.clip(ids[:,1]+dy,0,size-1),np.clip(ids[:,0]+dx,0,size-1)] for dy in [-1,0,1] for dx in [-1,0,1]])
        visible=z>=local-.007
        for i in range(len(xy)-1):
            if visible[i] and visible[i+1]:draw.line([tuple(xy[i]),tuple(xy[i+1])],fill=(28,28,28),width=2)
    im.save(path)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mesh');p.add_argument('output');args=p.parse_args();render(trimesh.load(args.mesh,force='mesh'),args.output)
