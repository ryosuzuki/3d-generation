# Typed schema → indexed mesh

```sh
cd typed-schema-to-mesh
node mesh-export.mjs example.json > /tmp/typed-mesh.json
```

APIなしでローカル実行できる安全な型付きgeometry compiler。lathe / sweep / extrude / indexed meshを扱う。example.jsonは新規手書きの試験入力で、モデル生成結果ではない。question → schemaのAIサーバーやavatarはここには含めず、元のavatar-generalized-sketch-v2と新しい3d-avatarカテゴリを参照する。

vendor Three.jsとMIT licenseを保持。位置合わせ・組立ては宣言された入力に依存し、重なった部品はboolean unionされた物理実体ではない。
