{
  "experiment_info": {
    "title": "Omar's 13 Cases Medium Scale Verification",
    "x_max": 1000000,
    "total_cases": 13,
    "experiment_duration": 28800.5,
    "timestamp": "2025-07-16T02:50:46"
  },
  "results": {
    "Omar Case 1": {
      "case_name": "Omar Case 1",
      "polynomial": "x^8 - x^7 - 34*x^6 + ...",
      "m_rho_0_val": 0,
      "x_max": 1000000,
      "galois_group": "Q8",
      "discriminant": 1259712000000000000,
      "subfield_discriminants": [5, 21, 105],
      "total_bias_coeffs": {
        "1": 0.5,
        "-1": 2.5,
        "i": -0.5,
        "j": -0.5,
        "k": -0.5
      },
      "computation_stats": {
        "total_primes": 78498,
        "successful_computations": 74822,
        "skipped_bad_reduction": 3,
        "unknown_patterns": 156,
        "errors": 3517
      },
      "execution_time": 2745.23,
      "success_rate": 95.32,
      "results": [
        [2, "1"],
        [3, "-1"],
        [5, "i"],
        ...
      ]
    }
  }
}
```

## 理論的背景

### 偏りの公式（深リーマン予想下）

各フロベニウス元σに対して：

```
S_σ(x) = π_{1/2}(x) - |Gal(L/Q)|/|c_σ| × π_{1/2}(x; σ) 
        = (M(σ) + m(σ)) log log x + c + o(1)
```

### Chebyshevバイアスの理論値

**m_ρ0 = 0の場合 (Case 1, 5, 11):**
- S1 = π_½(x) - 8π_½(x; 1): 理論値 = **0.5** × log(log(x))
- S2 = π_½(x) - 8π_½(x; -1): 理論値 = **2.5** × log(log(x))
- S3 = π_½(x) - 4π_½(x; i): 理論値 = **-0.5** × log(log(x))
- S4 = π_½(x) - 4π_½(x; j): 理論値 = **-0.5** × log(log(x))
- S5 = π_½(x) - 4π_½(x; k): 理論値 = **-0.5** × log(log(x))

**m_ρ0 = 1の場合 (Case 2-4, 6-10, 12-13):**
- S1: 理論値 = **2.5** × log(log(x))
- S2: 理論値 = **0.5** × log(log(x))
- S3, S4, S5: 理論値 = **-0.5** × log(log(x))

## 高速化の仕組み

### 1. アルゴリズムの最適化

従来の素朴なSage関数呼び出しを以下の手法で高速化：

- **ルジャンドル記号による分類**: 部分体での分解の様子を効率的に判定
- **mod p因数分解**: 定義多項式の最高次数(1, 2, 4)による迅速な分類
- **共役類構造の利用**: Quaternion群Q8の構造を活用した効率的な分類

### 2. 並列処理と大容量対応

- **マルチコア対応**: 利用可能な全CPUコアで素数範囲を分割処理
- **メモリ効率**: バッチ処理と中間保存による安定した大容量計算
- **エラー回復**: 計算エラーに対する堅牢な処理機構

### 3. JSON保存の最適化

- **SageMath型変換**: Integer, Rational等の自動Python型変換
- **フォールバック機能**: JSON失敗時のPickle自動保存
- **デバッグ機能**: 詳細なエラー追跡とログ出力

## 実験結果の例

### Case 1での10^6規模実験結果

```
✅ Omar Case 1 計算完了
⏱️  実行時間: 2745.23秒 (約45分)
📊 計算統計:
   total_primes: 78,498
   successful_computations: 74,822
   skipped_bad_reduction: 3
   unknown_patterns: 156
   errors: 3,517
🎯 成功率: 95.32%

📊 フロベニウス分布:
   1: 9,372 (12.5%)
   -1: 9,373 (12.5%)
   i: 18,693 (25.0%)
   j: 18,692 (25.0%)
   k: 18,692 (25.0%)
```

### 理論値との比較

Chebyshevバイアスプロットにより、数値実験結果が理論予測 `C(σ) × log(log(x))` と良い一致を示すことが確認できます。

## トラブルシューティング

### 中規模実験でのよくある問題

**1. メモリ不足**
```
MemoryError: Unable to allocate array
```
対処法: 
- `x_max=10**5` で実行
- システムのRAMを確認（推奨16GB以上）

**2. JSON保存エラー**
```
TypeError: Object of type Integer is not JSON serializable
```
対処法: 自動修正済み、最新版を使用

**3. 長時間実行の中断**
```
KeyboardInterrupt
```
対処法: 中間保存ファイルから復旧可能

### デバッグ手順

**1. 依存関係確認**
```sage
load('src/medium_scale_experiment.py')
check_dependencies()
```

**2. 単一ケーステスト**
```sage
experiment, result = run_single_case_test(case_index=0, x_max=1000)
```

**3. JSON変換テスト**
```sage
test_json_conversion()
```

## 研究への応用

### 1. 新しいケースの追加

```python
# medium_scale_experiment.py の _initialize_omar_cases に追加
{
    'name': 'Omar Case 14',
    'poly': 'x^8 + ...',  # 新しい8次多項式
    'm_rho_0': 0,  # または1
    'description': 'New quaternion field case'
}
```

### 2. カスタム分析

```sage
# 特定の共役類のみ分析
case_result = results['Omar Case 1']
i_primes = [p for p, cc in case_result['results'] if cc == 'i']
print("i類の素数: {}個".format(len(i_primes)))

# 素数分布の詳細分析
import numpy as np
x_values = [p for p, cc in case_result['results']]
max_prime = max(x_values)
loglog_max = np.log(np.log(max_prime))
print("log(log({})) = {:.3f}".format(max_prime, loglog_max))
```

### 3. 理論値の検証

```sage
# S値の計算と理論値との比較
def calculate_s_values(frobenius_results):
    sums = {'1': 0, '-1': 0, 'i': 0, 'j': 0, 'k': 0}
    for p, cc in frobenius_results:
        sums[cc] += 1.0 / np.sqrt(p)
    
    pi_half = sum(sums.values())
    S1 = pi_half - 8 * sums['1']
    S2 = pi_half - 8 * sums['-1']
    S3 = pi_half - 4 * sums['i']
    S4 = pi_half - 4 * sums['j']
    S5 = pi_half - 4 * sums['k']
    
    return {'S1': S1, 'S2': S2, 'S3': S3, 'S4': S4, 'S5': S5}

# 使用例
s_vals = calculate_s_values(case_result['results'])
theory_s1 = 0.5 * np.log(np.log(max_prime))  # Case 1の理論値
print("S1 観測値: {:.3f}, 理論値: {:.3f}".format(s_vals['S1'], theory_s1))
```

## Jupyter Notebook環境での使用

### 1. リポジトリのセットアップ

```python
# Jupyter Notebookのセルで実行
!git clone https://github.com/jxta/bias_with_claude.git
%cd bias_with_claude

# SageMathカーネルで実行
load('src/medium_scale_experiment.py')
load('src/chebyshev_bias_visualizer.py')
```

### 2. 軽量実験とライブ可視化

```python
# 軽量テスト実行
experiment, results = run_test_verification(x_max=5000)

# 即座に可視化
visualizer = visualize_omar_results(results_dir=experiment.output_dir)

# 特定ケースの詳細表示
%matplotlib inline
fig = visualizer.create_chebyshev_bias_plot('Omar Case 1')
```

### 3. 進捗モニタリング

```python
# 中間結果の確認
import os
import glob

# 中間保存ファイルを監視
intermediate_files = glob.glob(experiment.output_dir + "/*intermediate.json")
for file in intermediate_files:
    print("中間保存: {}".format(os.path.basename(file)))
```

## 参考文献

1. 青木美穂, 小山信也. "Chebyshev's Bias against Splitting and Principal Primes in Global Fields", Journal of Number Theory 245, 233-262 (2023).

2. S. Omar. "Central values of Artin L-functions for quaternion fields", ANTS-IV, Leiden, Springer LNCS 1838, 449-458 (2000).

3. M. Rubinstein, P. Sarnak. "Chebyshev's bias", Experimental Mathematics 3, 173-197 (1994).

## ライセンス

このプログラムは研究目的で作成されており、青木美穂さんとの共同研究で使用されます。

## 更新履歴

- **2025/07/16**: 中規模実験システム追加
  - 10^6規模の本格実験対応
  - SageMath型の自動JSON変換
  - Chebyshevバイアス可視化ツール
  - Notebookスタイルプロット対応
  - 統計分析ダッシュボード

- **2025/07/13**: 初版作成
  - 高速化アルゴリズムの実装
  - 並列処理対応
  - 全13ケースのサポート
  - グラフ描画機能

## 今後の開発予定

- 更なる大規模実験対応（10^7素数まで）
- 分散計算対応
- リアルタイム進捗Web表示
- 自動理論値フィッティング機能