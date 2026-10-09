"""Experimental Hunyuan learned shape + TripoSR learned color field fusion.

No projected source texture and no Paint claim. Target geometry stays exact;
appearance is actual TripoSR neural querying under explicit bbox/axis alignment.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time,types
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('ids',nargs='+');a=p.parse_args();root=Path(a.root);up=Path(__file__).parent/'triposr-upstream';sys.path.insert(0,str(up))
import torch,numpy as np,trimesh
from PIL import Image
from skimage.measure import marching_cubes
from huggingface_hub import hf_hub_download
adapter=types.ModuleType('torchmcubes')
def mc(v,l):
 vs,fs,_,_=marching_cubes(v.detach().cpu().numpy(),l);return torch.from_numpy(vs[:,[2,1,0]].copy()),torch.from_numpy(fs.copy()).long()
adapter.marching_cubes=mc;sys.modules['torchmcubes']=adapter
from tsr.system import TSR
rev='5b521936b01fbe1890f6f9baed0254ab6351c04a';checkpoint=hf_hub_download('stabilityai/TripoSR','model.ckpt',revision=rev);hf_hub_download('stabilityai/TripoSR','config.yaml',revision=rev);t=time.perf_counter();model=TSR.from_pretrained(str(Path(checkpoint).parent),config_name='config.yaml',weight_name='model.ckpt').to('mps');model.eval();model.renderer.set_chunk_size(8192);torch.mps.synchronize();load=time.perf_counter()-t;items=[]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
with torch.inference_mode():
 for key in a.ids:
  hp=root/f'{key}-hunyuan-mps-s30-r256-seed42-mobile.glb';tp=root/f'{key}-triposr-mps-r128.glb';ip=root/f'{key}-input.png';h=trimesh.load(hp,force='mesh',process=False);tripo=trimesh.load(tp,force='mesh',process=False);arr=np.asarray(Image.open(ip).convert('RGBA'),dtype=np.float32)/255;image=Image.fromarray(((arr[:,:,:3]*arr[:,:,3:4]+.5*(1-arr[:,:,3:4]))*255).astype('uint8'));t=time.perf_counter();codes=model([image],device='mps');torch.mps.synchronize();forward=time.perf_counter()-t
  # Tripo's source camera is +X with Z-up; Hunyuan is +Z with Y-up.
  frac=(h.vertices-h.bounds[0])/(h.bounds[1]-h.bounds[0]);mapped=frac[:,[2,0,1]];pos=tripo.bounds[0]+mapped*(tripo.bounds[1]-tripo.bounds[0]);t=time.perf_counter();colors=model.renderer.query_triplane(model.decoder,torch.tensor(pos,dtype=torch.float32,device='mps'),codes[0])['color'];torch.mps.synchronize();query=time.perf_counter()-t;rgb=colors.cpu().numpy();assert np.isfinite(rgb).all()
  # Network output matches image/PIL sRGB; glTF COLOR_0 is linear.
  linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);rgba=np.concatenate([np.clip(linear,0,1),np.ones((len(linear),1))],axis=1);h.visual=trimesh.visual.ColorVisuals(vertex_colors=np.round(rgba*255).astype('uint8'));dst=root/f'{key}-hunyuan-shape-triposr-neural-color.glb';h.export(dst);check=trimesh.load(dst,force='mesh',process=False);assert np.array_equal(check.faces,h.faces) and np.allclose(check.vertices,h.vertices,atol=2e-7)
  row=dict(id=key,status='actual-neural-color-query-on-inferred-shape-complete',shape=hp.name,shape_sha256=sha(hp),color_model='stabilityai/TripoSR',color_model_revision=rev,reference_triposr_mesh=tp.name,reference_triposr_mesh_sha256=sha(tp),input_sha256=sha(ip),output=dst.name,output_sha256=sha(dst),faces=len(h.faces),vertices=len(h.vertices),color_forward_seconds=forward,color_query_seconds=query,alignment='Normalized per-axis bbox map from HunyuanXYZ to Tripo(ZXY source fractions): TripoXYZ positions=Hunyuan(ZXY fractions), no semantic registration. Original target geometry unchanged.',color_encoding='Neural renderer/PIL sRGB output converted to linear glTF COLOR_0, uint8',appearance_inference=True,paint_inference=False,projection=False,mps_current_allocated_bytes=torch.mps.current_allocated_memory(),mps_driver_allocated_bytes=torch.mps.driver_allocated_memory());items.append(row);print(json.dumps(row),flush=True)
  (root/'neural-color-fusion-receipt.json').write_text(json.dumps(dict(status='experimental-neural-color-fusion',model_load_seconds=load,items=items,limits=['Cross-model bbox alignment is an approximation, not geometric correspondence or texture registration','Color field infers unseen appearance, not measured texture','No UV/PBR material or Hunyuan Paint claim; target learned geometry unchanged']),indent=2))
