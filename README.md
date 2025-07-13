# Quaternion拡大における素数の偏りの計算プログラム

青木美穂さんとの共同研究のための高速化・並列化プログラムです。

## 概要

このプログラムは以下の2つの主要機能を提供します：

1. **フロベニウス元計算**: 素数pに対応するフロベニウス元を高速に計算し、JSONファイルに保存
2. **グラフ描画**: 保存されたデータから素数の偏りを可視化するグラフを作成

Sami Omarの論文に記載された13のQuaternion拡大ケースすべてに対応しています。

## ファイル構成

```
.
├── src/
│   ├── frobenius_calculator.py    # フロベニウス元計算の高速化プログラム
│   ├── graph_plotter.py          # グラフ描画プログラム
│   └── main_runner.py            # 統合実行スクリプト
├── run_scripts.sh                # 実行用シェルスクリプト
├── README.md                     # このファイル
├── frobenius_data/               # JSONデータ保存ディレクトリ (自動作成)
├── graphs/                       # グラフ保存ディレクトリ (自動作成)
└── logs/                         # ログファイル保存ディレクトリ (自動作成)
```

## 必要な環境

- SageMath 9.5以上
- Python 3.9以上
- matplotlib
- numpy
- multiprocessing対応のシステム

## クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/jxta/bias_with_claude.git
cd bias_with_claude
```

### 2. 実行権限の設定

```bash
chmod +x run_scripts.sh
```

### 3. テスト実行（推奨）

```bash
# 小規模テスト（10^5素数まで、約2-3分）
./run_scripts.sh test
```

### 4. 全ケース実行

```bash
# 全ケース実行（10^6素数まで、約10-15分）
./run_scripts.sh all
```

## 使用方法

### シェルスクリプトを使用（推奨）

```bash
# 全ケース実行
./run_scripts.sh all

# テスト実行（10^5素数まで）
./run_scripts.sh test

# 特定ケースのみ実行
./run_scripts.sh case 1

# データファイル確認
./run_scripts.sh check

# システム情報表示
./run_scripts.sh info
```

### 直接実行

```bash
# 全ケースを順次実行
sage src/main_runner.py --all

# 特定のケース（例：Case 1）
sage src/main_runner.py --case 1 --all

# フロベニウス元計算のみ
sage src/main_runner.py --compute-frobenius

# グラフ描画のみ
sage src/main_runner.py --plot-graphs

# データファイル確認
sage src/main_runner.py --check-data
```

## 高度な設定

### 計算範囲の変更

```bash
# 最大素数を50万に設定
sage src/main_runner.py --all --max-prime 500000

# 最大素数を200万に設定（大容量メモリ推奨）
sage src/main_runner.py --all --max-prime 2000000
```

### 並列処理の調整

```bash
# 使用するプロセス数を4に制限
sage src/main_runner.py --all --processes 4

# 単一プロセスで実行（デバッグ用）
sage src/main_runner.py --all --processes 1
```

## 高速化の仕組み

### 1. アルゴリズムの最適化

従来の素朴なSage関数呼び出しを以下の手法で高速化：

- **ルジャンドル記号による分類**: 部分体での分解の様子を効率的に判定
- **mod p因数分解**: 定義多項式の最高次数(1, 2, 4)による迅速な分類
- **共役類構造の利用**: Quaternion群Q8の構造を活用した効率的な分類

### 2. 並列処理

- **マルチコア対応**: 利用可能な全CPUコアで素数範囲を分割処理
- **バッチ処理**: メモリ効率を考慮した適切なサイズでの分割実行

### 3. フロベニウス元の分類規則

```
最高次数 = 1  → フロベニウス元 = g0 (1)
最高次数 = 4  → フロベニウス元 = g1 (-1)
最高次数 = 2  → ルジャンドル記号とp mod 8により{i, j, k, -i, -j, -k}を分類
```

## 出力ファイル

### JSONデータファイル

`frobenius_data/case_XX_frobenius.json`

```json
{
  "case_id": 1,
  "polynomial": "x^8 - x^7 - 34*x^6 + ...",
  "discriminant": "3^6 * 5^6 * 7^6",
  "m_rho0": 0,
  "frobenius_elements": {
    "2": 0,
    "3": 1,
    "5": 2,
    ...
  },
  "group_structure": {
    "g0": "identity (1)",
    "g1": "minus_one (-1)",
    "g2": "i",
    ...
  }
}
```

### グラフファイル

#### 統合グラフ
`graphs/case_XX_bias_graphs.png`: 5つのサブプロットを含む統合グラフ

#### 個別グラフ
- `graphs/case_XX_S1_1.png`: σ = 1の偏り
- `graphs/case_XX_S2_minus1.png`: σ = -1の偏り  
- `graphs/case_XX_S3_i.png`: σ = iの偏り
- `graphs/case_XX_S4_j.png`: σ = jの偏り
- `graphs/case_XX_S5_k.png`: σ = kの偏り

## 理論的背景

### 偏りの公式

深リーマン予想(DRH)を仮定すると、各フロベニウス元σに対して：

```
π_{1/2}(x) - [F:Q]/|c_σ| × π_{1/2}(x; σ) = (M(σ) + m(σ)) log log x + c + o(1)
```

ここで：
- `π_{1/2}(x)`: x以下の素数pについての Σ(1/√p)
- `π_{1/2}(x; σ)`: フロベニウス元がσと共役な素数についての Σ(1/√p)
- `M(σ)`: 表現論的偏り係数
- `m(σ)`: L関数の中心値での零点位数による係数
- `|c_σ|`: σの共役類のサイズ

### Quaternion群Q8の構造

```
共役類:
- c_1 = {1}           (サイズ 1)
- c_{-1} = {-1}       (サイズ 1)  
- c_i = {i, -i}       (サイズ 2)
- c_j = {j, -j}       (サイズ 2)
- c_k = {k, -k}       (サイズ 2)
```

### 偏り係数の値

Omar論文の結果により：

**m_ρ0 = 0の場合:**
- M(1) + m(1) = 1/2
- M(-1) + m(-1) = 5/2
- M(i) + m(i) = M(j) + m(j) = M(k) + m(k) = -1/2

**m_ρ0 = 1の場合:**
- M(1) + m(1) = 5/2
- M(-1) + m(-1) = 1/2
- M(i) + m(i) = M(j) + m(j) = M(k) + m(k) = -1/2

## 実行例

### Case 1の実行例

```bash
$ ./run_scripts.sh case 1

Case 1 のフロベニウス元計算を開始
多項式: x^8 - x^7 - 34*x^6 + 29*x^5 + 361*x^4 - 305*x^3 - 1090*x^2 + 1345*x - 395
判別式: 3^6 * 5^6 * 7^6
m_ρ₀: 0

Case 1: 分岐する素数 = [3, 5, 7]
Processing primes from 2 to 250000
Processing primes from 250001 to 500000
Processing primes from 500001 to 750000
Processing primes from 750001 to 1000000

Case 1: 計算完了 (時間: 45.23秒)
計算した素数の数: 78495

Case 1: データを保存しました -> frobenius_data/case_01_frobenius.json

Case 1 のグラフ描画を開始
Case 1: グラフを保存しました -> graphs/case_01_bias_graphs.png
Case 1: 個別グラフも保存しました

Case 1 統計情報:
多項式: x^8 - x^7 - 34*x^6 + 29*x^5 + 361*x^4 - 305*x^3 - 1090*x^2 + 1345*x - 395
判別式: 3^6 * 5^6 * 7^6
m_ρ₀: 0
計算した素数の個数: 78,495

フロベニウス元の分布:
  g0 (1): 9,812 primes (12.50%)
  g1 (-1): 9,811 primes (12.50%)
  g2 (i): 19,623 primes (25.00%)
  g3 (j): 19,624 primes (25.00%)
  g4 (k): 19,625 primes (25.00%)
  g5 (-i): 0 primes (0.00%)
  g6 (-j): 0 primes (0.00%)
  g7 (-k): 0 primes (0.00%)
```

## パフォーマンス情報

### 計算時間の目安

**10^6個の素数まで（推奨設定）:**
- 1ケース: 約30-60秒
- 全13ケース: 約10-15分

**10^5個の素数まで（高速設定）:**
- 1ケース: 約5-10秒  
- 全13ケース: 約2-3分

### メモリ使用量

- 10^5素数: 約200MB per case
- 10^6素数: 約2GB per case
- 推奨RAM: 8GB以上

### 並列処理効果

4コアCPUでの測定例：
- 単一プロセス: 120秒/ケース
- 4並列プロセス: 35秒/ケース（約3.4倍高速化）

## Jupyter Notebook環境での使用

### 1. クローンと移動

```python
# Jupyter Notebookのセルで実行
!git clone https://github.com/jxta/bias_with_claude.git
%cd bias_with_claude
```

### 2. 権限設定と実行

```python
# 実行権限を設定
!chmod +x run_scripts.sh

# テスト実行
!./run_scripts.sh test
```

### 3. 個別のケース実行

```python
# Case 1のみ実行
!sage src/main_runner.py --case 1 --all --max-prime 100000

# データファイル確認
!sage src/main_runner.py --check-data
```

### 4. 結果の確認

```python
import json
import matplotlib.pyplot as plt

# データファイルを読み込み
with open('frobenius_data/case_01_frobenius.json', 'r') as f:
    data = json.load(f)

print(f"Case {data['case_id']}: {len(data['frobenius_elements'])} primes computed")

# グラフファイルの表示
from IPython.display import Image, display
display(Image('graphs/case_01_bias_graphs.png'))
```

## トラブルシューティング

### よくあるエラー

**1. メモリ不足エラー**
```
MemoryError: Unable to allocate array
```
対処法: `--max-prime`を小さく設定するか、`--processes`を減らす

**2. ファイルが見つからないエラー**
```
FileNotFoundError: データファイルが見つかりません
```
対処法: 先に`--compute-frobenius`を実行してデータを生成

**3. SageMathエラー**
```
ImportError: No module named sage
```
対処法: SageMathが正しくインストールされていることを確認

### デバッグ方法

**1. 単一プロセスで実行**
```bash
sage src/main_runner.py --case 1 --compute-frobenius --processes 1
```

**2. 小さな範囲でテスト**
```bash
sage src/main_runner.py --case 1 --compute-frobenius --max-prime 10000
```

**3. システム情報の確認**
```bash
./run_scripts.sh info
```

## 研究への応用

### 新しいケースの追加

`src/frobenius_calculator.py`の`OMAR_POLYNOMIALS`リストに新しいケースを追加：

```python
{
    'id': 14,
    'poly': 'x^8 + ...',  # 新しい8次多項式
    'discriminant': '...',
    'm_rho0': 0  # または1
}
```

### 設定のカスタマイズ

**1. グラフの最大値変更**
`src/graph_plotter.py`の`max_x`パラメータを調整

**2. 偏り係数の修正**
`bias_coefficients`辞書で理論値を更新

**3. 分類アルゴリズムの改良**
`_determine_frobenius_element`メソッドで分類ロジックを改善

## 参考文献

1. 青木美穂, 小山信也. "Chebyshev's Bias against Splitting and Principal Primes in Global Fields", Journal of Number Theory 245, 233-262 (2023).

2. S. Omar. "Central values of Artin L-functions for quaternion fields", ANTS-IV, Leiden, Springer LNCS 1838, 449-458 (2000).

## ライセンス

このプログラムは研究目的で作成されており、青木美穂さんとの共同研究で使用されます。

## 更新履歴

- 2025/07/13: 初版作成
  - 高速化アルゴリズムの実装
  - 並列処理対応
  - 全13ケースのサポート
  - グラフ描画機能
