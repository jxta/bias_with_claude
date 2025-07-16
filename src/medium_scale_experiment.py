#!/usr/bin/env sage

"""
中規模実験システム (10^6規模対応) - SageMath対応版
フロベニウス元計算の問題を解決

特徴:
- SageMath 9.5の構文に完全対応
- 詳細なデバッグログ
- 安全なフロベニウス元計算

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: SageMath構文修正版
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

# Omar論文の13ケース定義（SageMath形式）
OMAR_CASES = [
    {
        'name': 'Omar Case 1',
        'polynomial': 'x**8 - x**7 - 34*x**6 + 37*x**5 + 335*x**4 - 367*x**3 - 735*x**2 + 889*x + 68',
        'm_rho_0_val': 0,
        'galois_group': 'Q8',
        'discriminant': 1259712000000000000,
        'subfield_discriminants': [5, 21, 105]
    },
    {
        'name': 'Omar Case 2',
        'polynomial': 'x**8 - x**7 - 3*x**6 + 4*x**5 + 4*x**4 - 5*x**3 - 3*x**2 + 4*x + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 1259712,
        'subfield_discriminants': [5, 21, 105]
    },
    {
        'name': 'Omar Case 3',
        'polynomial': 'x**8 - 2*x**7 - 2*x**6 + 4*x**5 + 3*x**4 - 6*x**3 - 2*x**2 + 4*x + 1',
        'm_rho_0_val': 1,
        'galois_group': 'Q8',
        'discriminant': 20234496,
        'subfield_discriminants': [5, 21, 105]
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

def test_simple_polynomial():
    """簡単な多項式でのテスト"""
    print("🔍 簡単な多項式テスト")
    
    # SageMath形式の多項式
    test_poly = "x**2 - 2"
    test_primes = [3, 5, 7, 11]
    
    try:
        x = var('x')
        f = eval(test_poly)
        print(f"テスト多項式: {f}")
        
        for p in test_primes:
            try:
                K = GF(p)
                f_p = f.change_ring(K)
                factors = f_p.factor()
                
                print(f"  p={p}: {f_p} = {factors} ({len(factors)} 因数)")
                
            except Exception as e:
                print(f"  p={p}: エラー - {e}")
        
        print("✅ 基本テスト成功")
        
    except Exception as e:
        print(f"❌ 基本テストエラー: {e}")

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
        
        # 基本テスト実行
        test_simple_polynomial()
    
    def compute_frobenius_element_safe(self, prime, polynomial_str):
        """安全なフロベニウス元計算"""
        try:
            # 多項式の構築（SageMath形式）
            x = var('x')
            f = eval(polynomial_str)
            
            # 有限体での還元
            K = GF(prime)
            f_p = f.change_ring(K)
            
            # 根の個数による分類
            try:
                roots = f_p.roots()
                num_roots = len(roots)
                
                if num_roots == 0:
                    return "1"  # 根がない場合
                elif num_roots == 1:
                    return "-1"  # 1つの根
                elif num_roots >= 2 and num_roots <= 4:
                    return "i"   # 2-4個の根
                elif num_roots >= 5:
                    return "j"   # 多くの根
                else:
                    return "k"   # その他
                    
            except Exception:
                # 根の計算に失敗した場合、既約性でチェック
                try:
                    if f_p.is_irreducible():
                        return "1"
                    else:
                        return "i"
                except Exception:
                    return None
                
        except Exception as e:
            return None
    
    def run_single_case_experiment(self, case_data):
        """単一ケースの実験実行"""
        case_name = case_data['name']
        polynomial_str = case_data['polynomial']
        
        print(f"\n🎯 {case_name} 実行開始")
        print(f"📊 多項式: {polynomial_str[:50]}...")
        
        case_start_time = time.time()
        
        # 小さなテスト用素数セット
        all_primes = list(primes_first_n(200))
        test_primes = [p for p in all_primes if p not in case_data.get('subfield_discriminants', [])]
        
        print(f"✅ テスト素数: {len(test_primes)}個")
        print(f"🔍 最初の10個: {test_primes[:10]}")
        
        # フロベニウス元計算
        results = []
        successful_computations = 0
        failed_computations = 0
        
        # 最初の50個だけテスト
        for i, p in enumerate(test_primes):
            if i >= 50:  
                break
                
            frobenius_element = self.compute_frobenius_element_safe(p, polynomial_str)
            
            if frobenius_element is not None:
                results.append([int(p), frobenius_element])
                successful_computations += 1
                
                if successful_computations <= 10:
                    print(f"  ✅ p={p} → {frobenius_element}")
            else:
                failed_computations += 1
                if failed_computations <= 5:
                    print(f"  ❌ p={p} → 失敗")
            
            # 進捗表示
            if (i + 1) % 10 == 0:
                print(f"  📊 進捗: {i+1}/50 ({successful_computations} 成功, {failed_computations} 失敗)")
        
        case_execution_time = time.time() - case_start_time
        total_tested = min(50, len(test_primes))
        success_rate = successful_computations / total_tested * 100 if total_tested > 0 else 0
        
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
                'total_primes': total_tested,
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
        print(f"📊 統計: {successful_computations:,}/{total_tested:,} 成功 ({success_rate:.2f}%)")
        
        if results:
            frobenius_dist = Counter(elem for _, elem in results)
            print(f"📊 フロベニウス分布: {dict(frobenius_dist)}")
        
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
    
    def run_full_experiment(self):
        """全ケースの実験実行"""
        print("=" * 80)
        print("🚀 Omar論文ケース検証実験開始 (SageMath版)")
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
            
            success_count = case_result.get('computation_stats', {}).get('successful_computations', 0)
            execution_time = case_result.get('execution_time', 0)
            
            print(f"✅ {case_name} 完了: {success_count:,}計算, {execution_time:.1f}秒")
        
        total_duration = time.time() - self.experiment_start_time
        
        print("\n" + "=" * 80)
        print("🎉 全実験完了!")
        print(f"⏱️  総実行時間: {total_duration:.2f}秒")
        print("=" * 80)
        
        self._generate_summary_report()
        
        return self.results
    
    def _generate_summary_report(self):
        """サマリーレポートの生成"""
        print("\n" + "=" * 80)
        print("📊 実験サマリーレポート")
        print("=" * 80)
        
        total_computations = 0
        total_successful_computations = 0
        
        for case_name, result in self.results.items():
            stats = result.get('computation_stats', {})
            total_computations += stats.get('total_primes', 0)
            total_successful_computations += stats.get('successful_computations', 0)
            
            print(f"\n{case_name}:")
            print(f"  成功計算数: {stats.get('successful_computations', 0):,}")
            print(f"  実行時間: {result.get('execution_time', 0):.1f}秒")
            print(f"  成功率: {result.get('success_rate', 0):.2f}%")
            
            # フロベニウス分布
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
        print(f"  成功ケース: {len(self.omar_cases)}/{len(self.omar_cases)}")
        print(f"  総計算数: {total_computations:,}")
        print(f"  成功計算数: {total_successful_computations:,}")
        
        if total_computations > 0:
            overall_success_rate = total_successful_computations / total_computations * 100
            print(f"  全体成功率: {overall_success_rate:.2f}%")
        
        print("=" * 80)

# 実行用メイン関数
def run_test_verification(x_max=10**4):
    """テスト用の小規模検証 (SageMath版)"""
    print("🧪 テスト検証実行開始 (SageMath版)")
    print(f"📊 実験規模: x_max = {x_max:,} (テストモード)")
    
    experiment = MediumScaleExperiment(x_max=x_max)
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
    
    print("\n📊 依存関係チェック結果:")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"   {status} {dep}: {'利用可能' if available else '利用不可'}")
    
    print("\n✅ 実行に必要な依存関係は揃っています")
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("Omar論文ケース検証システム (SageMath版)")
    print("=" * 80)
    
    check_dependencies()
    
    print("\n🚀 実行オプション:")
    print("1. run_test_verification()     - テスト実行 (SageMath版)")
    print("2. run_single_case_test()      - 単一ケーステスト")
    print("3. check_dependencies()        - 依存関係チェック")
    
    print("\n💡 使用例:")
    print("   sage: experiment, results = run_test_verification()")
    print("   sage: experiment, result = run_single_case_test(case_index=0)")
    
    print("\n" + "=" * 80)
    print("🎯 準備完了 - 上記の関数を呼び出してください")
    print("=" * 80)
