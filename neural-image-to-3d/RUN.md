# Neural image → 3D / sketch → image → 3D

```sh
cd neural-image-to-3d
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements-mac-lock.txt
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git hunyuan-upstream
git -C hunyuan-upstream checkout f8db63096c8282cb27354314d896feba5ba6ff8a
git clone https://github.com/VAST-AI-Research/TripoSR.git triposr-upstream
git -C triposr-upstream checkout 107cefdc244c39106fa830359024f6a2f1c78871
mkdir -p output
# Put your own licensed RGBA image in output/my-object-input.png first.
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python run-triposr.py --output output --ids my-object --device mps --resolution 128
# Alternative geometry model:
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python run-shape.py --output output --ids my-object --device mps --steps 30 --resolution 256
```

Experimental Apple MPS source. Image-model weights use pinned revisions. Initial download time, inference time, and memory requirements depend on the environment. Unseen surfaces are inferred; semantic, silhouette, and mechanical correctness are not guaranteed. TripoSR produces vertex colors; the Hunyuan shape pipeline produces untextured geometry.

The sketch bridge converts the bundled hand-authored synthetic SVG fixtures to ControlNet images, extracted foregrounds, and then 3D. These fixtures are not user-study participants’ drawings.
```sh
.venv/bin/python prepare-stroke-fixtures.py output
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python run-controlnet-bridge.py --output output --scale .65
.venv/bin/python prepare-bridge-inputs.py output --scale .65
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python run-triposr.py --output output --ids fish-stroke-sdxl-bridge owl-stroke-sdxl-bridge --device mps --resolution 128
```

SDXL, ControlNet, U2Net, Tencent community/MIT terms are separate. This repository retains the original Hunyuan and TripoSR license notices. No paid/API inference performed for consolidation.
