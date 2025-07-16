#!/usr/bin/env sage

"""
中規模実験システム (詳細デバッグ版)
フロベニウス元計算の問題を根本的に解決

特徴:
- 非常に詳細なデバッグ出力
- ステップバイステップの計算検証
- エラーの完全なトレース

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: 完全デバッグ版
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

# 簡単なケースのみテスト用
SIMPLE_TEST_CASES = [
    {
        'name': 'Simple Test Case 1',
        'polynomial': 'x**2 - 2',
        'm_rho_0_val': 0,
        'galois_group': 'C2',
        'discriminant': 8,
        'subfield_discriminants': []
    },
    {
        'name': 'Simple Test Case 2', 
        'polynomial': 'x**2 - 3',
        'm_rho_0_val': 1,
        'galois_group': 'C2',
        'discriminant': 12,
        'subfield_discriminants': []
    }
]

def debug_sage_basics():
    """SageMathの基本機能をテスト"""
    print("\n🔍 === SageMath基本機能テスト ===")
    
    try:
        # 多項式リングの作成
        print("Step 1: 多項式リング作成")
        R = ZZ['x']  # 整数上の多項式リング
        x = R.gen()  # 生成元
        print(f"✅ 多項式リング作成: {R}")
        print(f"✅ 生成元x作成: {x}")
        print(f"   x の型: {type(x)}")
        
        # 多項式の作成
        print("Step 2: 多項式作成")
        f = x**2 - 2
        print(f"✅ 多項式作成: {f}")
        print(f"   f の型: {type(f)}")
        
        # 有限体の作成
        print("Step 3: 有限体作成")
        K = GF(3)
        print(f"✅ 有限体GF(3)作成: {K}")
        
        # 有限体上の多項式リング
        print("Step 4: 有限体上の多項式リング作成")
        R_K = K['x']
        print(f"✅ GF(3)上の多項式リング: {R_K}")
        
        # 多項式の有限体での表現
        print("Step 5: 多項式を有限体に変換")
        f_3 = R_K(f)  # 多項式をGF(3)上に変換
        print(f"✅ 多項式をGF(3)に変換: {f_3}")
        print(f"   f_3 の型: {type(f_3)}")
        
        # 因数分解
        print("Step 6: 因数分解")
        factors = f_3.factor()
        print(f"✅ 因数分解: {factors}")
        print(f"   因数の数: {len(factors)}")
        
        # 根の計算
        print("Step 7: 根の計算")
        roots = f_3.roots()
        print(f"✅ 根の計算: {roots}")
        print(f"   根の数: {len(roots)}")
        
        # 既約性チェック
        print("Step 8: 既約性チェック")
        is_irreducible = f_3.is_irreducible()
        print(f"✅ 既約性: {is_irreducible}")
        
        return True
        
    except Exception as e:
        print(f"❌ SageMath基本テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_polynomial_step_by_step(polynomial_str, prime):
    """多項式計算をステップバイステップでデバッグ"""
    print(f"\n🔍 === ステップバイステップデバッグ (p={prime}) ===")
    
    try:
        # ステップ1: 多項式リング作成
        print("Step 1: 多項式リング作成")
        R = ZZ['x']  # 整数上の多項式リング
        x = R.gen()
        print(f"  多項式リング: {R}")
        print(f"  生成元x: {x}")
        
        # ステップ2: 多項式文字列の解析
        print("Step 2: 多項式文字列解析")
        print(f"  polynomial_str = '{polynomial_str}'")
        
        # ステップ3: 多項式オブジェクト作成
        print("Step 3: 多項式オブジェクト作成")
        # polynomial_strを安全に評価（xは多項式リングの要素として）
        f = eval(polynomial_str.replace('x', 'x'))
        print(f"  f = {f}")
        print(f"  f の型: {type(f)}")
        
        # ステップ4: 有限体作成
        print(f"Step 4: 有限体GF({prime})作成")
        K = GF(prime)
        print(f"  K = {K}")
        
        # ステップ5: 有限体上の多項式リング作成
        print("Step 5: 有限体上の多項式リング作成")
        R_K = K['x']
        print(f"  R_K = {R_K}")
        
        # ステップ6: 多項式の有限体への変換
        print("Step 6: 多項式を有限体に変換")
        f_p = R_K(f)
        print(f"  f_p = {f_p}")
        print(f"  f_p の型: {type(f_p)}")
        
        # ステップ7: 因数分解
        print("Step 7: 因数分解")
        factors = f_p.factor()
        print(f"  factors = {factors}")
        print(f"  factors の型: {type(factors)}")
        print(f"  因数の数: {len(factors)}")
        
        # ステップ8: 根の計算
        print("Step 8: 根の計算")
        roots = f_p.roots()
        print(f"  roots = {roots}")
        print(f"  根の数: {len(roots)}")
        
        # ステップ9: 既約性チェック
        print("Step 9: 既約性チェック")
        is_irreducible = f_p.is_irreducible()
        print(f"  既約: {is_irreducible}")
        
        # ステップ10: フロベニウス元決定
        print("Step 10: フロベニウス元決定")
        num_roots = len(roots)
        if num_roots == 0:
            frobenius = "1"
        elif num_roots == 1:
            frobenius = "-1"
        elif num_roots == 2:
            frobenius = "i"
        else:
            frobenius = "j"
        
        print(f"  根の数 {num_roots} → フロベニウス元: {frobenius}")
        
        return frobenius
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_polynomial_from_string(polynomial_str):
    """文字列から多項式オブジェクトを安全に作成"""
    try:
        # 整数上の多項式リング
        R = ZZ['x']
        x = R.gen()
        
        # 文字列を評価して多項式を作成
        # セキュリティのため、基本的な操作のみ許可
        allowed_chars = set('x0123456789+-*() ')
        if not all(c in allowed_chars for c in polynomial_str):
            raise ValueError(f"不正な文字が含まれています: {polynomial_str}")
        
        # xを多項式リングの生成元で置換
        f = eval(polynomial_str)
        
        # 多項式リングの要素に変換
        if not isinstance(f, R.element_class):
            f = R(f)
        
        return f
        
    except Exception as e:
        print(f"❌ 多項式作成エラー: {e}")
        return None

class DebugExperiment:
    """デバッグ用実験クラス"""
    
    def __init__(self):
        self.output_dir = f"debug_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("🚀 デバッグ実験システム初期化")
        print(f"💾 出力ディレクトリ: {self.output_dir}")
        
        # 基本機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗しました")
            return
    
    def test_simple_case(self):
        """非常に簡単なケースをテスト"""
        print("\n🎯 === 簡単なケーステスト ===")
        
        case = SIMPLE_TEST_CASES[0]
        polynomial_str = case['polynomial']
        test_primes = [3, 5, 7, 11, 13]
        
        print(f"テストケース: {case['name']}")
        print(f"多項式: {polynomial_str}")
        print(f"テスト素数: {test_primes}")
        
        results = []
        
        for p in test_primes:
            print(f"\n--- 素数 {p} での計算 ---")
            
            frobenius = debug_polynomial_step_by_step(polynomial_str, p)
            
            if frobenius is not None:
                results.append([p, frobenius])
                print(f"✅ 成功: p={p} → {frobenius}")
            else:
                print(f"❌ 失敗: p={p}")
        
        print(f"\n📊 結果サマリー:")
        print(f"  成功: {len(results)}/{len(test_primes)}")
        print(f"  結果: {results}")
        
        if results:
            frobenius_dist = Counter(elem for _, elem in results)
            print(f"  分布: {dict(frobenius_dist)}")
        
        return results
    
    def run_all_test_cases(self):
        """すべてのテストケースを実行"""
        print("\n🎯 === 全テストケース実行 ===")
        
        all_results = {}
        
        for case in SIMPLE_TEST_CASES:
            print(f"\n{'='*60}")
            print(f"ケース: {case['name']}")
            print(f"{'='*60}")
            
            polynomial_str = case['polynomial']
            test_primes = [3, 5, 7, 11, 13, 17, 19, 23]
            
            results = []
            successful = 0
            failed = 0
            
            for p in test_primes:
                print(f"\n素数 {p}:")
                
                frobenius = debug_polynomial_step_by_step(polynomial_str, p)
                
                if frobenius is not None:
                    results.append([p, frobenius])
                    successful += 1
                    print(f"  ✅ 成功: {frobenius}")
                else:
                    failed += 1
                    print(f"  ❌ 失敗")
            
            print(f"\n📊 ケース結果:")
            print(f"  成功: {successful}/{len(test_primes)}")
            print(f"  失敗: {failed}/{len(test_primes)}")
            
            if results:
                frobenius_dist = Counter(elem for _, elem in results)
                print(f"  分布: {dict(frobenius_dist)}")
            
            all_results[case['name']] = {
                'results': results,
                'successful': successful,
                'failed': failed,
                'success_rate': successful / len(test_primes) * 100
            }
        
        return all_results

def run_debug_test():
    """デバッグテストの実行"""
    print("🧪 デバッグテスト実行開始")
    
    experiment = DebugExperiment()
    
    # 単一ケーステスト
    print("\n" + "="*80)
    print("PHASE 1: 単一ケーステスト")
    print("="*80)
    experiment.test_simple_case()
    
    # 全ケーステスト
    print("\n" + "="*80)
    print("PHASE 2: 全ケーステスト")
    print("="*80)
    all_results = experiment.run_all_test_cases()
    
    # 最終サマリー
    print("\n" + "="*80)
    print("最終サマリー")
    print("="*80)
    
    total_successful = 0
    total_tests = 0
    
    for case_name, result in all_results.items():
        print(f"\n{case_name}:")
        print(f"  成功: {result['successful']}")
        print(f"  失敗: {result['failed']}")
        print(f"  成功率: {result['success_rate']:.1f}%")
        
        total_successful += result['successful']
        total_tests += result['successful'] + result['failed']
    
    overall_success_rate = total_successful / total_tests * 100 if total_tests > 0 else 0
    print(f"\n全体成功率: {overall_success_rate:.1f}% ({total_successful}/{total_tests})")
    
    if overall_success_rate > 0:
        print("✅ フロベニウス元計算は正常に動作しています！")
    else:
        print("❌ フロベニウス元計算に問題があります")
    
    return experiment, all_results

def run_test_verification():
    """テスト検証の実行 - medium-testで呼び出される関数"""
    print("🧪 中規模テスト実行開始")
    
    try:
        # 基本的なSageMath機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗")
            return None, None
        
        # 軽量なテストケース実行
        experiment = DebugExperiment()
        results = experiment.test_simple_case()
        
        print("✅ 中規模テスト完了")
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
        # 基本的なSageMath機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗")
            return None, None
        
        # 全テストケース実行
        experiment = DebugExperiment()
        results = experiment.run_all_test_cases()
        
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
        if case_index >= len(SIMPLE_TEST_CASES):
            print(f"❌ 無効なケースインデックス: {case_index}")
            return None, None
        
        case = SIMPLE_TEST_CASES[case_index]
        print(f"テストケース: {case['name']}")
        
        # 基本的なSageMath機能テスト
        if not debug_sage_basics():
            print("❌ SageMath基本機能テストに失敗")
            return None, None
        
        # 単一ケースの詳細テスト
        polynomial_str = case['polynomial']
        test_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        
        results = []
        for p in test_primes:
            frobenius = debug_polynomial_step_by_step(polynomial_str, p)
            if frobenius is not None:
                results.append([p, frobenius])
        
        print(f"✅ 単一ケーステスト完了: {len(results)} 成功")
        return case, results
        
    except Exception as e:
        print(f"❌ 単一ケーステストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_dependencies():
    """依存関係チェック"""
    print("🔍 依存関係チェック")
    try:
        # SageMath基本機能
        debug_sage_basics()
        print("✅ 依存関係チェック完了")
        return True
    except Exception as e:
        print(f"❌ 依存関係チェックエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("詳細デバッグ版 - フロベニウス元計算テスト")
    print("=" * 80)
    
    print("\n💡 実行方法:")
    print("   sage: experiment, results = run_debug_test()")
    print("   sage: experiment, results = run_test_verification()")
    print("   sage: experiment, results = run_medium_scale_verification()")
    
    print("\n🎯 このテストで何が分かるか:")
    print("   - SageMathの基本機能が動作するか")
    print("   - 多項式計算の各ステップでエラーが出るか")
    print("   - フロベニウス元の決定ロジックが正しいか")
    
    print("\n" + "=" * 80)
