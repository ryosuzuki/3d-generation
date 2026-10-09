# 3D Generation — アプローチ別実装集

既存リポジトリは変更せず、確定commitから公開用ソースを選別したpublicカテゴリ集。各フォルダを独立した作業ディレクトリとして使えます。リンク集やsubmoduleではなくソース実体を収録しています。

| フォルダ | 入力 → 出力 | 実行環境 / 状態 | 限界 |
|---|---|---|---|
| `closed-outline-inflation` | 閉じた輪郭 → GLB/OBJ | CPU Python・決定論的・実装済み | 対称厚み。意味/隠れ面/rigの推定なし |
| `asset-provenance-adapter` | 輪郭/既存mesh → 共通asset schema | CPU Python + browser JS・検証用fixture入り | 自動修復/一般形状推論/physicsなし |
| `neural-image-to-3d` | 画像 → TripoSR/Hunyuan、sketch→ControlNet画像→mesh | Apple MPS実験コード、モデル/環境は別途復元 | 不可視面は推定。誤認・形状逸脱あり |
| `typed-schema-to-mesh` | 明示schema → indexed mesh | Node・依存vendor内蔵・API不要 | AI生成schemaサーバーとavatarは別カテゴリ |

## 最初に動かす

各フォルダの `RUN.md` を参照。private実験ログと個人データは含めません。外部API/モデル生成は今回実行していません。

## ソース・復元・ライセンス

`provenance.json` に元repo、immutable commit、コピーした全ファイルのSHA256とbytesがあります。`python3 verify-snapshots.py` で完全性を確認できます。元repoは変更せず、ソースとsynthetic fixtureのみpublic公開。GPUモデルの重み、大量生成結果、部屋/人物のデータは含めません。

`RESTORE.md` に公開版の依存・入力assetの準備方法。MIT Three.js / TripoSRとTencent Hunyuan community licenseは元ファイルを保持。その他自作コードは上流でライセンス指定なしのため新たな包括ライセンスを付与しません。参照した研究コード・モデルのライセンスがすべて同じという意味ではありません。

関連カテゴリ: [image-tracking](https://github.com/ryosuzuki/image-tracking)、[digital-twin](https://github.com/ryosuzuki/digital-twin)、[3d-avatar](https://github.com/ryosuzuki/3d-avatar)。最後のカテゴリ側がavatar UIとquestion→schemaの統合アプリを所有します。
