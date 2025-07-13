#!/bin/bash

# =============================================================================
# Quaternion拡大における素数の偏り計算プログラム
# 実行用シェルスクリプト集
# =============================================================================

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ログディレクトリを作成
mkdir -p logs

# =============================================================================
# 1. 全ケース実行（推奨）
# =============================================================================
run_all() {
    echo "=== 全ケースのフロベニウス元計算とグラフ描画を実行 ==="
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --all --max-prime 1000000 2>&1 | tee logs/run_all_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_all_*.log"
}

# =============================================================================
# 2. 高速テスト実行（10^5素数まで）
# =============================================================================
run_test() {
    echo "=== テスト実行（10^5素数まで） ==="
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --all --max-prime 100000 2>&1 | tee logs/run_test_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_test_*.log"
}

# =============================================================================
# 3. フロベニウス元計算のみ
# =============================================================================
run_frobenius_only() {
    echo "=== フロベニウス元計算のみ実行 ==="
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --compute-frobenius --max-prime 1000000 2>&1 | tee logs/run_frobenius_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_frobenius_*.log"
}

# =============================================================================
# 4. グラフ描画のみ
# =============================================================================
run_graphs_only() {
    echo "=== グラフ描画のみ実行 ==="
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --plot-graphs 2>&1 | tee logs/run_graphs_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_graphs_*.log"
}

# =============================================================================
# 5. 特定ケース実行
# =============================================================================
run_single_case() {
    if [ -z "$1" ]; then
        echo "使用方法: run_single_case <ケース番号(1-13)>"
        echo "例: run_single_case 1"
        return 1
    fi
    
    local case_id=$1
    echo "=== Case $case_id のみ実行 ==="
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --case $case_id --all --max-prime 1000000 2>&1 | tee logs/run_case_${case_id}_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_case_${case_id}_*.log"
}

# =============================================================================
# 6. データファイル確認
# =============================================================================
check_data() {
    echo "=== データファイル確認 ==="
    sage src/main_runner.py --check-data
}

# =============================================================================
# 7. クリーンアップ
# =============================================================================
cleanup() {
    echo "=== クリーンアップ実行 ==="
    read -p "データファイルを削除しますか？ (frobenius_data/) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf frobenius_data/
        echo "データファイルを削除しました"
    fi
    
    read -p "グラフファイルを削除しますか？ (graphs/) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf graphs/
        echo "グラフファイルを削除しました"
    fi
    
    read -p "ログファイルを削除しますか？ (logs/) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf logs/
        echo "ログファイルを削除しました"
    fi
}

# =============================================================================
# 8. システム情報表示
# =============================================================================
show_system_info() {
    echo "=== システム情報 ==="
    echo "日時: $(date)"
    echo "OS: $(uname -a)"
    echo "CPU数: $(nproc)"
    echo "メモリ: $(free -h | grep '^Mem:' | awk '{print $2}')"
    echo "ディスク空き容量: $(df -h . | tail -1 | awk '{print $4}')"
    echo
    
    echo "=== SageMath情報 ==="
    if command -v sage &> /dev/null; then
        sage --version
        echo "SageMath Python: $(sage --python --version 2>&1)"
    else
        echo "SageMathが見つかりません"
    fi
    echo
    
    echo "=== ファイル確認 ==="
    echo "必要なファイル:"
    for file in src/frobenius_calculator.py src/graph_plotter.py src/main_runner.py; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        else
            echo "  ✗ $file (見つかりません)"
        fi
    done
}

# =============================================================================
# 9. 大規模計算実行（2×10^6素数まで）
# =============================================================================
run_large_scale() {
    echo "=== 大規模計算実行（2×10^6素数まで） ==="
    echo "警告: この計算には大量のメモリ（16GB以上推奨）と時間（数時間）が必要です"
    read -p "続行しますか？ [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "キャンセルしました"
        return 0
    fi
    
    echo "開始時刻: $(date)"
    
    sage src/main_runner.py --all --max-prime 2000000 --processes $(nproc) 2>&1 | tee logs/run_large_$(date +%Y%m%d_%H%M%S).log
    
    echo "終了時刻: $(date)"
    echo "ログファイル: logs/run_large_*.log"
}

# =============================================================================
# 10. 並列処理テスト
# =============================================================================
test_parallel() {
    echo "=== 並列処理テスト ==="
    echo "利用可能なCPU数: $(nproc)"
    
    # 1プロセス
    echo "1プロセスでCase 1を実行..."
    time sage src/main_runner.py --case 1 --compute-frobenius --max-prime 100000 --processes 1 > /dev/null 2>&1
    
    # 全プロセス
    echo "全プロセス($(nproc))でCase 1を実行..."
    time sage src/main_runner.py --case 1 --compute-frobenius --max-prime 100000 --processes $(nproc) > /dev/null 2>&1
    
    echo "並列処理テスト完了"
}

# =============================================================================
# メイン関数
# =============================================================================
main() {
    echo "Quaternion拡大における素数の偏り計算プログラム"
    echo "=================================================="
    echo
    
    if [ $# -eq 0 ]; then
        echo "使用方法:"
        echo "  $0 [コマンド] [オプション]"
        echo
        echo "利用可能なコマンド:"
        echo "  all                     - 全ケース実行（推奨）"
        echo "  test                    - テスト実行（10^5素数まで）"
        echo "  frobenius              - フロベニウス元計算のみ"
        echo "  graphs                 - グラフ描画のみ"
        echo "  case <番号>            - 特定ケース実行（1-13）"
        echo "  check                  - データファイル確認"
        echo "  cleanup                - ファイル削除"
        echo "  info                   - システム情報表示"
        echo "  large                  - 大規模計算（2×10^6素数）"
        echo "  parallel               - 並列処理テスト"
        echo
        echo "例:"
        echo "  $0 all                 # 全ケースを実行"
        echo "  $0 test                # テスト実行"
        echo "  $0 case 1              # Case 1のみ実行"
        echo "  $0 check               # データ確認"
        echo
        return 0
    fi
    
    case "$1" in
        "all")
            run_all
            ;;
        "test")
            run_test
            ;;
        "frobenius")
            run_frobenius_only
            ;;
        "graphs")
            run_graphs_only
            ;;
        "case")
            run_single_case "$2"
            ;;
        "check")
            check_data
            ;;
        "cleanup")
            cleanup
            ;;
        "info")
            show_system_info
            ;;
        "large")
            run_large_scale
            ;;
        "parallel")
            test_parallel
            ;;
        *)
            echo "エラー: 不明なコマンド '$1'"
            echo "使用方法については '$0' を実行してください"
            return 1
            ;;
    esac
}

# スクリプトが直接実行された場合
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
