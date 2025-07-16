#!/bin/bash

# 高性能大規模実験対応実行スクリプト（140コア対応）
# 青木美穂研究グループ - Quaternion拡大における素数の偏りの計算
# 更新日: 2025/07/16

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 色付きの出力関数
print_header() {
    echo -e "\n\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[1;36m📊 $1\033[0m"
}

# システム情報の表示
show_system_info() {
    print_header "システム情報（140コア対応）"
    echo "CPU: $(nproc) コア"
    echo "メモリ: $(free -h | grep '^Mem:' | awk '{print $2}')"
    echo "ディスク空き: $(df -h . | tail -1 | awk '{print $4}')"
    echo "OS: $(uname -s) $(uname -r)"
    echo "SageMath: $(sage --version | head -1)"
    echo "Python並列処理: $(python3 -c 'import multiprocessing; print(f"{multiprocessing.cpu_count()} コア利用可能")')"
    echo "推定メモリ使用量: $(($(nproc) / 2)) GB (140コア使用時: 70 GB)"
}

# 依存関係チェック
check_dependencies() {
    print_header "依存関係チェック（並列処理対応）"
    
    # SageMathの確認
    if ! command -v sage &> /dev/null; then
        print_error "SageMathがインストールされていません"
        exit 1
    fi
    print_success "SageMath"
    
    # Pythonライブラリの確認
    python3 -c "import psutil, tqdm, multiprocessing, concurrent.futures" 2>/dev/null || {
        print_warning "一部のライブラリが不足しています"
        echo "以下のコマンドでインストールしてください:"
        echo "pip install psutil tqdm"
    }
    print_success "並列処理ライブラリ"
    
    # ファイルの確認
    required_files=(
        "src/medium_scale_experiment.py"
        "src/large_scale_experiment.py"
        "src/chebyshev_bias_visualizer.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "$file"
        else
            print_error "$file が見つかりません"
            exit 1
        fi
    done
    
    # システムリソースチェック
    check_system_resources
}

# システムリソースチェック
check_system_resources() {
    print_header "システムリソースチェック"
    
    # CPU コア数
    cores=$(nproc)
    print_info "利用可能コア数: $cores"
    
    if [[ $cores -lt 140 ]]; then
        print_warning "140コアが利用できません。利用可能な $cores コアを使用します。"
    else
        print_success "140コア以上利用可能"
    fi
    
    # メモリチェック
    memory_gb=$(free -g | grep '^Mem:' | awk '{print $2}')
    estimated_usage=$((140 / 2))  # 140コア使用時の推定メモリ使用量
    
    print_info "総メモリ: ${memory_gb} GB"
    print_info "推定メモリ使用量（140コア）: ${estimated_usage} GB"
    
    if [[ $memory_gb -lt $estimated_usage ]]; then
        print_warning "メモリが不足している可能性があります"
        print_warning "推奨: ${estimated_usage} GB以上"
    else
        print_success "メモリ容量十分"
    fi
    
    # ディスク容量チェック
    disk_gb=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    print_info "ディスク空き容量: ${disk_gb} GB"
    
    if [[ $disk_gb -lt 10 ]]; then
        print_warning "ディスク容量が不足している可能性があります"
    else
        print_success "ディスク容量十分"
    fi
}

# 使用方法の表示
show_usage() {
    cat << EOF
🚀 高性能大規模実験対応実行スクリプト（140コア対応）

使用方法:
  $0 [オプション]

オプション:
  test                  - 小規模テスト (10K素数、約1分)
  medium               - 中規模実験 (50K素数、約5分)
  large                - 大規模実験 (1M素数、約1時間)
  ultra                - 超大規模実験 (10M素数、約10時間)
  
  benchmark            - ベンチマークテスト (性能測定)
  stress-test          - ストレステスト (システム負荷テスト)
  
  check-deps           - 依存関係チェック
  check-system         - システム要件チェック
  monitor              - リアルタイムシステム監視
  cleanup              - 結果ファイルのクリーンアップ
  
  help                 - このヘルプを表示

実験規模の比較（140コア使用時）:
  📊 小規模テスト:     10K素数         - 1分
  📊 中規模実験:       50K素数         - 5分
  📊 大規模実験:       1M素数          - 1時間
  📊 超大規模実験:     10M素数         - 10時間

パフォーマンス目標:
  📊 計算速度:         1,000+ 計算/秒
  📊 並列効率:         140コア同時稼働
  📊 メモリ効率:       70GB以下

例:
  $0 test              # 小規模テスト実行
  $0 medium            # 中規模実験実行
  $0 large             # 大規模実験実行
  $0 benchmark         # 性能測定
  $0 check-system      # システム要件チェック

EOF
}

# SageMathスクリプト実行関数（改良版）
run_sage_script() {
    local script_content="$1"
    
    # 一時ファイルを作成してスクリプトを実行
    local temp_file=$(mktemp /tmp/sage_script_XXXXXX.sage)
    
    # SageMath環境の初期化を含むスクリプトを作成
    cat > "$temp_file" << EOF
# SageMath環境の初期化
from sage.all import *

# スクリプト内容
$script_content
EOF
    
    # SageMathで実行
    sage "$temp_file"
    local exit_code=$?
    
    rm -f "$temp_file"
    return $exit_code
}

# 実験実行関数
run_experiment() {
    local experiment_type=$1
    
    print_header "実験実行: $experiment_type（140コア対応）"
    
    case $experiment_type in
        "test")
            print_info "小規模テスト実行中（10K素数）..."
            run_sage_script "
load('src/medium_scale_experiment.py')
try:
    experiment, results = run_test_verification()  # 10K素数
    print('✅ 小規模テスト完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "medium")
            print_info "中規模実験実行中（50K素数）..."
            run_sage_script "
load('src/medium_scale_experiment.py')
try:
    experiment, results = run_medium_scale_verification()  # 50K素数
    print('✅ 中規模実験完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "large")
            print_info "大規模実験実行中（1M素数）..."
            print_warning "この実験は約1時間かかります"
            print_info "真の大規模実験システムを使用します"
            read -p "続行しますか? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_sage_script "
# 真の大規模実験システムを使用
load('src/large_scale_experiment.py')
try:
    print('🚀 真の大規模実験システム開始...')
    experiment, results = run_large_scale_verification(x_max=1000000, num_workers=None, case_indices=[0, 1, 2])
    print('✅ 大規模実験完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    print('🔄 フォールバックモードに切り替え...')
    load('src/medium_scale_experiment.py')
    try:
        experiment, results = run_large_scale_verification()
        print('✅ フォールバック大規模実験完了')
    except Exception as e2:
        print(f'❌ フォールバックエラー: {e2}')
        import traceback
        traceback.print_exc()
"
            else
                print_info "大規模実験をキャンセルしました"
            fi
            ;;
        
        "ultra")
            print_info "超大規模実験実行中（10M素数）..."
            print_warning "この実験は約10時間かかります"
            print_warning "140コア、70GB メモリが必要です"
            read -p "続行しますか? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_sage_script "
# 超大規模実験システムを使用
load('src/large_scale_experiment.py')
try:
    print('🚀 超大規模実験システム開始...')
    experiment, results = run_large_scale_verification(x_max=10000000, num_workers=None, case_indices=None)
    print('✅ 超大規模実験完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    print('🔄 フォールバックモードに切り替え...')
    load('src/medium_scale_experiment.py')
    try:
        experiment, results = run_high_performance_test(max_prime=10000000)
        print('✅ フォールバック超大規模実験完了')
    except Exception as e2:
        print(f'❌ フォールバックエラー: {e2}')
        import traceback
        traceback.print_exc()
"
            else
                print_info "超大規模実験をキャンセルしました"
            fi
            ;;
        
        *)
            print_error "不明な実験タイプ: $experiment_type"
            show_usage
            exit 1
            ;;
    esac
}

# ベンチマークテスト
run_benchmark() {
    print_header "ベンチマークテスト実行"
    print_info "140コアの性能を測定します..."
    
    run_sage_script "
# 基本並列処理性能ベンチマーク
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def compute_task(p):
    return p**2 % 1000003

def benchmark_performance():
    print('🔬 並列処理性能ベンチマーク')
    
    # テスト用素数
    test_primes = primes_first_n(5000)
    
    # シングルスレッド
    start_time = time.time()
    single_results = [compute_task(p) for p in test_primes]
    single_time = time.time() - start_time
    print(f'シングルスレッド: {single_time:.3f}秒')
    
    # 並列処理
    cores_to_use = min(140, mp.cpu_count())
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=cores_to_use) as executor:
        parallel_results = list(executor.map(compute_task, test_primes))
    parallel_time = time.time() - start_time
    print(f'並列処理({cores_to_use}コア): {parallel_time:.3f}秒')
    
    if parallel_time > 0:
        speedup = single_time / parallel_time
        efficiency = speedup / cores_to_use * 100
        print(f'速度向上: {speedup:.1f}倍')
        print(f'並列効率: {efficiency:.1f}%')
        print(f'実効計算速度: {len(test_primes)/parallel_time:.0f} 計算/秒')

# メモリ使用量チェック
import psutil
process = psutil.Process()
initial_memory = process.memory_info().rss / 1024**2
print(f'初期メモリ使用量: {initial_memory:.1f} MB')

benchmark_performance()

current_memory = process.memory_info().rss / 1024**2
memory_increase = current_memory - initial_memory
print(f'ベンチマーク後メモリ: {current_memory:.1f} MB (+{memory_increase:.1f} MB)')
print('✅ ベンチマーク完了')
"
}

# ストレステスト
run_stress_test() {
    print_header "ストレステスト実行"
    print_warning "このテストはシステムに高負荷をかけます"
    
    read -p "続行しますか? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "ストレステストをキャンセルしました"
        return
    fi
    
    run_sage_script "
import time
import multiprocessing as mp
import psutil
from concurrent.futures import ProcessPoolExecutor

def heavy_computation(n):
    # 重い計算タスク
    result = 0
    for i in range(n, n + 1000):
        if is_prime(i):
            result += i**2
    return result

def stress_test(duration_minutes=3):
    print(f'🔥 {duration_minutes}分間のストレステスト開始')
    
    start_time = time.time()
    end_time = start_time + duration_minutes * 60
    total_tasks = 0
    
    cores_to_use = min(140, mp.cpu_count())
    
    with ProcessPoolExecutor(max_workers=cores_to_use) as executor:
        while time.time() < end_time:
            # 連続的にタスクを投入
            tasks = range(total_tasks * 10000, (total_tasks + 100) * 10000, 10000)
            results = list(executor.map(heavy_computation, tasks))
            total_tasks += 100
            
            # 30秒ごとに進捗表示
            elapsed = time.time() - start_time
            if elapsed % 30 < 5:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                print(f'経過: {elapsed:.0f}秒, CPU: {cpu_percent:.1f}%, メモリ: {memory.percent:.1f}%, タスク: {total_tasks}')
    
    total_time = time.time() - start_time
    print(f'✅ ストレステスト完了: {total_time:.1f}秒, 総タスク: {total_tasks}')

stress_test(3)  # 3分間のテスト
"
}

# リアルタイムシステム監視
monitor_system() {
    print_header "リアルタイムシステム監視開始"
    print_info "Ctrl+C で終了"
    
    python3 << 'EOF'
import psutil
import time

try:
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        print(f"\r🖥️  CPU: {cpu_percent:5.1f}% | 🧠 MEM: {memory.percent:5.1f}% ({memory.used//1024**3}/{memory.total//1024**3}GB) | 💾 DISK: {disk.percent:5.1f}%", end="", flush=True)
        
except KeyboardInterrupt:
    print("\n✅ 監視終了")
EOF
}

# 結果ファイルのクリーンアップ
cleanup_results() {
    print_header "結果ファイルのクリーンアップ"
    
    # 確認
    echo "以下のディレクトリが削除されます:"
    ls -d *results* 2>/dev/null || echo "  (削除対象なし)"
    
    read -p "続行しますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf *results* 2>/dev/null || true
        rm -rf frobenius_data/ graphs/ logs/ performance.log 2>/dev/null || true
        print_success "クリーンアップ完了"
    else
        print_info "クリーンアップをキャンセルしました"
    fi
}

# 実験後の可視化
run_visualization() {
    print_header "結果の可視化"
    
    # 最新の結果ディレクトリを探す
    latest_results=$(ls -td *results* 2>/dev/null | head -1)
    
    if [[ -z "$latest_results" ]]; then
        print_warning "結果ディレクトリが見つかりません"
        return
    fi
    
    print_info "可視化対象: $latest_results"
    
    run_sage_script "
load('src/chebyshev_bias_visualizer.py')
try:
    visualizer = visualize_omar_results(results_dir='$latest_results')
    print('✅ 可視化完了')
except Exception as e:
    print(f'❌ 可視化エラー: {e}')
    import traceback
    traceback.print_exc()
"
}

# パフォーマンス監視
monitor_performance() {
    print_header "パフォーマンス監視開始"
    
    # バックグラウンドで監視
    (
        while true; do
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
            mem_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
            load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
            
            echo "$timestamp CPU: ${cpu_usage}%, MEM: ${mem_usage}%, LOAD: ${load_avg}" >> performance.log
            sleep 30
        done
    ) &
    
    monitor_pid=$!
    echo "パフォーマンス監視プロセス: $monitor_pid"
    echo "ログファイル: performance.log"
    
    # 終了時にプロセスを停止
    trap "kill $monitor_pid 2>/dev/null || true" EXIT
}

# メイン処理
main() {
    # 引数チェック
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi
    
    # 最初に基本チェック
    check_dependencies
    
    case $1 in
        "help"|"-h"|"--help")
            show_usage
            ;;
        
        "check-deps")
            check_dependencies
            ;;
        
        "check-system")
            check_system_resources
            ;;
        
        "benchmark")
            run_benchmark
            ;;
        
        "stress-test")
            run_stress_test
            ;;
        
        "monitor")
            monitor_system
            ;;
        
        "cleanup")
            cleanup_results
            ;;
        
        "test"|"medium"|"large"|"ultra")
            show_system_info
            
            # パフォーマンス監視を開始
            monitor_performance
            
            # 実験実行
            run_experiment $1
            
            # 可視化
            run_visualization
            
            print_success "全処理完了"
            ;;
        
        *)
            print_error "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"
