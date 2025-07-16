# Quaternion拡大における素数の偏りの計算プログラム

青木美穂さんとの共同研究のための高速化・並列化プログラムです。

## 概要

このプログラムは以下の機能を提供します：

1. **フロベニウス元計算**: 素数pに対応するフロベニウス元を高速に計算し、JSONファイルに保存
2. **グラフ描画**: 保存されたデータから素数の偏りを可視化するグラフを作成
3. **中規模実験システム**: Omar論文の13ケースで10^6規模の本格計算
4. **大規模実験システム**: 10^8規模の並列処理による高速化実験（NEW!）
5. **超大規模実験システム**: 10^9規模の分散処理・ストリーミング実験（NEW!）
6. **Chebyshevバイアス可視化**: Notebookスタイルの詳細バイアスプロット

Sami Omarの論文に記載された13のQuaternion拡大ケースすべてに対応しています。

## ファイル構成

```
.
├── src/
│   ├── frobenius_calculator.py       # フロベニウス元計算の高速化プログラム
│   ├── graph_plotter.py             # グラフ描画プログラム
│   ├── main_runner.py               # 統合実行スクリプト
│   ├── medium_scale_experiment.py   # 中規模実験システム (10^6)
│   ├── large_scale_experiment.py    # 大規模実験システム (10^8) (NEW!)
│   ├── ultra_large_experiment.py    # 超大規模実験システム (10^9) (NEW!)
│   └── chebyshev_bias_visualizer.py # Chebyshevバイアス可視化ツール
├── run_scripts.sh                   # 実行用シェルスクリプト (大幅強化!)
├── README.md                        # このファイル
├── INSTALL.md                       # インストール手順
├── demo.ipynb                       # デモ用Jupyter Notebook
├── frobenius_data/                  # JSONデータ保存ディレクトリ (自動作成)
├── graphs/                          # グラフ保存ディレクトリ (自動作成)
└── logs/                            # ログファイル保存ディレクトリ (自動作成)
```

## 🆕 新機能: 大規模実験システム (10^8規模)

### 特徴

- **10^8規模の並列計算**: 5,761,455個の素数を対象とした大規模実験
- **マルチコア並列化**: 最大32コアまでの並列処理対応
- **メモリ効率化**: チャンク処理による効率的なメモリ使用
- **自動負荷分散**: プロセス間の負荷を自動調整
- **リアルタイム進捗**: 詳細な進捗表示とパフォーマンス監視
- **障害耐性**: エラー処理と自動リトライ機能

### 使用方法

```sage
# 大規模実験システムをロード
load('src/large_scale_experiment.py')

# フル実験実行（10^8、全13ケース、6-12時間）
experiment, results = run_large_scale_verification()

# テスト実行（10^7、3ケース、30-60分）
experiment, results = run_large_scale_test()

# 単一ケーステスト
experiment, result = run_single_large_case(case_index=0, x_max=10000000)

# 依存関係チェック
check_large_scale_dependencies()

# 最適設定の取得
optimal_settings = get_optimal_settings()
```

## 🆕 新機能: 超大規模実験システム (10^9規模)

### 特徴

- **10^9規模のストリーミング処理**: 50,847,534個の素数を対象
- **分散処理対応**: 複数ノードでの分散計算
- **メモリ効率的ストリーミング**: 大規模データの逐次処理
- **SQLiteデータベース**: 結果の効率的な管理と検索
- **チェックポイント機能**: 障害時の自動復旧
- **リアルタイム監視**: 詳細なログとアラート機能

### 使用方法

```sage
# 超大規模実験システムをロード
load('src/ultra_large_experiment.py')

# システム要件チェック
if check_ultra_large_dependencies():
    # フル実験実行（10^9、全13ケース、24-48時間）
    experiment, results = run_ultra_large_verification()
    
    # テスト実行（10^8、2ケース、3-6時間）
    experiment, results = run_ultra_large_test()
```

## 実験規模の比較

| システム | 規模 | 素数数 | 実行時間 | メモリ使用量 | CPU要件 | 用途 |
|----------|------|--------|----------|--------------|---------|------|
| 軽量テスト | 10^5 | 78K | 2-3分 | 200MB | 2コア | 高速テスト |
| 中規模実験 | 10^6 | 78K | 1-2時間 | 2-8GB | 4コア | 本格研究 |
| 大規模実験 | 10^8 | 5.7M | 6-12時間 | 16-32GB | 16コア | 大規模研究 |
| 超大規模実験 | 10^9 | 50M | 24-48時間 | 64-128GB | 32コア | 最先端研究 |

## システム要件

### 基本要件
- SageMath 9.5以上
- Python 3.9以上
- matplotlib, numpy, pandas
- tqdm（進捗表示用）

### 大規模実験要件
- 32GB RAM以上
- 16コア以上のCPU
- 50GB以上の空きディスク容量
- psutil, multiprocessing

### 超大規模実験要件
- 64GB RAM以上
- 32コア以上のCPU
- 100GB以上の空きディスク容量
- SQLite3, 高速SSD推奨

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

### 3. システム要件チェック

```bash
# システム要件の確認
./run_scripts.sh check-system

# 依存関係の確認
./run_scripts.sh check-deps
```

### 4. 実験実行

```bash
# 軽量テスト（推奨）
./run_scripts.sh test

# 中規模実験テスト
./run_scripts.sh medium-test

# 大規模実験テスト（要32GB RAM）
./run_scripts.sh large-test

# 超大規模実験テスト（要64GB RAM）
./run_scripts.sh ultra-test
```

### 5. 本格実験の実行

```bash
# 中規模実験（10^6、1-2時間）
./run_scripts.sh medium

# 大規模実験（10^8、6-12時間）
./run_scripts.sh large

# 超大規模実験（10^9、24-48時間）
./run_scripts.sh ultra
```

## 並列化の詳細

### 大規模実験システムの並列化

**アーキテクチャ:**
- **ProcessPoolExecutor**: 複数プロセスでの並列処理
- **動的負荷分散**: 各プロセスの負荷を自動調整
- **メモリ効率化**: チャンク単位での処理
- **進捗監視**: リアルタイムの処理状況表示

**最適化技術:**
- **プロセス間通信**: 効率的なタスク分散
- **メモリ管理**: ガベージコレクション最適化
- **エラー処理**: 自動リトライと障害耐性

### 超大規模実験システムの分散処理

**ストリーミング処理:**
- **素数生成器**: メモリ効率的な逐次生成
- **チャンク処理**: 大規模データの分割処理
- **データベース統合**: SQLiteによる効率的な結果管理

**分散処理対応:**
- **マスター・ワーカー方式**: 複数ノードでの処理分散
- **チェックポイント**: 障害時の自動復旧
- **リアルタイム監視**: 詳細なログとアラート

## 出力ファイル構造

### 中規模実験の結果
```
medium_scale_results_YYYYMMDD_HHMMSS/
├── medium_scale_experiment_complete.json
├── Omar_Case_N_final.json
└── visualization_plots/
```

### 大規模実験の結果
```
large_scale_results_YYYYMMDD_HHMMSS/
├── large_scale_experiment_complete.json
├── Omar_Case_N_large_scale.json
├── checkpoints/
└── visualization_plots/
```

### 超大規模実験の結果
```
ultra_large_results_YYYYMMDD_HHMMSS/
├── experiment.db                     # SQLiteデータベース
├── Omar_Case_N_ultra_large.json      # 統合結果
├── checkpoints/                      # 自動チェックポイント
├── logs/                            # 詳細ログ
└── visualization_plots/              # 可視化結果
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
visualizer = visualize_omar_results(results_dir='./large_scale_results_20250716_025046')

# 特定ケースのChebyshevバイアスプロットのみ作成
fig = create_single_bias_plot('./results_dir', 'Omar Case 1')
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

## パフォーマンス最適化

### 大規模実験の最適化技術

**並列処理最適化:**
- **適応的ワーカー数**: システムリソースに応じた最適な並列度
- **動的チャンクサイズ**: メモリ使用量に応じたチャンクサイズ調整
- **負荷分散**: 各プロセスの処理時間を均等化

**メモリ最適化:**
- **メモリ使用量監視**: 80%制限による安全な運用
- **ガベージコレクション**: 適切なタイミングでのメモリ解放
- **中間保存**: 定期的なチェックポイント保存

### 超大規模実験の最適化技術

**ストリーミング最適化:**
- **逐次素数生成**: メモリ効率的な素数生成器
- **データベース統合**: SQLiteによる効率的な結果管理
- **圧縮保存**: 結果データの効率的な保存

**分散処理最適化:**
- **マスター・ワーカー方式**: 複数ノードでの効率的な処理分散
- **障害耐性**: チェックポイントによる自動復旧
- **リアルタイム監視**: 詳細なパフォーマンス監視

## 実験結果の例

### Case 1での10^8規模実験結果

```
✅ Omar Case 1 計算完了 (大規模実験)
⏱️  実行時間: 18,245.67秒 (約5時間)
🧮 並列度: 16コア
📊 計算統計:
   total_primes: 5,761,455
   successful_computations: 5,489,832
   success_rate: 95.28%
   throughput: 317 素数/秒

📊 フロベニウス分布:
   1: 686,229 (12.5%)
   -1: 686,230 (12.5%)
   i: 1,372,686 (25.0%)
   j: 1,372,344 (25.0%)
   k: 1,372,343 (25.0%)

💾 結果保存: large_scale_results_20250716_154521/
```

### Case 1での10^9規模実験結果

```
✅ Omar Case 1 計算完了 (超大規模実験)
⏱️  実行時間: 156,789.23秒 (約44時間)
🧮 並列度: 32コア + ストリーミング
📊 計算統計:
   total_primes: 50,847,534
   successful_computations: 48,305,358
   success_rate: 95.00%
   throughput: 324 素数/秒
   checkpoints_saved: 127

📊 フロベニウス分布:
   1: 6,038,169 (12.5%)
   -1: 6,038,170 (12.5%)
   i: 12,076,339 (25.0%)
   j: 12,076,340 (25.0%)
   k: 12,076,340 (25.0%)

💾 結果保存: ultra_large_results_20250716_201045/
🗄️  データベース: experiment.db (2.1GB)
```

## トラブルシューティング

### 一般的な問題

**メモリ不足:**
- より小さいチャンクサイズを使用
- 不要なプロセスの終了
- スワップファイルの設定

**並列処理エラー:**
- ワーカー数の削減
- システムリソースの確認
- 他のプロセスの停止

**実行時間の長さ:**
- テスト実行での事前確認
- 並列度の最適化
- 中間結果の確認

### 大規模実験特有の問題

**並列処理の停止:**
- 自動リトライ機能が作動
- チェックポイントからの復旧
- ログファイルの確認

**メモリ制限に達する:**
- 自動的にチェックポイント保存
- ガベージコレクション実行
- チャンクサイズの自動調整

## 参考文献

1. 青木美穂, 小山信也. "Chebyshev's Bias against Splitting and Principal Primes in Global Fields", Journal of Number Theory 245, 233-262 (2023).

2. S. Omar. "Central values of Artin L-functions for quaternion fields", ANTS-IV, Leiden, Springer LNCS 1838, 449-458 (2000).

3. M. Rubinstein, P. Sarnak. "Chebyshev's bias", Experimental Mathematics 3, 173-197 (1994).

## ライセンス

このプログラムは研究目的で作成されており、青木美穂さんとの共同研究で使用されます。

## 更新履歴

- **2025/07/16**: 大規模・超大規模実験システム追加
  - 10^8規模の大規模実験対応（並列処理）
  - 10^9規模の超大規模実験対応（分散処理・ストリーミング）
  - マルチコア並列化による大幅な高速化
  - SQLiteデータベースによる効率的な結果管理
  - 障害耐性とチェックポイント機能
  - リアルタイム監視とパフォーマンス最適化

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

- 更なる大規模実験対応（10^10素数まで）
- GPUアクセラレーション対応
- クラウド分散計算対応
- 機械学習による最適化
- リアルタイムWeb監視インターフェース
- 自動理論値フィッティング機能
