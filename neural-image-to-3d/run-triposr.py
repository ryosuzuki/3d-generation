"""Pinned neural TripoSR on Apple MPS; honest CPU surface extraction adapter."""
from pathlib import Path
import argparse, hashlib, json, resource, subprocess, sys, time, types, traceback
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--ids',nargs='+',required=True);p.add_argument('--run-name',default='');p.add_argument('--color-encoding',choices=['native','gltf-linear'],default='native');p.add_argument('--device',default='mps');p.add_argument('--resolution',type=int,default=128);a=p.parse_args();root=Path(a.output);up=Path(__file__).parent/'triposr-upstream';sys.path.insert(0,str(up))
import torch,numpy as np
from PIL import Image
from skimage.measure import marching_cubes
from huggingface_hub import hf_hub_download
adapter=types.ModuleType('torchmcubes')
def mc(v,l):
 vs,fs,_,_=marching_cubes(v.detach().cpu().numpy(),l);return torch.from_numpy(vs[:,[2,1,0]].copy()),torch.from_numpy(fs.copy()).long()
adapter.marching_cubes=mc;sys.modules['torchmcubes']=adapter
from tsr.system import TSR
rev='5b521936b01fbe1890f6f9baed0254ab6351c04a'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sync():
 if a.device=='mps':torch.mps.synchronize()
 elif a.device=='cuda':torch.cuda.synchronize()
receipt=dict(status='loading',model='stabilityai/TripoSR',revision=rev,upstream_commit=subprocess.check_output(['git','-C',str(up),'rev-parse','HEAD'],text=True).strip(),device=a.device,precision='float32',torch=torch.__version__,mesh_resolution=a.resolution,marching_cubes='scikit-image CPU Lewiner adapter; official neural layers unchanged',items=[],limits=['Inferred unseen surfaces, not measured scan','Vertex colors inferred by official model, not UV PBR texture'])
rp=root/f'triposr-{a.device}-r{a.resolution}{("-"+a.run_name) if a.run_name else ""}-receipt.json'
def save():rp.write_text(json.dumps(receipt,indent=2))
save();checkpoint=hf_hub_download('stabilityai/TripoSR','model.ckpt',revision=rev);config=hf_hub_download('stabilityai/TripoSR','config.yaml',revision=rev);receipt['checkpoint_sha256']=sha(checkpoint);t=time.perf_counter();model=TSR.from_pretrained(str(Path(checkpoint).parent),config_name='config.yaml',weight_name='model.ckpt').to(a.device);model.eval();model.renderer.set_chunk_size(8192);sync();receipt['load_seconds']=time.perf_counter()-t
with torch.inference_mode():
 for key in a.ids:
  row=dict(id=key,input_sha256=sha(root/f'{key}-input.png'),status='running');receipt['items'].append(row);save()
  try:
   arr=np.asarray(Image.open(root/f'{key}-input.png').convert('RGBA'),dtype=np.float32)/255;im=Image.fromarray(((arr[:,:,:3]*arr[:,:,3:4]+.5*(1-arr[:,:,3:4]))*255).astype('uint8'))
   t=time.perf_counter();codes=model([im],device=a.device);sync();row['forward_seconds']=time.perf_counter()-t;t=time.perf_counter();mesh=model.extract_mesh(codes,has_vertex_color=True,resolution=a.resolution)[0];sync();row['surface_extraction_seconds']=time.perf_counter()-t
   if a.color_encoding=='gltf-linear':
    c=mesh.visual.vertex_colors.copy();v=c[:,:3].astype(np.float32)/255;c[:,:3]=np.round(np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)*255).astype(np.uint8);mesh.visual.vertex_colors=c;row['color_encoding']='Declared appearance encoding hypothesis: interpret upstream/PIL RGB as sRGB, convert to linear glTF COLOR_0. Not fresh colorfield inference or improved geometry; native export retained separately if available.'
   assert np.isfinite(mesh.vertices).all() and len(mesh.faces)>0;stem=f'{key}-triposr-{a.device}-r{a.resolution}'+(('-'+a.run_name) if a.run_name else '')+('-linearcolor' if a.color_encoding=='gltf-linear' else '');mesh.export(root/f'{stem}.glb');mesh.export(root/f'{stem}.obj');row.update(status='actual-neural-inference-complete',vertices=len(mesh.vertices),faces=len(mesh.faces),glb=f'{stem}.glb',glb_sha256=sha(root/f'{stem}.glb'),obj=f'{stem}.obj',obj_sha256=sha(root/f'{stem}.obj'),max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
   if a.device=='mps':row.update(mps_current_allocated_bytes=torch.mps.current_allocated_memory(),mps_driver_allocated_bytes=torch.mps.driver_allocated_memory())
  except Exception as e:row.update(status='failed',error=str(e),traceback=traceback.format_exc());print(traceback.format_exc(),flush=True)
  save();print(json.dumps(row),flush=True)
receipt['status']='inference-complete' if all(x['status']=='actual-neural-inference-complete' for x in receipt['items']) else 'complete-with-failures';save()
