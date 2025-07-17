# Jupyter環境での実行手順 (修正版)

このファイルでは、Jupyter環境でbias_with_claudeプロジェクトを実行する手順を説明します。

## ✅ 修正済みの項目

- **legendre_symbol関数のインポートエラー**: Python互換版に修正
- **SageMathのRational型フォーマットエラー**: float型変換で解決
- **依存関係の問題**: SymPy/Pythonのみで動作するよう修正

## 🚀 クイックスタート

### 1. 必要なライブラリのインストール

```python
import sys
import subprocess

# 必要なライブラリをインストール
libraries = ['matplotlib', 'numpy', 'sympy', 'tqdm']
for lib in libraries:
    try:
        __import__(lib)
        print(f"✓ {lib} is available")
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
        print(f"✓ {lib} installed successfully")
```

### 2. プロジェクト構造の作成

```python
import os

# プロジェクトディレクトリの作成
project_dirs = ['src', 'frobenius_data', 'graphs', 'logs']
for dir_name in project_dirs:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"Created directory: {dir_name}")
```

### 3. Python版ファイルの使用

修正版では以下のPython互換ファイルを使用してください：

- `src/frobenius_calculator_python.py`: Python/SymPy版フロベニウス計算器
- `src/graph_plotter_python.py`: Python/matplotlib版グラフ描画器

### 4. 基本的な実行例

```python
# frobenius_calculator_python.pyをインポート
sys.path.append('./src')
from frobenius_calculator_python import OMAR_POLYNOMIALS, compute_frobenius_elements_sequential, save_frobenius_data

# Case 1のテスト実行
case_info = OMAR_POLYNOMIALS[0]  # Case 1
frobenius_data = compute_frobenius_elements_sequential(case_info, max_prime=10**4)
save_frobenius_data(case_info, frobenius_data)

print(f"計算完了: {len(frobenius_data)} 個の素数を処理")
```

### 5. グラフの作成と表示

```python
from graph_plotter_python import BiasAnalyzer
from IPython.display import Image, display

# 解析器を初期化
analyzer = BiasAnalyzer(data_dir="frobenius_data")

# Case 1のグラフを作成
analyzer.plot_bias_graphs(case_id=1, max_x=None, target_points=300)

# グラフを表示
display(Image('graphs/case_01_bias_graphs.png'))
```

## 📊 期待される結果

### Case 1 (m_ρ₀ = 0)
- **g0 (1)**: ~24% (理論値12.5%より多い)
- **g1 (-1)**: 0% (理論値12.5%より大幅に少ない)
- **g2-g4 (i,j,k)**: 各~25% (理論値に近い)

### Chebyshevバイアスの確認
- **S1**: +0.5 log(log(x))の正のバイアス
- **S2**: +2.5 log(log(x))の強い正のバイアス  
- **S3-S5**: -0.5 log(log(x))の負のバイアス

## 🔧 トラブルシューティング

### エラー: "legendre_symbol not found"
```python
# 修正版では独自実装を使用
def legendre_symbol_simple(a, p):
    if not isprime(p):
        return 1
    if a % p == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return -1 if result == p - 1 else result
```

### エラー: "Rational.__format__"
```python
# floatで明示的に変換
percentage = float(count) / float(total_primes) * 100
```

## 📁 生成されるファイル

- `frobenius_data/case_01_frobenius.json`: フロベニウス元計算結果
- `graphs/case_01_bias_graphs.png`: 偏りグラフ（5つのサブプロット）
- `frobenius_analysis_results.csv`: 分析結果のまとめ

## 🎯 次のステップ

1. **より大規模な計算**: `max_prime=10**5` または `10**6` で実行
2. **全ケースの実行**: OMAR_POLYNOMIALS[0:3] で Case 1-3 を実行
3. **理論値との詳細比較**: 偏り係数の定量的検証
4. **統計的有意性検証**: より多くの素数での検証

## 📖 参考文献

- 青木美穂, 小山信也. "Chebyshev's Bias against Splitting and Principal Primes in Global Fields", Journal of Number Theory 245, 233-262 (2023)
- S. Omar. "Central values of Artin L-functions for quaternion fields", ANTS-IV (2000)

## 🆕 更新履歴

- **2025/07/17**: Python互換版に修正、エラー解決
- SageMath依存を除去し、Jupyter環境で完全動作
- legendre_symbol関数の独自実装
- フォーマットエラーの修正
