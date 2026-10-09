# Adapter — independent run

```sh
cd asset-provenance-adapter
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python smoke.py
node check-js.mjs
```

CPU Python + browser-safe JS。10個のsynthetic authored contours/schema/meshを収録。inflate_source / import_asset / to_rendererが本体。元のprivate fish/owl GLB・研究ログ・host-specific browser harnessは非公開のまま。実assetの欠陥チェックは自身のlicensed GLBで行う。自動repair、rig推定、physicsはなし。
