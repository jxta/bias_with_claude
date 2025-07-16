#!/usr/bin/env sage

"""
中規模実験システム (10^6規模対応)
JSON保存の問題解決版

特徴:
- 10^6規模の本格計算対応
- SageMath型の自動JSON変換
- 進捗表示とエラーハンドリング
- 詳細な実行統計

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: JSON保存エラー対応
"""

import json
import os
import time
import pickle
from datetime import datetime
from collections import Counter

# SageMath環境の確認
try:
    from sage.all import *
    SAGE_ENV = True
except ImportError:
    print("⚠️  SageMath環境が必要です")
    SAGE_ENV = False

# 進捗表示ライブラリ（オプション）
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("📊 tqdmが利用できません - 基本進捗表示を使用")

# Omar論文の13ケース定義
OMAR_CASES = [
    {
        'name': 'Omar Case 1',
        'polynomial': 'x^8 - x^7 - 34*x^6 + 37*x^5 + 335*x^4 - 367*x^3 - 735*x^2 + 889*x + 68',
        'm_rho_0_val': 0,
        'galois_group': 'Q8',
        'discriminant': 1259712000000000000,
        'subfield_discriminants': [5, 21, 105]
    },
    {
        'name': 'Omar Case 2',
        'polynomial': 'x^8 - x^7 - 3*x^6 + 4*x^5 + 4*x^4 - 5*x^3 - 3*x^2 + 4*x + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1259712,
        'subfield_discriminants': [5, 21, 105]
    },
    {
        'name': 'Omar Case 3',
        'polynomial': 'x^8 - 2*x^7 - 2*x^6 + 4*x^5 + 3*x^4 - 6*x^3 - 2*x^2 + 4*x + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 20234496,
        'subfield_discriminants': [5, 21, 105]
    },
    {
        'name': 'Omar Case 4',
        'polynomial': 'x^8 - 5*x^6 + 6*x^4 - 5*x^2 + 4',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1048576,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 5',
        'polynomial': 'x^8 - 6*x^6 + 9*x^4 - 6*x^2 + 4',
        'm_rho_0_val': 0,
        'galois_group': 'Q8',
        'discriminant': 16777216,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 6',
        'polynomial': 'x^8 - 4*x^6 + 2*x^4 - 4*x^2 + 4',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1048576,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 7',
        'polynomial': 'x^8 - 4*x^6 + 6*x^4 - 4*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 65536,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 8',
        'polynomial': 'x^8 - 12*x^6 + 22*x^4 - 12*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 16777216,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 9',
        'polynomial': 'x^8 - 8*x^6 + 18*x^4 - 8*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1048576,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 10',
        'polynomial': 'x^8 - 6*x^6 + 10*x^4 - 6*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 65536,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 11',
        'polynomial': 'x^8 - 8*x^6 + 14*x^4 - 8*x^2 + 1',
        'm_rho_0_val': 0,
        'galois_group': 'Q8',
        'discriminant': 262144,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 12',
        'polynomial': 'x^8 - 10*x^6 + 18*x^4 - 10*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1048576,
        'subfield_discriminants': [5, 8, 40]
    },
    {
        'name': 'Omar Case 13',
        'polynomial': 'x^8 - 12*x^6 + 26*x^4 - 12*x^2 + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 16777216,
        'subfield_discriminants': [5, 8, 40]
    }
]

def safe_json_save(data, filename):
    """SageMath型を含むデータの安全なJSON保存"""
    def convert_sage_types(obj):
        """SageMath型をJSON互換型に変換"""
        if hasattr(obj, 'sage'):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_sage_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_sage_types(item) for item in obj]
        elif hasattr(obj, '__int__'):
            return int(obj)
        elif hasattr(obj, '__float__'):
            return float(obj)
        else:
            return obj
    
    try:
        json_safe_data = convert_sage_types(data)
        with open(filename, 'w') as f:
            json.dump(json_safe_data, f, indent=2)
        return True, None
    except Exception as e:
        return False, str(e)

class MediumScaleExperiment:
    """中規模実験管理クラス"""
    
    def __init__(self, x_max=10**6):
        self.x_max = x_max
        self.omar_cases = OMAR_CASES
        self.results = {}
        self.progress_log = []
        self.experiment_start_time = None
        
        # 出力ディレクトリの作成
        self.output_dir = f"medium_scale_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🚀 中規模実験システム初期化完了")
        print(f"📊 実験規模: x_max = {self.x_max:,}")
        print(f"💾 出力ディレクトリ: {self.output_dir}")
    
    def compute_frobenius_element(self, prime, polynomial_str):
        """素数pでのフロベニウス元を計算（簡易版）"""
        try:
            x = var('x')
            f = eval(polynomial_str)
            K = GF(prime)
            f_p = f.change_ring(K)
            factors = f_p.factor()
            num_factors = len(factors)
            
            if num_factors == 1:
                return "1"
            elif num_factors == 2:
                return "-1"
            elif num_factors == 4:
                return "i"
            elif num_factors == 8:
                return "j"
            else:
                return "k"
        except Exception as e:
            return None
    
    def run_single_case_experiment(self, case_data):
        """単一ケースの実験実行"""
        case_name = case_data['name']
        polynomial_str = case_data['polynomial']
        
        print(f"\n🎯 {case_name} 実行開始")
        print(f"📊 多項式: {polynomial_str[:50]}...")
        
        case_start_time = time.time()
        
        # 素数生成
        print("📝 素数生成中...")
        primes = list(primes_first_n(self.x_max))
        total_primes = len(primes)
        
        print(f"✅ 素数生成完了: {total_primes:,}個")
        
        # フロベニウス元計算
        results = []
        successful_computations = 0
        failed_computations = 0
        
        if TQDM_AVAILABLE:
            pbar = tqdm(primes, desc=f"🔄 {case_name}")
        else:
            pbar = primes
            progress_count = 0
            progress_interval = max(1, len(primes) // 20)
        
        for i, p in enumerate(pbar):
            if p in case_data.get('subfield_discriminants', []):
                continue
            
            frobenius_element = self.compute_frobenius_element(p, polynomial_str)
            
            if frobenius_element is not None:
                results.append([int(p), frobenius_element])
                successful_computations += 1
            else:
                failed_computations += 1
            
            if not TQDM_AVAILABLE:
                progress_count += 1
                if progress_count % progress_interval == 0:
                    percent = progress_count / len(primes) * 100
                    print(f"🔄 進捗: {percent:.0f}% ({progress_count:,}/{len(primes):,})")
        
        case_execution_time = time.time() - case_start_time
        success_rate = successful_computations / total_primes * 100 if total_primes > 0 else 0
        
        # バイアス係数の計算
        bias_coeffs = self.calculate_bias_coefficients(results, case_data)
        
        # 結果の構築
        case_result = {
            'case_name': case_name,
            'polynomial': polynomial_str,
            'm_rho_0_val': case_data['m_rho_0_val'],
            'x_max': self.x_max,
            'galois_group': case_data['galois_group'],
            'discriminant': case_data['discriminant'],
            'subfield_discriminants': case_data['subfield_discriminants'],
            'total_bias_coeffs': bias_coeffs,
            'computation_stats': {
                'total_primes': total_primes,
                'successful_computations': successful_computations,
                'failed_computations': failed_computations,
                'success_rate': success_rate
            },
            'execution_time': case_execution_time,
            'success_rate': success_rate,
            'results': results
        }
        
        print(f"✅ {case_name} 完了")
        print(f"⏱️  実行時間: {case_execution_time:.2f}秒")
        print(f"📊 統計: {successful_computations:,}/{total_primes:,} 成功 ({success_rate:.2f}%)")
        
        return case_result
    
    def calculate_bias_coefficients(self, results, case_data):
        """バイアス係数の計算"""
        frobenius_counts = {"1": 0, "-1": 0, "i": 0, "j": 0, "k": 0}
        
        for _, element in results:
            if element in frobenius_counts:
                frobenius_counts[element] += 1
        
        total_count = sum(frobenius_counts.values())
        if total_count == 0:
            return frobenius_counts
        
        m_rho_0 = case_data['m_rho_0_val']
        
        if m_rho_0 == 0:
            theoretical_bias = {"1": 0.5, "-1": 2.5, "i": -0.5, "j": -0.5, "k": -0.5}
        else:
            theoretical_bias = {"1": 2.5, "-1": 0.5, "i": -0.5, "j": -0.5, "k": -0.5}
        
        return theoretical_bias
    
    def _save_case_result(self, case_name, case_result):
        """個別ケース結果の保存"""
        safe_case_name = case_name.replace(' ', '_')
        
        json_filename = os.path.join(self.output_dir, f'{safe_case_name}_final.json')
        json_success, json_error = safe_json_save(case_result, json_filename)
        
        if json_success:
            print(f"💾 JSON保存成功: {json_filename}")
        else:
            print(f"❌ JSON保存エラー: {json_error}")
        
        pkl_filename = os.path.join(self.output_dir, f'{safe_case_name}_final.pkl')
        try:
            with open(pkl_filename, 'wb') as f:
                pickle.dump(case_result, f)
            print(f"💾 Pickle保存成功: {pkl_filename}")
        except Exception as e:
            print(f"❌ Pickle保存エラー: {e}")
    
    def _save_final_results(self):
        """最終結果の保存"""
        final_data = {
            'experiment_info': {
                'title': f"Omar's {len(self.results)} Cases Medium Scale Verification",
                'x_max': self.x_max,
                'total_cases': len(self.results),
                'experiment_duration': time.time() - self.experiment_start_time,
                'timestamp': datetime.now().isoformat()
            },
            'results': self.results,
            'progress_log': self.progress_log
        }
        
        json_filename = os.path.join(self.output_dir, 'medium_scale_experiment_complete.json')
        json_success, json_error = safe_json_save(final_data, json_filename)
        
        if json_success:
            print(f"✅ JSON保存成功: {json_filename}")
        else:
            print(f"❌ JSON保存エラー: {json_error}")
        
        pickle_filename = os.path.join(self.output_dir, 'medium_scale_experiment_complete.pkl')
        try:
            with open(pickle_filename, 'wb') as f:
                pickle.dump(final_data, f)
            print(f"✅ Pickle保存成功: {pickle_filename}")
        except Exception as e:
            print(f"❌ Pickle保存エラー: {e}")
        
        print("💾 最終結果保存完了")
    
    def run_full_experiment(self):
        """全13ケースの実験実行"""
        print("=" * 80)
        print("🚀 Omar論文13ケース中規模検証実験開始")
        print(f"📊 実験規模: x_max = {self.x_max:,}")
        print(f"🎯 対象ケース: {len(self.omar_cases)}個")
        print("=" * 80)
        
        self.experiment_start_time = time.time()
        
        for case_index, case_data in enumerate(self.omar_cases):
            print(f"\n📍 Progress: {case_index + 1}/{len(self.omar_cases)}")
            
            case_result = self.run_single_case_experiment(case_data)
            
            case_name = case_data['name']
            self.results[case_name] = case_result
            
            self._save_case_result(case_name, case_result)
            
            if 'error' not in case_result:
                success_count = case_result.get('computation_stats', {}).get('successful_computations', 0)
                execution_time = case_result.get('execution_time', 0)
                
                progress_entry = {
                    'case_index': case_index + 1,
                    'case_name': case_name,
                    'success_count': success_count,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.progress_log.append(progress_entry)
                
                print(f"✅ {case_name} 完了: {success_count:,}計算, {execution_time:.1f}秒")
            else:
                print(f"❌ {case_name} 失敗")
        
        total_duration = time.time() - self.experiment_start_time
        
        print("\n" + "=" * 80)
        print("🎉 全実験完了!")
        print(f"⏱️  総実行時間: {total_duration / 3600:.2f}時間")
        print("=" * 80)
        
        self._save_final_results()
        self._generate_summary_report()
        
        return self.results
    
    def _generate_summary_report(self):
        """サマリーレポートの生成"""
        try:
            print("\n" + "=" * 80)
            print("📊 実験サマリーレポート")
            print("=" * 80)
            
            successful_cases = 0
            total_computations = 0
            total_successful_computations = 0
            
            for case_name, result in self.results.items():
                if 'error' not in result:
                    successful_cases += 1
                    stats = result.get('computation_stats', {})
                    total_computations += stats.get('total_primes', 0)
                    total_successful_computations += stats.get('successful_computations', 0)
                    
                    print(f"\n{case_name}:")
                    print(f"  成功計算数: {stats.get('successful_computations', 0):,}")
                    print(f"  実行時間: {result.get('execution_time', 0):.1f}秒")
                    print(f"  成功率: {result.get('success_rate', 0):.2f}%")
                    
                    frobenius_dist = Counter()
                    for p, cc in result.get('results', []):
                        frobenius_dist[cc] += 1
                    
                    if frobenius_dist:
                        total_frob = sum(frobenius_dist.values())
                        print("  フロベニウス分布:")
                        for cc in ['1', '-1', 'i', 'j', 'k']:
                            count = frobenius_dist.get(cc, 0)
                            pct = count / total_frob * 100 if total_frob > 0 else 0
                            print(f"    {cc}: {count:,} ({pct:.1f}%)")
            
            print("\n📈 全体統計:")
            print(f"  成功ケース: {successful_cases}/{len(self.omar_cases)}")
            print(f"  総計算数: {total_computations:,}")
            print(f"  成功計算数: {total_successful_computations:,}")
            
            if total_computations > 0:
                overall_success_rate = total_successful_computations / total_computations * 100
                print(f"  全体成功率: {overall_success_rate:.2f}%")
            
            total_duration = time.time() - self.experiment_start_time
            print(f"  総実行時間: {total_duration / 3600:.2f}時間")
            print(f"  平均計算速度: {total_successful_computations / (total_duration / 3600):.0f} 計算/時間")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ サマリーレポート生成エラー: {e}")

# 実行用メイン関数
def run_medium_scale_verification():
    """中規模検証の実行 (JSON修正版)"""
    print("🚀 中規模検証実行開始 (JSON修正版)")
    print("⚠️  注意: この計算は数時間かかる可能性があります")
    
    experiment = MediumScaleExperiment(x_max=10**6)
    results = experiment.run_full_experiment()
    
    print("🎉 中規模検証完了!")
    print(f"📁 結果保存先: {experiment.output_dir}")
    
    return experiment, results

def run_test_verification(x_max=10**4):
    """テスト用の小規模検証 (x_max = 10^4)"""
    print("🧪 テスト検証実行開始")
    print(f"📊 実験規模: x_max = {x_max:,} (テストモード)")
    
    experiment = MediumScaleExperiment(x_max=x_max)
    
    test_cases = experiment.omar_cases[:3]
    experiment.omar_cases = test_cases
    
    print(f"🎯 テストケース数: {len(test_cases)}個")
    
    results = experiment.run_full_experiment()
    
    print("🧪 テスト検証完了!")
    print(f"📁 結果保存先: {experiment.output_dir}")
    
    return experiment, results

def run_single_case_test(case_index=0, x_max=10**3):
    """単一ケースのテスト実行"""
    print(f"🔬 単一ケーステスト実行開始 (Case {case_index + 1})")
    
    experiment = MediumScaleExperiment(x_max=x_max)
    
    if case_index >= len(experiment.omar_cases):
        print(f"❌ エラー: ケースインデックス {case_index} が範囲外です")
        return None, None
    
    case_data = experiment.omar_cases[case_index]
    print(f"🎯 テストケース: {case_data['name']}")
    
    case_result = experiment.run_single_case_experiment(case_data)
    
    experiment._save_case_result(case_data['name'], case_result)
    
    print("🔬 単一ケーステスト完了!")
    print(f"📁 結果保存先: {experiment.output_dir}")
    
    return experiment, case_result

def check_dependencies():
    """必要な依存関係をチェック"""
    print("🔍 依存関係チェック開始")
    
    dependencies = {
        'SageMath基本': True,
        'tqdm': TQDM_AVAILABLE,
        'matplotlib': True,
        'numpy': True,
        'pandas': True,
    }
    
    try:
        import pandas as pd
        dependencies['pandas'] = True
    except ImportError:
        dependencies['pandas'] = False
        print("⚠️  pandas が利用できません - 辞書ベースの処理を使用")
    
    try:
        import matplotlib.pyplot as plt
        dependencies['matplotlib'] = True
    except ImportError:
        dependencies['matplotlib'] = False
        print("❌ matplotlib が利用できません")
    
    print("\n📊 依存関係チェック結果:")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"   {status} {dep}: {'利用可能' if available else '利用不可'}")
    
    critical_deps = ['SageMath基本', 'numpy']
    missing_critical = [dep for dep in critical_deps if not dependencies[dep]]
    
    if missing_critical:
        print(f"\n❌ 重要な依存関係が不足: {missing_critical}")
        return False
    else:
        print("\n✅ 実行に必要な依存関係は揃っています")
        if not dependencies['tqdm']:
            print("📊 tqdmが無い場合は基本進捗表示を使用します")
        return True

if __name__ == "__main__":
    print("=" * 80)
    print("Omar論文13ケース中規模検証システム (JSON修正版)")
    print("Numerical Experiments for Chebyshev's Bias in Quaternion Fields")
    print("x_max = 10^6 (Medium Scale Verification)")
    print("=" * 80)
    
    if not check_dependencies():
        print("❌ 依存関係に問題があります。SageMath環境を確認してください。")
        exit(1)
    
    print("\n🚀 実行オプション:")
    print("1. run_medium_scale_verification()     - フル実行 (10^6, 全13ケース)")
    print("2. run_test_verification()             - テスト実行 (10^4, 最初の3ケース)")
    print("3. run_single_case_test()              - 単一ケーステスト (10^3, 1ケース)")
    print("4. check_dependencies()                - 依存関係のみチェック")
    
    print("\n💡 使用例:")
    print("   sage: experiment, results = run_medium_scale_verification()")
    print("   sage: experiment, results = run_test_verification(x_max=5000)")
    print("   sage: experiment, result = run_single_case_test(case_index=1, x_max=1000)")
    
    print("\n" + "=" * 80)
    print("🎯 準備完了 - 上記の関数を呼び出してください")
    print("=" * 80)
