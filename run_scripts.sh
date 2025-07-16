#!/bin/bash

# 大規模・超大規模実験対応実行スクリプト
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
    print_header "システム情報"
    echo "CPU: $(nproc) コア"
    echo "メモリ: $(free -h | grep '^Mem:' | awk '{print $2}')"
    echo "ディスク空き: $(df -h . | tail -1 | awk '{print $4}')"
    echo "OS: $(uname -s) $(uname -r)"
    echo "SageMath: $(sage --version | head -1)"
}

# 依存関係チェック
check_dependencies() {
    print_header "依存関係チェック"
    
    # SageMathの確認
    if ! command -v sage &> /dev/null; then
        print_error "SageMathがインストールされていません"
        exit 1
    fi
    print_success "SageMath"
    
    # Pythonライブラリの確認
    python3 -c "import psutil, tqdm, numpy" 2>/dev/null || {
        print_warning "一部のライブラリが不足しています"
        echo "以下のコマンドでインストールしてください:"
        echo "pip install psutil tqdm numpy"
    }
    
    # ファイルの確認
    required_files=(
        "src/frobenius_calculator.py"
        "src/medium_scale_experiment.py"
        "src/large_scale_experiment.py"
        "src/ultra_large_experiment.py"
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
}

# 使用方法の表示
show_usage() {
    cat << EOF
🚀 大規模・超大規模実験対応実行スクリプト

使用方法:
  $0 [オプション]

オプション:
  test                  - 軽量テスト (10^5規模、約2-3分)
  medium               - 中規模実験 (10^6規模、約1-2時間)
  large                - 大規模実験 (10^8規模、約6-12時間)
  ultra                - 超大規模実験 (10^9規模、約24-48時間)
  
  medium-test          - 中規模テスト (10^4規模、約3-5分)
  large-test           - 大規模テスト (10^7規模、約30-60分)
  ultra-test           - 超大規模テスト (10^8規模、約3-6時間)
  
  single-case [N]      - 単一ケーステスト (N=0-12)
  check-deps           - 依存関係チェック
  check-system         - システム要件チェック
  cleanup              - 結果ファイルのクリーンアップ
  
  help                 - このヘルプを表示

実験規模の比較:
  📊 軽量テスト:     10^5 (78K素数)      - 数分
  📊 中規模実験:     10^6 (78K素数)      - 1-2時間
  📊 大規模実験:     10^8 (5.7M素数)     - 6-12時間
  📊 超大規模実験:   10^9 (50M素数)      - 24-48時間

システム要件:
  📊 軽量テスト:     2GB RAM, 2コア
  📊 中規模実験:     8GB RAM, 4コア
  📊 大規模実験:     32GB RAM, 16コア
  📊 超大規模実験:   64GB RAM, 32コア

例:
  $0 test              # 軽量テスト実行
  $0 medium-test       # 中規模テスト実行
  $0 large             # 大規模実験実行
  $0 single-case 0     # Omar Case 1のテスト
  $0 check-system      # システム要件チェック

EOF
}

# システム要件チェック
check_system_requirements() {
    print_header "システム要件チェック"
    
    # メモリチェック
    memory_gb=$(free -g | grep '^Mem:' | awk '{print $2}')
    cpu_cores=$(nproc)
    disk_gb=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    
    print_info "現在のシステム:"
    echo "  CPU: ${cpu_cores} コア"
    echo "  メモリ: ${memory_gb} GB"
    echo "  ディスク空き: ${disk_gb} GB"
    
    # 各規模の要件チェック
    echo
    print_info "実験規模別要件チェック:"
    
    # 軽量テスト
    if [[ $memory_gb -ge 2 && $cpu_cores -ge 2 ]]; then
        print_success "軽量テスト (10^5): 実行可能"
    else
        print_warning "軽量テスト (10^5): 要件不足"
    fi
    
    # 中規模実験
    if [[ $memory_gb -ge 8 && $cpu_cores -ge 4 ]]; then
        print_success "中規模実験 (10^6): 実行可能"
    else
        print_warning "中規模実験 (10^6): 要件不足"
    fi
    
    # 大規模実験
    if [[ $memory_gb -ge 32 && $cpu_cores -ge 16 ]]; then
        print_success "大規模実験 (10^8): 実行可能"
    else
        print_warning "大規模実験 (10^8): 要件不足 (32GB RAM, 16コア推奨)"
    fi
    
    # 超大規模実験
    if [[ $memory_gb -ge 64 && $cpu_cores -ge 32 && $disk_gb -ge 100 ]]; then
        print_success "超大規模実験 (10^9): 実行可能"
    else
        print_warning "超大規模実験 (10^9): 要件不足 (64GB RAM, 32コア, 100GB空き推奨)"
    fi
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
        rm -rf frobenius_data/ graphs/ logs/ 2>/dev/null || true
        print_success "クリーンアップ完了"
    else
        print_info "クリーンアップをキャンセルしました"
    fi
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
    local case_index=$2
    
    print_header "実験実行: $experiment_type"
    
    case $experiment_type in
        "test")
            print_info "軽量テスト実行中..."
            run_sage_script "
load('src/frobenius_calculator.py')
try:
    experiment, results = run_quick_test()
    print('✅ 軽量テスト完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "medium")
            print_info "中規模実験実行中 (10^6規模)..."
            run_sage_script "
load('src/medium_scale_experiment.py')
try:
    check_dependencies()
    experiment, results = run_medium_scale_verification()
    print('✅ 中規模実験完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "medium-test")
            print_info "中規模テスト実行中 (10^4規模)..."
            run_sage_script "
load('src/medium_scale_experiment.py')
try:
    check_dependencies()
    experiment, results = run_test_verification()
    print('✅ 中規模テスト完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "large")
            print_info "大規模実験実行中 (10^8規模)..."
            print_warning "この実験は6-12時間かかる可能性があります"
            read -p "続行しますか? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_sage_script "
load('src/large_scale_experiment.py')
try:
    check_large_scale_dependencies()
    experiment, results = run_large_scale_verification()
    print('✅ 大規模実験完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            else
                print_info "大規模実験をキャンセルしました"
            fi
            ;;
        
        "large-test")
            print_info "大規模テスト実行中 (10^7規模)..."
            run_sage_script "
load('src/large_scale_experiment.py')
try:
    check_large_scale_dependencies()
    experiment, results = run_large_scale_test()
    print('✅ 大規模テスト完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "ultra")
            print_info "超大規模実験実行中 (10^9規模)..."
            print_warning "この実験は24-48時間かかる可能性があります"
            print_warning "64GB RAM, 32コア, 100GB空き容量が必要です"
            read -p "続行しますか? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_sage_script "
load('src/ultra_large_experiment.py')
try:
    if check_ultra_large_dependencies():
        experiment, results = run_ultra_large_verification()
        print('✅ 超大規模実験完了')
    else:
        print('❌ システム要件を満たしていません')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            else
                print_info "超大規模実験をキャンセルしました"
            fi
            ;;
        
        "ultra-test")
            print_info "超大規模テスト実行中 (10^8規模)..."
            run_sage_script "
load('src/ultra_large_experiment.py')
try:
    if check_ultra_large_dependencies():
        experiment, results = run_ultra_large_test()
        print('✅ 超大規模テスト完了')
    else:
        print('❌ システム要件を満たしていません')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        "single-case")
            if [[ -z "$case_index" ]]; then
                print_error "ケースインデックスを指定してください (0-12)"
                exit 1
            fi
            print_info "単一ケーステスト実行中: Omar Case $((case_index + 1))"
            run_sage_script "
load('src/medium_scale_experiment.py')
try:
    experiment, result = run_single_case_test(case_index=$case_index, x_max=1000)
    print('✅ 単一ケーステスト完了')
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
"
            ;;
        
        *)
            print_error "不明な実験タイプ: $experiment_type"
            show_usage
            exit 1
            ;;
    esac
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
            cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
            mem_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
            
            echo "$(date '+%Y-%m-%d %H:%M:%S') CPU: ${cpu_usage}%, MEM: ${mem_usage}%" >> performance.log
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
            check_system_requirements
            ;;
        
        "cleanup")
            cleanup_results
            ;;
        
        "test"|"medium"|"medium-test"|"large"|"large-test"|"ultra"|"ultra-test")
            show_system_info
            
            # パフォーマンス監視を開始
            monitor_performance
            
            # 実験実行
            run_experiment $1
            
            # 可視化
            run_visualization
            
            print_success "全処理完了"
            ;;
        
        "single-case")
            if [[ -n "$2" && "$2" =~ ^[0-9]+$ && "$2" -ge 0 && "$2" -le 12 ]]; then
                run_experiment $1 $2
            else
                print_error "有効なケースインデックスを指定してください (0-12)"
                exit 1
            fi
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
