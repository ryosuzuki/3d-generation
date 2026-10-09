# Run

```sh
cd closed-outline-inflation
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python inflate.py --output output/example
.venv/bin/python validate.py --output output/example
```

独立CPU実装。元READMEの入力仕様/拒否条件/限界を参照。outputはGit対象外。
