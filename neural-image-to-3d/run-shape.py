"""Actual official pretrained Hunyuan neural inference on CUDA, MPS or CPU.

No procedural shape generation. CPU Lewiner extraction is upstream's mc path.
MPS port uses upstream device argument; no shared runtime is modified.
"""
from pathlib import Path
import argparse, hashlib, json, sys, time, subprocess, traceback, resource
p=argparse.ArgumentParser()
p.add_argument('--model-size',choices=['mini','full'],default='mini');p.add_argument('--output',required=True);p.add_argument('--ids',nargs='+',default=['fish','turtle'])
p.add_argument('--run-name',default='');p.add_argument('--device',default='mps');p.add_argument('--steps',type=int,default=30)
p.add_argument('--resolution',type=int,default=128);p.add_argument('--seed',type=int,default=42)
p.add_argument('--upstream',default=str(Path(__file__).parent/'hunyuan-upstream'))
args=p.parse_args();root=Path(args.output);sys.path.insert(0,args.upstream)
import numpy as np, torch
from PIL import Image
from huggingface_hub import snapshot_download
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
revision='f90a0f7df7d5e6f71109cf333f6a95a0ae3194a6' if args.model_size=='mini' else '9cd649ba6913f7a852e3286bad86bfa9a2d83dcf'
model_id='tencent/Hunyuan3D-2mini' if args.model_size=='mini' else 'tencent/Hunyuan3D-2'
subfolder='hunyuan3d-dit-v2-mini' if args.model_size=='mini' else 'hunyuan3d-dit-v2-0'
model_label='hunyuan' if args.model_size=='mini' else 'hunyuan-full'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sync():
 if args.device=='cuda':torch.cuda.synchronize()
 elif args.device=='mps':torch.mps.synchronize()
receipt=dict(status='loading',model=model_id,revision=revision,upstream_commit=subprocess.check_output(['git','-C',args.upstream,'rev-parse','HEAD'],text=True).strip(),device=args.device,torch=torch.__version__,steps=args.steps,octree_resolution=args.resolution,seed=args.seed,precision='float16',surface_extraction='official CPU scikit-image Lewiner mc',texture_generation=False,items=[],limits=['Single-image learned geometry including unobserved sides; not calibrated scanning or scientific topology','Per-input provenance distinguishes primitive sanity fixtures, public official images, and automatic contour surrogates; training-set membership unknown','MPS current allocated memory is not peak total-board memory; process RSS includes CPU/model buffers'])
receiptpath=root/f'{model_label}-{args.device}-s{args.steps}-r{args.resolution}-seed{args.seed}{("-"+args.run_name) if args.run_name else ""}-receipt.json'
def save():receiptpath.write_text(json.dumps(receipt,indent=2))
save();t=time.perf_counter();snap=Path(snapshot_download(model_id,revision=revision,allow_patterns=[f'{subfolder}/config.yaml',f'{subfolder}/model.fp16.safetensors','LICENSE*']));receipt['checkpoint_download_seconds']=time.perf_counter()-t
folder=snap/subfolder;receipt['checkpoint_sha256']=sha(folder/'model.fp16.safetensors');t=time.perf_counter()
pipe=Hunyuan3DDiTFlowMatchingPipeline.from_single_file(str(folder/'model.fp16.safetensors'),str(folder/'config.yaml'),device=args.device,dtype=torch.float16,use_safetensors=True)
sync();receipt['model_load_seconds']=time.perf_counter()-t;receipt['status']='running';save()
for key in args.ids:
 row=dict(id=key,status='running',input_sha256=sha(root/f'{key}-input.png'));receipt['items'].append(row);save()
 try:
  if args.device=='cuda':torch.cuda.reset_peak_memory_stats()
  t=time.perf_counter();mesh=pipe(image=Image.open(root/f'{key}-input.png').convert('RGBA'),num_inference_steps=args.steps,octree_resolution=args.resolution,num_chunks=4000,mc_algo='mc',generator=torch.Generator(device='cpu').manual_seed(args.seed))[0];sync();row['pipeline_seconds']=time.perf_counter()-t
  assert mesh is not None and np.isfinite(mesh.vertices).all() and len(mesh.faces)>0
  stem=f'{key}-{model_label}-{args.device}-s{args.steps}-r{args.resolution}-seed{args.seed}'
  mesh.export(root/f'{stem}.glb');mesh.export(root/f'{stem}.obj');row.update(status='actual-neural-shape-inference-complete',glb=f'{stem}.glb',obj=f'{stem}.obj',glb_sha256=sha(root/f'{stem}.glb'),obj_sha256=sha(root/f'{stem}.obj'),vertices=len(mesh.vertices),faces=len(mesh.faces),bounds=mesh.bounds.tolist(),watertight=bool(mesh.is_watertight),components=len(mesh.split(only_watertight=False)),max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
  if args.device=='cuda':row['peak_torch_allocated_bytes']=torch.cuda.max_memory_allocated()
  elif args.device=='mps':row.update(mps_current_allocated_bytes=torch.mps.current_allocated_memory(),mps_driver_allocated_bytes=torch.mps.driver_allocated_memory())
 except Exception as e:row.update(status='failed',error=str(e),traceback=traceback.format_exc());print(traceback.format_exc(),flush=True)
 save();print(json.dumps(row),flush=True)
receipt['status']='inference-complete' if all(x['status']=='actual-neural-shape-inference-complete' for x in receipt['items']) else 'complete-with-failures';save()
