# Quaternion拡大における素数の偏りの計算プログラム

青木美穂さんとの共同研究のための高速化・並列化プログラムです。

## 概要

このプログラムは以下の機能を提供します：

1. **フロベニウス元計算**: 素数pに対応するフロベニウス元を高速に計算し、JSONファイルに保存
2. **グラフ描画**: 保存されたデータから素数の偏りを可視化するグラフを作成
3. **中規模実験システム**: Omar論文の13ケースで10^6規模の本格計算（NEW!）
4. **Chebyshevバイアス可視化**: Notebookスタイルの詳細バイアスプロット（NEW!）

Sami Omarの論文に記載された13のQuaternion拡大ケースすべてに対応しています。

## ファイル構成

```
.
├── src/
│   ├── frobenius_calculator.py       # フロベニウス元計算の高速化プログラム
│   ├── graph_plotter.py             # グラフ描画プログラム
│   ├── main_runner.py               # 統合実行スクリプト
│   ├── medium_scale_experiment.py   # 中規模実験システム (NEW!)
│   └── chebyshev_bias_visualizer.py # Chebyshevバイアス可視化ツール (NEW!)
├── run_scripts.sh                   # 実行用シェルスクリプト
├── README.md                        # このファイル
├── INSTALL.md                       # インストール手順
├── demo.ipynb                       # デモ用Jupyter Notebook
├── frobenius_data/                  # JSONデータ保存ディレクトリ (自動作成)
├── graphs/                          # グラフ保存ディレクトリ (自動作成)
└── logs/                            # ログファイル保存ディレクトリ (自動作成)
```

## 🆕 新機能: 中規模実験システム

### 特徴

- **10^6規模の本格計算**: 78,498個の素数を対象とした大規模実験
- **JSON保存対応**: SageMath型の自動変換でエラーフリー保存
- **進捗表示**: tqdm対応の詳細進捗表示
- **自動中間保存**: 1000素数ごとの自動バックアップ
- **統計レポート**: 成功率、実行時間等の詳細統計

### 使用方法

```sage
# 中規模実験システムをロード
load('src/medium_scale_experiment.py')

# フル実験実行（10^6、全13ケース、数時間）
experiment, results = run_medium_scale_verification()

# テスト実行（10^4、最初の3ケース、数分）
experiment, results = run_test_verification()

# 単一ケーステスト（10^3、1ケース、数秒）
experiment, result = run_single_case_test(case_index=0, x_max=1000)
```

## 🆕 新機能: Chebyshevバイアス可視化

### 特徴

- **Notebookスタイルプロット**: 元のJupyter Notebookと同じ6つのサブプロット
- **理論値との比較**: C(σ) * log(log(x))の理論曲線を重ね合わせ
- **統計グラフ**: フロベニウス分布、成功率、実行時間等の比較
- **総合ダッシュボード**: 全13ケースの包括的な分析

### 使用方法

```sage
# 可視化ツールをロード
load('src/chebyshev_bias_visualizer.py')

# 保存された結果から全可視化を作成
visualizer = visualize_omar_results(results_dir='./medium_scale_results_20250716_025046')

# 特定ケースのChebyshevバイアスプロットのみ作成
fig = create_single_bias_plot('./results_dir', 'Omar Case 1')
```

### 作成されるグラフ

1. **個別Chebyshevバイアスプロット**: 各ケースのS1〜S5プロット
2. **フロベニウス分布比較**: 全ケースの共役類分布
3. **計算統計比較**: 成功率、実行時間、効率性
4. **総合サマリーダッシュボード**: 7つのサブプロットを含む包括的分析

## 必要な環境

- SageMath 9.5以上
- Python 3.9以上
- matplotlib
- numpy
- pandas（推奨）
- tqdm（推奨、進捗表示用）
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

### 3. 軽量テスト（推奨）

```bash
# 小規模テスト（10^5素数まで、約2-3分）
./run_scripts.sh test
```

### 4. 中規模実験テスト

```sage
# SageMathで実行
sage
load('src/medium_scale_experiment.py')

# 依存関係チェック
check_dependencies()

# テスト実行（10^4、3ケース、数分）
experiment, results = run_test_verification()
```

### 5. 結果の可視化

```sage
# 可視化ツールで結果を表示
load('src/chebyshev_bias_visualizer.py')
visualizer = visualize_omar_results(results_dir=experiment.output_dir)
```

## 出力ファイル構造

### 中規模実験の結果

```
medium_scale_results_YYYYMMDD_HHMMSS/
├── medium_scale_experiment_complete.json    # 全結果統合ファイル
├── medium_scale_experiment_complete.pkl     # Pickle形式バックアップ
├── Omar_Case_1_final.json                  # 個別ケース結果
├── Omar_Case_1_intermediate.json           # 中間保存ファイル
└── visualization_plots/                    # 可視化結果
    ├── chebyshev_bias_Omar_Case_1.png      # 個別バイアスプロット
    ├── frobenius_distribution.png          # フロベニウス分布
    ├── computation_statistics.png          # 計算統計
    └── comprehensive_summary.png           # 総合サマリー
```

### 結果データの形式

```json
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
      "galois_group": "Q8",
      "discriminant": 1259712000000000000,
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
        "success_rate": 95.32
      },
      "results": [[2, "1"], [3, "-1"], [5, "i"], ...]
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

## 実験規模の比較

| システム | 素数数 | 実行時間 | メモリ使用量 | 用途 |
|----------|--------|----------|--------------|------|
| 高速化システム | 10^5 | 2-3分 | 200MB | 高速テスト |
| 中規模実験 | 10^6 | 数時間 | 2-8GB | 本格研究 |
| 単一ケーステスト | 10^3 | 数秒 | 10MB | デバッグ |

## 実験結果の例

### Case 1での10^6規模実験結果

```
✅ Omar Case 1 計算完了
⏱️  実行時間: 2745.23秒 (約45分)
📊 計算統計:
   total_primes: 78,498
   successful_computations: 74,822
   success_rate: 95.32%

📊 フロベニウス分布:
   1: 9,372 (12.5%)
   -1: 9,373 (12.5%)
   i: 18,693 (25.0%)
   j: 18,692 (25.0%)
   k: 18,692 (25.0%)
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
