#!/usr/bin/env sage

"""
青木美穂さんとの共同研究
Quaternion拡大における素数の偏りの計算プログラム

使用方法:
1. フロベニウス元の計算とJSONファイル出力:
   sage main_runner.py --compute-frobenius

2. グラフの描画:
   sage main_runner.py --plot-graphs

3. 両方を順次実行:
   sage main_runner.py --all

4. 特定のケースのみ実行:
   sage main_runner.py --case 1 --compute-frobenius
   sage main_runner.py --case 1 --plot-graphs
   
5. 並列処理の設定:
   sage main_runner.py --plot-graphs --graph-processes 8
"""

import argparse
import sys
import os
import time
import multiprocessing as mp
import json

# SageMathの必要な関数をインポート
from sage.all import *

# 他のモジュールをインポート（同じディレクトリにあると仮定）
try:
    from frobenius_calculator import (
        OMAR_POLYNOMIALS, 
        compute_frobenius_elements_parallel, 
        save_frobenius_data
    )
    from graph_plotter import BiasAnalyzer
except ImportError as e:
    print(f"モジュールのインポートエラー: {e}")
    print("frobenius_calculator.py と graph_plotter.py が同じディレクトリにあることを確認してください。")
    sys.exit(1)

class QuaternionResearch:
    def __init__(self, max_prime=10**6, num_processes=None, graph_max_x=None, graph_processes=None):
        """
        Quaternion拡大研究の統合クラス
        
        Args:
            max_prime: 計算する最大の素数
            num_processes: フロベニウス計算用プロセス数
            graph_max_x: グラフの最大x値 (Noneの場合は自動検出)
            graph_processes: グラフ描画用プロセス数 (Noneの場合は自動設定)
        """
        self.max_prime = max_prime
        self.graph_max_x = graph_max_x
        self.num_processes = num_processes or mp.cpu_count()
        self.graph_processes = graph_processes  # 新規追加
        self.data_dir = "frobenius_data"
        self.graph_dir = "graphs"
        
        # ディレクトリを作成
        for dir_path in [self.data_dir, self.graph_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        print(f"Quaternion拡大における素数の偏り研究")
        print(f"設定:")
        print(f"  最大素数: {self.max_prime:,}")
        print(f"  グラフ最大x値: {'自動検出' if self.graph_max_x is None else f'{self.graph_max_x:,}'}")
        print(f"  フロベニウス計算プロセス数: {self.num_processes}")
        print(f"  グラフ描画プロセス数: {'自動設定' if self.graph_processes is None else self.graph_processes}")
        print(f"  データディレクトリ: {self.data_dir}")
        print(f"  グラフディレクトリ: {self.graph_dir}")
        print()
    
    def compute_frobenius_all_cases(self):
        """
        全ケースのフロベニウス元を計算
        """
        print("=" * 60)
        print("全ケースのフロベニウス元計算を開始")
        print("=" * 60)
        
        total_start_time = time.time()
        
        for case_info in OMAR_POLYNOMIALS:
            case_start_time = time.time()
            
            try:
                print(f"\nCase {case_info['id']} 開始")
                print(f"多項式: {case_info['poly']}")
                print(f"判別式: {case_info['discriminant']}")
                print(f"m_ρ₀: {case_info['m_rho0']}")
                
                # フロベニウス元を計算
                frobenius_data = compute_frobenius_elements_parallel(
                    case_info, self.max_prime, self.num_processes
                )
                
                # JSONファイルに保存
                save_frobenius_data(case_info, frobenius_data, self.data_dir)
                
                case_end_time = time.time()
                case_duration = case_end_time - case_start_time
                
                print(f"Case {case_info['id']} 完了 (時間: {case_duration:.2f}秒)")
                print(f"計算した素数の数: {len(frobenius_data)}")
                
            except Exception as e:
                print(f"Case {case_info['id']} でエラーが発生: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        print("\n" + "=" * 60)
        print(f"全ケースの計算が完了しました！")
        print(f"総計算時間: {total_duration:.2f}秒 ({total_duration/60:.2f}分)")
        print("=" * 60)
    
    def compute_frobenius_single_case(self, case_id):
        """
        単一ケースのフロベニウス元を計算
        
        Args:
            case_id: ケースID (1-13)
        """
        if not (1 <= case_id <= 13):
            print(f"エラー: ケースIDは1-13の範囲で指定してください。指定値: {case_id}")
            return
        
        case_info = OMAR_POLYNOMIALS[case_id - 1]
        
        print(f"Case {case_id} のフロベニウス元計算を開始")
        print(f"多項式: {case_info['poly']}")
        print(f"判別式: {case_info['discriminant']}")
        print(f"m_ρ₀: {case_info['m_rho0']}")
        
        start_time = time.time()
        
        try:
            # フロベニウス元を計算
            frobenius_data = compute_frobenius_elements_parallel(
                case_info, self.max_prime, self.num_processes
            )
            
            # JSONファイルに保存
            save_frobenius_data(case_info, frobenius_data, self.data_dir)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Case {case_id} 完了 (時間: {duration:.2f}秒)")
            print(f"計算した素数の数: {len(frobenius_data)}")
            
        except Exception as e:
            print(f"Case {case_id} でエラーが発生: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_graphs_all_cases(self):
        """
        全ケースのグラフを描画（並列処理対応版）
        """
        print("=" * 60)
        print("全ケースのグラフ描画を開始（並列処理版）")
        print("=" * 60)
        
        # 並列処理対応のAnalyzerを初期化
        analyzer = BiasAnalyzer(self.data_dir, num_processes=self.graph_processes)
        
        try:
            # 改善版: 自動検出またはユーザー指定のmax_xを使用
            analyzer.analyze_all_cases(max_x=self.graph_max_x)
            print("全ケースのグラフ描画が完了しました！")
        except Exception as e:
            print(f"グラフ描画中にエラーが発生: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_graphs_single_case(self, case_id):
        """
        単一ケースのグラフを描画（並列処理対応版）
        
        Args:
            case_id: ケースID (1-13)
        """
        if not (1 <= case_id <= 13):
            print(f"エラー: ケースIDは1-13の範囲で指定してください。指定値: {case_id}")
            return
        
        print(f"Case {case_id} のグラフ描画を開始（並列処理版）")
        
        # 並列処理対応のAnalyzerを初期化
        analyzer = BiasAnalyzer(self.data_dir, num_processes=self.graph_processes)
        
        try:
            # 改善版: 自動検出またはユーザー指定のmax_xを使用
            analyzer.plot_bias_graphs(case_id, max_x=self.graph_max_x, output_dir=self.graph_dir)
            analyzer.print_statistics(case_id)
            print(f"Case {case_id} のグラフ描画が完了しました！")
        except Exception as e:
            print(f"Case {case_id} のグラフ描画中にエラーが発生: {e}")
            import traceback
            traceback.print_exc()
    
    def run_all(self):
        """
        フロベニウス元計算とグラフ描画を順次実行
        """
        print("=" * 60)
        print("フロベニウス元計算とグラフ描画を順次実行")
        print("=" * 60)
        
        # フロベニウス元計算
        self.compute_frobenius_all_cases()
        
        print("\n" + "=" * 60)
        print("フロベニウス元計算完了。グラフ描画を開始します。")
        print("=" * 60)
        
        # グラフ描画
        self.plot_graphs_all_cases()
    
    def check_data_files(self):
        """
        データファイルの存在をチェック
        """
        print("データファイルの存在チェック:")
        print("-" * 40)
        
        max_detected_prime = 0
        
        for case_id in range(1, 14):
            filename = f"{self.data_dir}/case_{case_id:02d}_frobenius.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    frobenius_elements = data.get('frobenius_elements', {})
                    num_primes = len(frobenius_elements)
                    
                    # 最大素数を取得
                    if frobenius_elements:
                        case_max_prime = max(int(p) for p in frobenius_elements.keys())
                        max_detected_prime = max(max_detected_prime, case_max_prime)
                        print(f"Case {case_id:2d}: ✓ ({num_primes:,} primes, max: {case_max_prime:,})")
                    else:
                        print(f"Case {case_id:2d}: ✓ ({num_primes:,} primes)")
                        
                except Exception as e:
                    print(f"Case {case_id:2d}: ✗ (ファイルは存在するが読み込めません: {e})")
            else:
                print(f"Case {case_id:2d}: ✗ (ファイルが存在しません)")
        
        if max_detected_prime > 0:
            print(f"\n検出された最大素数: {max_detected_prime:,}")
            print(f"推奨グラフ最大x値: {self._suggest_graph_max_x(max_detected_prime):,}")
            
            # 並列処理の推奨設定を表示
            cpu_count = mp.cpu_count()
            if max_detected_prime >= 10**7:
                recommended_processes = min(8, cpu_count)
                print(f"推奨グラフ描画プロセス数: {recommended_processes} (大規模データ用)")
            else:
                recommended_processes = min(4, cpu_count)
                print(f"推奨グラフ描画プロセス数: {recommended_processes}")
    
    def _suggest_graph_max_x(self, max_prime):
        """
        最大素数から推奨グラフ最大x値を計算
        """
        if max_prime < 10**3:
            return 10**3
        elif max_prime < 10**4:
            return 10**4
        elif max_prime < 10**5:
            return 10**5
        elif max_prime < 10**6:
            return 10**6
        elif max_prime < 10**7:
            return 10**7
        else:
            return 10**8

def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(
        description="Quaternion拡大における素数の偏りの計算プログラム",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 実行モードの選択
    parser.add_argument('--compute-frobenius', action='store_true',
                        help='フロベニウス元を計算してJSONファイルに保存')
    parser.add_argument('--plot-graphs', action='store_true',
                        help='JSONファイルからグラフを描画')
    parser.add_argument('--all', action='store_true',
                        help='フロベニウス元計算とグラフ描画を順次実行')
    parser.add_argument('--check-data', action='store_true',
                        help='データファイルの存在をチェック')
    
    # ケース指定
    parser.add_argument('--case', type=int, metavar='N',
                        help='特定のケース(1-13)のみを処理')
    
    # 設定オプション
    parser.add_argument('--max-prime', type=int, default=10**6,
                        help='計算する最大の素数 (デフォルト: 1,000,000)')
    parser.add_argument('--graph-max-x', type=int, 
                        help='グラフの最大x値 (指定しない場合は自動検出)')
    parser.add_argument('--processes', type=int, 
                        help='フロベニウス計算用プロセス数 (デフォルト: 自動)')
    parser.add_argument('--graph-processes', type=int,
                        help='グラフ描画用プロセス数 (デフォルト: 自動、大規模データには8推奨)')
    
    args = parser.parse_args()
    
    # 引数のチェック
    if not any([args.compute_frobenius, args.plot_graphs, args.all, args.check_data]):
        parser.print_help()
        return
    
    # 研究クラスを初期化
    research = QuaternionResearch(
        max_prime=args.max_prime,
        num_processes=args.processes,
        graph_max_x=args.graph_max_x,
        graph_processes=args.graph_processes  # 新規追加
    )
    
    # データファイルチェック
    if args.check_data:
        research.check_data_files()
        return
    
    # 実行
    if args.all:
        research.run_all()
    elif args.case:
        if args.compute_frobenius:
            research.compute_frobenius_single_case(args.case)
        if args.plot_graphs:
            research.plot_graphs_single_case(args.case)
    else:
        if args.compute_frobenius:
            research.compute_frobenius_all_cases()
        if args.plot_graphs:
            research.plot_graphs_all_cases()

if __name__ == "__main__":
    main()
