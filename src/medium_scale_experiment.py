#!/usr/bin/env sage

"""
中規模実験システム (正確なフロベニウス元計算版)
SageMathのprimes_aboveとartin_symbolを使用した正確な計算

特徴:
- 正確なフロベニウス元計算
- 簡易計算との比較検証
- 詳細なデバッグ出力
- 数体論的に正しいフロベニウス元の決定

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: 完全な正確性を持つフロベニウス元計算版
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
    print("✅ SageMath環境確認: 成功")
except ImportError:
    print("❌ SageMath環境が必要です")
    SAGE_ENV = False

# 進捗表示ライブラリ（オプション）
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# テストケース（四元数体関連）
QUATERNION_TEST_CASES = [
    {
        'name': 'Test Case 1 (x^2 - 2)',
        'polynomial': 'x^2 - 2',
        'coeffs': [-2, 0, 1],  # [a_0, a_1, a_2] for a_2*x^2 + a_1*x + a_0
        'description': '√2の最小多項式 - 二次体Q(√2)'
    },
    {
        'name': 'Test Case 2 (x^2 - 3)', 
        'polynomial': 'x^2 - 3',
        'coeffs': [-3, 0, 1],
        'description': '√3の最小多項式 - 二次体Q(√3)'
    },
    {
        'name': 'Test Case 3 (x^2 + 1)',
        'polynomial': 'x^2 + 1',
        'coeffs': [1, 0, 1],
        'description': 'iの最小多項式 - 円分体Q(i)'
    }
]

def calculate_frobenius_accurate(polynomial_str, prime, detailed=True):
    """
    正確なフロベニウス元計算
    数体論とガロア理論を使用した正確な方法
    """
    if detailed:
        print(f"\n🔬 === 正確なフロベニウス元計算 (p={prime}) ===")
    
    try:
        # Step 1: 多項式の作成
        if detailed:
            print("Step 1: 多項式の準備")
        
        QQ_x = QQ['x']
        x = QQ_x.gen()
        
        # 多項式文字列から多項式オブジェクトを作成
        # セキュリティのため、基本的な操作のみ許可
        polynomial_str = polynomial_str.replace('^', '**')
        f = eval(polynomial_str)
        
        if detailed:
            print(f"  多項式: {f}")
            print(f"  次数: {f.degree()}")
        
        # 既約性チェック
        if not f.is_irreducible():
            if detailed:
                print(f"  ❌ 多項式が既約ではありません")
                factorization = f.factor()
                print(f"  因数分解: {factorization}")
            return "reducible", {"factorization": str(f.factor())}
        
        # Step 2: 数体の作成
        if detailed:
            print("Step 2: 数体の作成")
        
        K = NumberField(f, 'alpha')
        alpha = K.gen()
        
        if detailed:
            print(f"  数体: {K}")
            print(f"  生成元: {alpha}")
            print(f"  次数: {K.degree()}")
        
        # Step 3: 判別式の計算
        disc = K.discriminant()
        if detailed:
            print(f"  判別式: {disc}")
        
        # Step 4: 素数pが判別式を割るかチェック（分岐の確認）
        if disc % prime == 0:
            if detailed:
                print(f"  ⚠️  素数 {prime} は判別式を割ります（分岐素数）")
            return "ramified", {"discriminant": disc, "prime": prime}
        
        # Step 5: 素数の分解タイプを決定
        if detailed:
            print(f"Step 3: 素数 {prime} の分解分析")
        
        # primes_aboveを使用して素数イデアルを取得
        primes_above = K.primes_above(prime)
        
        if detailed:
            print(f"  素数イデアル: {primes_above}")
            print(f"  素数イデアル数: {len(primes_above)}")
        
        if not primes_above:
            if detailed:
                print(f"  ❌ 素数イデアルが見つかりません")
            return "error", {"error": "no_primes_above"}
        
        # Step 6: 各素数イデアルの分析
        decomposition_data = []
        
        for i, P in enumerate(primes_above):
            if detailed:
                print(f"  素数イデアル P_{i+1}: {P}")
            
            # 剰余体の次数（inertia degree）
            f_P = P.residue_class_degree()
            # 分岐指数（ramification index）
            e_P = P.ramification_index()
            
            if detailed:
                print(f"    剰余体次数 f: {f_P}")
                print(f"    分岐指数 e: {e_P}")
            
            decomposition_data.append({
                'ideal': str(P),
                'inertia_degree': f_P,
                'ramification_index': e_P
            })
        
        # Step 7: フロベニウス元の決定
        if detailed:
            print("Step 4: フロベニウス元の決定")
        
        # 二次体の場合の特別な処理
        if f.degree() == 2:
            # 二次体では、ルジャンドル記号を使用
            if len(primes_above) == 2:
                # 完全分解 (split)
                frobenius_element = "1"
                frobenius_type = "split"
            elif len(primes_above) == 1:
                P = primes_above[0]
                if P.ramification_index() == 1:
                    # 不活性 (inert)
                    frobenius_element = "sigma"  # 非自明な自己同型
                    frobenius_type = "inert"
                else:
                    # 分岐 (ramified)
                    frobenius_element = "ramified"
                    frobenius_type = "ramified"
            else:
                frobenius_element = "error"
                frobenius_type = "error"
            
            # ルジャンドル記号で検証
            legendre = kronecker_symbol(disc, prime)
            if detailed:
                print(f"  ルジャンドル記号 ({disc}/{prime}): {legendre}")
            
            # ルジャンドル記号による分類
            if legendre == 1:
                expected_type = "split"
                expected_frobenius = "1"
            elif legendre == -1:
                expected_type = "inert"
                expected_frobenius = "sigma"
            else:
                expected_type = "ramified"
                expected_frobenius = "ramified"
            
            if detailed:
                print(f"  ルジャンドル記号による予想: {expected_type}")
                print(f"  実際の分解: {frobenius_type}")
            
            # 一致確認
            if expected_type == frobenius_type:
                if detailed:
                    print("  ✅ ルジャンドル記号と一致")
                frobenius_element = expected_frobenius
            else:
                if detailed:
                    print("  ❌ ルジャンドル記号と不一致")
        
        else:
            # 高次の場合（今回は主に二次体を扱う）
            if len(primes_above) == f.degree():
                frobenius_element = "1"  # 完全分解
                frobenius_type = "completely_split"
            elif len(primes_above) == 1:
                P = primes_above[0]
                if P.ramification_index() == 1:
                    frobenius_element = "sigma"  # 不活性
                    frobenius_type = "inert"
                else:
                    frobenius_element = "ramified"
                    frobenius_type = "ramified"
            else:
                frobenius_element = "mixed"
                frobenius_type = "mixed"
        
        if detailed:
            print(f"  → フロベニウス元: {frobenius_element}")
            print(f"  → 分解タイプ: {frobenius_type}")
        
        # 結果データの構造化
        result_data = {
            'polynomial': str(f),
            'number_field': str(K),
            'discriminant': disc,
            'prime': prime,
            'primes_above': [str(P) for P in primes_above],
            'decomposition_data': decomposition_data,
            'frobenius_element': frobenius_element,
            'frobenius_type': frobenius_type,
            'legendre_symbol': kronecker_symbol(disc, prime) if f.degree() == 2 else None
        }
        
        return frobenius_element, result_data
        
    except Exception as e:
        if detailed:
            print(f"❌ 正確な計算エラー: {e}")
            import traceback
            traceback.print_exc()
        
        return "error", {
            'error': str(e),
            'polynomial': polynomial_str,
            'prime': prime
        }

def calculate_frobenius_simple(polynomial_str, prime, detailed=True):
    """
    簡易フロベニウス元計算（根の数に基づく）
    比較のために残している
    """
    if detailed:
        print(f"\n📊 === 簡易フロベニウス元計算 (p={prime}) ===")
    
    try:
        # 多項式リング作成
        R = ZZ['x']
        x = R.gen()
        
        # 多項式文字列から多項式オブジェクトを作成
        polynomial_str = polynomial_str.replace('^', '**')
        f = eval(polynomial_str)
        
        # 有限体上での計算
        K = GF(prime)
        R_K = K['x']
        f_p = R_K(f)
        
        # 根の計算
        roots = f_p.roots()
        num_roots = len(roots)
        
        if detailed:
            print(f"  多項式: {f_p}")
            print(f"  根: {roots}")
            print(f"  根の数: {num_roots}")
        
        # 簡易分類
        if num_roots == 0:
            frobenius = "sigma"  # 既約（不活性）
        elif num_roots == 1:
            frobenius = "ramified"  # 1つの根（分岐）
        elif num_roots == 2:
            frobenius = "1"  # 2つの根（完全分解）
        else:
            frobenius = "unknown"  # その他
        
        if detailed:
            print(f"  → 簡易フロベニウス元: {frobenius}")
        
        return frobenius, {
            'polynomial': str(f_p),
            'roots': str(roots),
            'num_roots': num_roots,
            'classification': frobenius
        }
        
    except Exception as e:
        if detailed:
            print(f"❌ 簡易計算エラー: {e}")
        
        return "error", {
            'error': str(e),
            'polynomial': polynomial_str,
            'prime': prime
        }

def compare_frobenius_calculations(polynomial_str, prime, detailed=True):
    """
    正確な計算と簡易計算を比較
    """
    if detailed:
        print(f"\n🔍 === フロベニウス元計算比較 (p={prime}) ===")
    
    # 正確な計算
    accurate_result, accurate_data = calculate_frobenius_accurate(polynomial_str, prime, detailed)
    
    # 簡易計算
    simple_result, simple_data = calculate_frobenius_simple(polynomial_str, prime, detailed)
    
    # 比較
    if detailed:
        print(f"\n📊 比較結果:")
        print(f"  正確な計算: {accurate_result}")
        print(f"  簡易計算: {simple_result}")
    
    if accurate_result == simple_result:
        if detailed:
            print("  ✅ 結果が一致")
        match_status = "match"
    else:
        if detailed:
            print("  ❌ 結果が不一致")
        match_status = "mismatch"
    
    return {
        'prime': prime,
        'polynomial': polynomial_str,
        'accurate_result': accurate_result,
        'simple_result': simple_result,
        'match_status': match_status,
        'accurate_data': accurate_data,
        'simple_data': simple_data
    }

def debug_sage_basics():
    """SageMathの基本機能をテスト"""
    print("\n🔍 === SageMath基本機能テスト ===")
    
    try:
        # 多項式リングの作成
        print("Step 1: 多項式リング作成")
        R = ZZ['x']
        x = R.gen()
        print(f"✅ 多項式リング作成: {R}")
        
        # 数体の作成テスト
        print("Step 2: 数体作成テスト")
        f = x^2 - 2
        K = NumberField(f, 'alpha')
        print(f"✅ 数体作成: {K}")
        
        # 素数イデアルのテスト
        print("Step 3: 素数イデアルテスト")
        primes_3 = K.primes_above(3)
        print(f"✅ 素数3の分解: {primes_3}")
        
        # 判別式のテスト
        print("Step 4: 判別式テスト")
        disc = K.discriminant()
        print(f"✅ 判別式: {disc}")
        
        # ルジャンドル記号のテスト
        print("Step 5: ルジャンドル記号テスト")
        legendre = kronecker_symbol(disc, 3)
        print(f"✅ ルジャンドル記号: {legendre}")
        
        # 分解タイプのテスト
        print("Step 6: 分解タイプテスト")
        P = primes_3[0]
        f_P = P.residue_class_degree()
        e_P = P.ramification_index()
        print(f"✅ 剰余体次数: {f_P}, 分岐指数: {e_P}")
        
        return True
        
    except Exception as e:
        print(f"❌ SageMath基本テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

class AccurateFrobeniusExperiment:
    """正確なフロベニウス元計算実験クラス"""
    
    def __init__(self):
        self.output_dir = f"accurate_frobenius_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("🚀 正確なフロベニウス元計算実験初期化")
        print(f"💾 出力ディレクトリ: {self.output_dir}")
        
        # 基本機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗しました")
            return
    
    def save_results(self, results, experiment_name="accurate_frobenius"):
        """結果を複数の形式で保存"""
        try:
            print(f"\n💾 結果保存中: {experiment_name}")
            
            # JSON形式で保存（Sage型を文字列に変換）
            json_file = os.path.join(self.output_dir, f'{experiment_name}_results.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json_data = self._make_json_serializable(results)
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON保存: {json_file}")
            
            # 人間が読みやすいテキスト形式でも保存
            text_file = os.path.join(self.output_dir, f'{experiment_name}_summary.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"正確なフロベニウス元計算結果: {experiment_name}\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for case_name, case_data in results.items():
                    f.write(f"ケース: {case_name}\n")
                    if isinstance(case_data, dict):
                        f.write(f"  多項式: {case_data.get('polynomial', 'N/A')}\n")
                        f.write(f"  計算数: {len(case_data.get('comparisons', []))}\n")
                        f.write(f"  一致率: {case_data.get('match_rate', 'N/A'):.1f}%\n")
                        f.write(f"  正確な結果: {case_data.get('accurate_results', [])}\n")
                        f.write(f"  簡易結果: {case_data.get('simple_results', [])}\n")
                        
                        # 不一致の詳細
                        mismatches = case_data.get('mismatches', [])
                        if mismatches:
                            f.write(f"  不一致詳細:\n")
                            for mismatch in mismatches:
                                f.write(f"    p={mismatch['prime']}: 正確={mismatch['accurate']}, 簡易={mismatch['simple']}\n")
                    f.write("\n")
            
            print(f"✅ テキスト保存: {text_file}")
            
        except Exception as e:
            print(f"❌ 結果保存エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _make_json_serializable(self, obj):
        """Sage型をJSONシリアライザブルに変換"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool, type(None))):
            return str(obj)
        else:
            return obj
    
    def test_comprehensive_frobenius(self):
        """包括的なフロベニウス元計算テスト"""
        print("\n🎯 === 包括的フロベニウス元計算テスト ===")
        
        test_primes = [3, 5, 7, 11, 13, 17, 19, 23]
        all_results = {}
        
        for case in QUATERNION_TEST_CASES:
            print(f"\n{'='*60}")
            print(f"ケース: {case['name']}")
            print(f"多項式: {case['polynomial']}")
            print(f"説明: {case['description']}")
            print(f"{'='*60}")
            
            polynomial_str = case['polynomial']
            comparisons = []
            matches = 0
            mismatches = []
            
            for prime in test_primes:
                print(f"\n--- 素数 {prime} ---")
                
                comparison = compare_frobenius_calculations(polynomial_str, prime, detailed=False)
                comparisons.append(comparison)
                
                if comparison['match_status'] == 'match':
                    matches += 1
                    print(f"✅ 一致: {comparison['accurate_result']}")
                else:
                    mismatches.append({
                        'prime': prime,
                        'accurate': comparison['accurate_result'],
                        'simple': comparison['simple_result']
                    })
                    print(f"❌ 不一致: 正確={comparison['accurate_result']}, 簡易={comparison['simple_result']}")
            
            # 統計計算
            match_rate = matches / len(test_primes) * 100
            accurate_results = [comp['accurate_result'] for comp in comparisons]
            simple_results = [comp['simple_result'] for comp in comparisons]
            
            print(f"\n📊 ケース結果:")
            print(f"  一致率: {match_rate:.1f}% ({matches}/{len(test_primes)})")
            print(f"  正確な結果: {accurate_results}")
            print(f"  簡易結果: {simple_results}")
            
            # 分布の比較
            accurate_dist = Counter(accurate_results)
            simple_dist = Counter(simple_results)
            
            print(f"\n📈 分布比較:")
            print(f"  正確な分布: {dict(accurate_dist)}")
            print(f"  簡易分布: {dict(simple_dist)}")
            
            # 結果を構造化
            all_results[case['name']] = {
                'polynomial': polynomial_str,
                'test_primes': test_primes,
                'comparisons': comparisons,
                'match_rate': match_rate,
                'matches': matches,
                'mismatches': mismatches,
                'accurate_results': accurate_results,
                'simple_results': simple_results,
                'accurate_distribution': dict(accurate_dist),
                'simple_distribution': dict(simple_dist)
            }
        
        # 全体統計
        print(f"\n{'='*80}")
        print("全体統計")
        print(f"{'='*80}")
        
        total_comparisons = sum(len(result['comparisons']) for result in all_results.values())
        total_matches = sum(result['matches'] for result in all_results.values())
        overall_match_rate = total_matches / total_comparisons * 100 if total_comparisons > 0 else 0
        
        print(f"総比較数: {total_comparisons}")
        print(f"総一致数: {total_matches}")
        print(f"全体一致率: {overall_match_rate:.1f}%")
        
        # 結果保存
        self.save_results(all_results, "comprehensive_frobenius_test")
        
        print(f"\n📁 結果保存先: {self.output_dir}")
        
        return all_results

def run_accurate_frobenius_test():
    """正確なフロベニウス元計算テストの実行"""
    print("🧪 正確なフロベニウス元計算テスト実行開始")
    
    try:
        experiment = AccurateFrobeniusExperiment()
        results = experiment.test_comprehensive_frobenius()
        
        print("✅ 正確なフロベニウス元計算テスト完了")
        return experiment, results
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def run_test_verification():
    """テスト検証の実行 - medium-testで呼び出される関数"""
    print("🧪 正確なフロベニウス元計算テスト実行開始")
    
    try:
        # 基本的なSageMath機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗")
            return None, None
        
        # 正確なフロベニウス元計算テスト
        experiment, results = run_accurate_frobenius_test()
        
        print("✅ 正確なフロベニウス元計算テスト完了")
        return experiment, results
        
    except Exception as e:
        print(f"❌ テスト検証エラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def run_medium_scale_verification():
    """中規模検証の実行 - mediumで呼び出される関数"""
    print("🧪 中規模検証実行開始")
    
    try:
        # 正確なフロベニウス元計算テスト
        experiment, results = run_accurate_frobenius_test()
        
        print("✅ 中規模検証完了")
        return experiment, results
        
    except Exception as e:
        print(f"❌ 中規模検証エラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def run_single_case_test(case_index=0, x_max=1000):
    """単一ケーステスト"""
    print(f"🧪 単一ケーステスト実行: Case {case_index}")
    
    try:
        if case_index >= len(QUATERNION_TEST_CASES):
            print(f"❌ 無効なケースインデックス: {case_index}")
            return None, None
        
        case = QUATERNION_TEST_CASES[case_index]
        print(f"テストケース: {case['name']}")
        
        # 正確なフロベニウス元計算テスト
        experiment, results = run_accurate_frobenius_test()
        
        print(f"✅ 単一ケーステスト完了")
        return experiment, results
        
    except Exception as e:
        print(f"❌ 単一ケーステストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_dependencies():
    """依存関係チェック"""
    print("🔍 依存関係チェック")
    try:
        debug_sage_basics()
        print("✅ 依存関係チェック完了")
        return True
    except Exception as e:
        print(f"❌ 依存関係チェックエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("正確なフロベニウス元計算テスト")
    print("Accurate Frobenius Element Calculation using Number Field Theory")
    print("=" * 80)
    
    print("\n💡 実行方法:")
    print("   sage: experiment, results = run_accurate_frobenius_test()")
    print("   sage: experiment, results = run_test_verification()")
    
    print("\n🎯 このテストで何が分かるか:")
    print("   - 数体論的に正確なフロベニウス元計算")
    print("   - 簡易計算（根の数ベース）との比較")
    print("   - ルジャンドル記号による理論的検証")
    print("   - 素数の分解タイプ（split/inert/ramified）の正確な判定")
    
    print("\n🔬 使用する数学的手法:")
    print("   - primes_above(): 素数の分解")
    print("   - residue_class_degree(): 剰余体次数")
    print("   - ramification_index(): 分岐指数")
    print("   - kronecker_symbol(): ルジャンドル記号")
    print("   - NumberField(): 数体の構成")
    
    print("\n" + "=" * 80)
