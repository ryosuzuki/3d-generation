# Primary-paper checks, 2026-10-09

Bounded review, not exhaustive recall / saturation claim. Original paper HTML via arXiv avoids publisher or browser authentication and preserves version metadata.

## SketchDream — arXiv:2405.06461v1

https://arxiv.org/html/2405.06461v1 ; DOI 10.1145/3658120, TOG43(4), SIGGRAPH2024.

Abstract/method: sketch-based text-to-3D generation/editing; sketch-conditioned multiview diffusion, depth-guided warping, 3D attention control, SDS generation, coarse/fine local editing. Text and sketch constraints complementary, but require inferred depth/appearance rather than recover unique geometry.

§5 Implementation Details: “We implement sketch-based generation and editing on a single NVIDIA RTX A100. It takes 1.0-1.3 hours to generate a single example depending on the area size of the objects in sketches.” The source calls it “RTX A100”; retain that verbatim instead of silently correcting the GPU branding. Repository says tested80GBVRAM.

§6 Conclusion limitations: strange sketches beyond training data may degrade shape faithfulness and realism; too-strange editing cases have fuzzy details; detailed lighting/color/material control remains difficult; sketches loosely control layout but not mushroom-dot detail. Exact practical constraint: “our current system currently requires about 1 hour for generation and 1.5 hours for editing, and thus does not support interactive generation or editing.”

Decision: strongest recent verified SIGGRAPH candidate in this bounded review, but not interactive implementation on a16GBGPU. Lower-resolution flags do not prove small-GPU or low-latency success.

## Sketch2Model — arXiv:2105.06663v1

https://arxiv.org/html/2105.06663 ; CVPR2021.

Abstract/§3: view-aware reconstruction reduces pose ambiguity by conditioning generation on inferred or user-selected viewpoint. §4 datasets distinguish ShapeNet synthetic and handdrawn sketches. This does not imply category-free generation; official code explicitly selects class ID and provides13class checkpoints. View-conditioned outputs valuable for user intention, but unknown shape semantics remain a pretrained-distribution limitation.

Decision: test only for supported classes or adaptation/retraining; do not advertise arbitrary fish/octopus/leaf support from the downloadable checkpoint list.

## Sketch2Mesh — arXiv:2104.00482v2

https://arxiv.org/html/2104.00482 ; ICCV2021.

Abstract/§3: encoder/decoder latent shape, reconstruction followed by external-contour matching (differentiable rendering or2DChamfer). Camera-known UI and partial stroke edits refine mesh latent code. §4 car/chair datasets; official downloadable checkpoint support is cars/chairs. Partial-stroke editing is not the same as reconstructing every unknown arbitrary singlestroke object.

Decision: useful interaction and latent refinement idea; GPL3 official implementation and category-limited downloadable models are distinct from a general engine.

## Verified upstream ambiguity

Teddy is SIGGRAPH1999; MonsterMash is SIGGRAPHAsia2020; SketchDream is SIGGRAPH2024. They are confirmed distinct identities. The user's intended spoken reference and “PICASSO” cannot be identified from these names alone. Keep unresolved instead of claiming a guessed match.
