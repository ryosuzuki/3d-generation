# Typed schema → indexed mesh

```sh
cd typed-schema-to-mesh
node mesh-export.mjs example.json > /tmp/typed-mesh.json
```

A locally runnable typed geometry compiler that requires no API. It supports lathe, sweep, extrude, and indexed meshes. example.json is a new hand-authored test input, not model-generated output. The question-to-schema AI server and avatar application are not included here; see the upstream avatar-generalized-sketch-v2 project and the 3d-avatar category.

Vendored Three.js modules and their MIT license are retained. Alignment and assembly depend on declared inputs; overlapping components are not Boolean-unioned physical solids.
