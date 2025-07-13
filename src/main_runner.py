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
"""

import argparse
import sys
import os
import time
import multiprocessing as mp
import json

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
    def __init__(self, max_prime=10**6, num_processes=None):
        """
        Quaternion拡大研究の統合クラス
        
        Args:
            max_prime: 計算する最大の素数
            num_processes: 使用するプロセス数
        """
        self.max_prime = max_prime
        self.num_processes = num_processes or mp.cpu_count()
        self.data_dir = "frobenius_data"
        self.graph_dir = "graphs"
        
        # ディレクトリを作成
        for dir_path in [self.data_dir, self.graph_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        print(f"Quaternion拡大における素数の偏り研究")
        print(f"設定:")
        print(f"  最大素数: {self.max_prime:,}")
        print(f"  プロセス数: {self.num_processes}")
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
        全ケースのグラフを描画
        """
        print("=" * 60)
        print("全ケースのグラフ描画を開始")
        print("=" * 60)
        
        analyzer = BiasAnalyzer(self.data_dir)
        
        try:
            analyzer.analyze_all_cases(max_x=min(self.max_prime, 10**5))
            print("全ケースのグラフ描画が完了しました！")
        except Exception as e:
            print(f"グラフ描画中にエラーが発生: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_graphs_single_case(self, case_id):
        """
        単一ケースのグラフを描画
        
        Args:
            case_id: ケースID (1-13)
        """
        if not (1 <= case_id <= 13):
            print(f"エラー: ケースIDは1-13の範囲で指定してください。指定値: {case_id}")
            return
        
        print(f"Case {case_id} のグラフ描画を開始")
        
        analyzer = BiasAnalyzer(self.data_dir)
        
        try:
            analyzer.plot_bias_graphs(case_id, max_x=min(self.max_prime, 10**5), output_dir=self.graph_dir)
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
        
        for case_id in range(1, 14):
            filename = f"{self.data_dir}/case_{case_id:02d}_frobenius.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    num_primes = len(data.get('frobenius_elements', {}))
                    print(f"Case {case_id:2d}: ✓ ({num_primes:,} primes)")
                except:
                    print(f"Case {case_id:2d}: ✗ (ファイルは存在するが読み込めません)")
            else:
                print(f"Case {case_id:2d}: ✗ (ファイルが存在しません)")

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
    parser.add_argument('--processes', type=int, 
                        help='使用するプロセス数 (デフォルト: 自動)')
    
    args = parser.parse_args()
    
    # 引数のチェック
    if not any([args.compute_frobenius, args.plot_graphs, args.all, args.check_data]):
        parser.print_help()
        return
    
    # 研究クラスを初期化
    research = QuaternionResearch(
        max_prime=args.max_prime,
        num_processes=args.processes
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
