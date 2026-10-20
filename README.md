# 3D Generation — implementations by approach

Public source selected from pinned commits, without modifying the original repositories. Each folder is an independent working directory containing actual source, not just links or submodules.

## Demos and runnable examples

These are **local runnable examples**, not public hosted applications or recorded demonstrations. No verified public recording of these exact four implementations is currently linked.

- [Closed-outline inflation: run and validate synthetic examples](closed-outline-inflation/RUN.md) — CPU Python, exports GLB/OBJ.
- [Asset adapter: run ten bundled synthetic cases](asset-provenance-adapter/RUN.md) — CPU Python and JavaScript transformation checks.
- [Typed schema to mesh: run the bundled example](typed-schema-to-mesh/RUN.md) — `node mesh-export.mjs example.json`, no API or model required.
- [Neural image/sketch to 3D: setup and inference commands](neural-image-to-3d/RUN.md) — requires model downloads and a compatible local environment; not a one-click hosted demo.
- For related recorded room-interaction demos, see the [Digital Twin demo catalog](https://github.com/ryosuzuki/digital-twin#demo-links). Those recordings are different implementations, not evidence of these generation methods.

| Folder | Input → output | Runtime / status | Limitations |
|---|---|---|---|
| `closed-outline-inflation` | Closed outline → GLB/OBJ | CPU Python; deterministic; implemented | Symmetric thickness; no semantic, hidden-surface, or rig inference |
| `asset-provenance-adapter` | Outline/existing mesh → common asset schema | CPU Python + browser JS; validation fixtures included | No automatic repair, general shape inference, or physics |
| `neural-image-to-3d` | Image → TripoSR/Hunyuan; sketch → ControlNet image → mesh | Experimental Apple MPS source; restore models/environment separately | Unseen surfaces inferred; semantic and shape errors possible |
| `typed-schema-to-mesh` | Explicit schema → indexed mesh | Node; vendored dependencies; no API | AI schema server and avatars belong to another category |

## Get started

See each folder’s `RUN.md`. Private experiment logs and personal data are excluded. External API calls and model inference were not performed during source consolidation or English documentation cleanup.

## Source, restoration, and licenses

`provenance.json` records upstream repositories, immutable commits, and the SHA-256 digests and byte sizes of copied files. Run `python3 verify-snapshots.py` to check integrity. The original repositories are unchanged; only source and synthetic fixtures are public here. GPU model weights, bulk generated outputs, and room/person data are excluded.

`RESTORE.md` explains public dependencies and input asset preparation. Original MIT Three.js / TripoSR notices and the Tencent Hunyuan community license are retained. Other custom upstream code has no explicit license; this repository does not grant a new blanket license or imply that all referenced research code and models share the same terms.

Related categories: [image-tracking](https://github.com/ryosuzuki/image-tracking), [digital-twin](https://github.com/ryosuzuki/digital-twin), and [3d-avatar](https://github.com/ryosuzuki/3d-avatar). The avatar category owns the avatar UI and integrated question-to-schema application.
