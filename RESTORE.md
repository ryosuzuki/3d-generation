# Dependencies and assets

No personal recordings, avatar/room scans, learned-output fixtures, model weights or host-specific paths are distributed here. Source dependencies are listed per method.

- Closed-outline inflation: install `requirements.txt`, supply a simple closed polygon JSON. `inflate.py --output output/example` also produces its own authored fixtures.
- Adapter: all ten synthetic contour/mesh cases are bundled; `node check-js.mjs` compares immutable schema → JS transformations with reference results. Python smoke test needs its requirements.
- Typed compiler: vendor includes required Three.js modules and MIT license; no asset restoration needed.
- Neural inference: clone pinned upstream revisions listed in `neural-image-to-3d/RUN.md`, install requirements, supply your own licensed RGBA image as `<id>-input.png` in the output directory. Script downloads pinned public weights and writes actual input/output hashes. Do not invoke inference without reviewing model licenses and resource requirements. We did not run inference/API calls during organization.

The original private experiment sources/outputs are not necessary for these source-only methods. Exact private restoration paths remain in the owner's workspace receipt, not on public GitHub.
