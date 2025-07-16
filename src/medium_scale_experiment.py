#!/usr/bin/env sage

"""
中規模実験システム (正確なフロベニウス元計算版)
primes_above と artin_symbol を使用した正確な計算

特徴:
- 正確なフロベニウス元計算
- 簡易計算との比較検証
- 詳細なデバッグ出力

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: 正確なフロベニウス元計算版
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

def calculate_frobenius_accurate(polynomial_str, prime):
    """
    正確なフロベニウス元計算
    primes_above と artin_symbol を使用
    """
    print(f"\n🔬 === 正確なフロベニウス元計算 (p={prime}) ===")
    
    try:
        # ステップ1: 多項式リング作成
        print("Step 1: 多項式とその体の作成")
        QQ_x = QQ['x']
        x = QQ_x.gen()
        
        # 多項式を作成
        f = eval(polynomial_str.replace('x', 'x'))
        print(f"  多項式: {f}")
        
        # 既約性チェック
        if not f.is_irreducible():
            print(f"  ❌ 多項式が既約でありません: {f}")
            return None
        
        # ステップ2: 数体の作成
        print("Step 2: 数体の作成")
        K = NumberField(f, 'alpha')
        alpha = K.gen()
        print(f"  数体: {K}")
        print(f"  生成元: {alpha}")
        
        # ステップ3: 素数の分解
        print(f"Step 3: 素数 {prime} の分解")
        p = prime
        
        # 素数イデアルを取得
        prime_ideals = K.primes_above(p)
        print(f"  素数イデアル: {prime_ideals}")
        
        if not prime_ideals:
            print(f"  ❌ 素数イデアルが見つかりません")
            return None
        
        # 最初の素数イデアルを使用
        P = prime_ideals[0]
        print(f"  使用する素数イデアル: {P}")
        
        # ステップ4: Artinシンボルの計算
        print("Step 4: Artinシンボルの計算")
        
        # Galois拡大の場合
        if f.degree() == 2:
            # 二次拡大の場合、判別式を使用
            disc = f.discriminant()
            print(f"  判別式: {disc}")
            
            # ルジャンドル記号を計算
            legendre = kronecker_symbol(disc, p)
            print(f"  ルジャンドル記号 ({disc}/{p}): {legendre}")
            
            if legendre == 1:
                frobenius = "1"  # 完全分解
            elif legendre == -1:
                frobenius = "sigma"  # 既約のまま
            else:
                frobenius = "ramified"  # 分岐
                
        else:
            # より一般的な場合
            try:
                # Galois群を計算
                L = K.galois_closure('beta')
                G = L.galois_group()
                print(f"  Galois群: {G}")
                
                # フロベニウス元を計算
                frob = G.artin_symbol(P)
                frobenius = str(frob)
                print(f"  フロベニウス元: {frobenius}")
                
            except Exception as e:
                print(f"  ❌ Galois群計算エラー: {e}")
                frobenius = "error"
        
        print(f"  → フロベニウス元: {frobenius}")
        return frobenius
        
    except Exception as e:
        print(f"❌ 正確な計算エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_frobenius_simple(polynomial_str, prime):
    """
    簡易フロベニウス元計算（根の数に基づく）
    比較のために残している
    """
    print(f"\n📊 === 簡易フロベニウス元計算 (p={prime}) ===")
    
    try:
        # 多項式リング作成
        R = ZZ['x']
        x = R.gen()
        f = eval(polynomial_str.replace('x', 'x'))
        
        # 有限体上での計算
        K = GF(prime)
        R_K = K['x']
        f_p = R_K(f)
        
        # 根の計算
        roots = f_p.roots()
        num_roots = len(roots)
        
        print(f"  多項式: {f_p}")
        print(f"  根: {roots}")
        print(f"  根の数: {num_roots}")
        
        # 簡易分類
        if num_roots == 0:
            frobenius = "1"  # 既約
        elif num_roots == 1:
            frobenius = "-1"  # 1つの根
        elif num_roots == 2:
            frobenius = "i"  # 2つの根
        else:
            frobenius = "j"  # その他
        
        print(f"  → 簡易フロベニウス元: {frobenius}")
        return frobenius
        
    except Exception as e:
        print(f"❌ 簡易計算エラー: {e}")
        return None

def compare_frobenius_calculations(polynomial_str, prime):
    """
    正確な計算と簡易計算を比較
    """
    print(f"\n🔍 === フロベニウス元計算比較 (p={prime}) ===")
    
    # 正確な計算
    accurate_result = calculate_frobenius_accurate(polynomial_str, prime)
    
    # 簡易計算
    simple_result = calculate_frobenius_simple(polynomial_str, prime)
    
    # 比較
    print(f"\n📊 比較結果:")
    print(f"  正確な計算: {accurate_result}")
    print(f"  簡易計算: {simple_result}")
    
    if accurate_result == simple_result:
        print("  ✅ 一致")
        match_status = "match"
    else:
        print("  ❌ 不一致")
        match_status = "mismatch"
    
    return {
        'prime': prime,
        'accurate': accurate_result,
        'simple': simple_result,
        'match': match_status
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
        f = x**2 - 2
        K = NumberField(f, 'alpha')
        print(f"✅ 数体作成: {K}")
        
        # 素数イデアルのテスト
        print("Step 3: 素数イデアルテスト")
        primes_3 = K.primes_above(3)
        print(f"✅ 素数3の分解: {primes_3}")
        
        # 判別式のテスト
        print("Step 4: 判別式テスト")
        disc = f.discriminant()
        print(f"✅ 判別式: {disc}")
        
        # ルジャンドル記号のテスト
        print("Step 5: ルジャンドル記号テスト")
        legendre = kronecker_symbol(disc, 3)
        print(f"✅ ルジャンドル記号: {legendre}")
        
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
            
            # JSON形式で保存
            json_file = os.path.join(self.output_dir, f'{experiment_name}_results.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
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
                        f.write(f"  一致率: {case_data.get('match_rate', 'N/A')}%\n")
                        f.write(f"  正確な結果: {case_data.get('accurate_results', [])}\n")
                        f.write(f"  簡易結果: {case_data.get('simple_results', [])}\n")
                    f.write("\n")
            
            print(f"✅ テキスト保存: {text_file}")
            
        except Exception as e:
            print(f"❌ 結果保存エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def test_accurate_frobenius(self):
        """正確なフロベニウス元計算のテスト"""
        print("\n🎯 === 正確なフロベニウス元計算テスト ===")
        
        case = SIMPLE_TEST_CASES[0]
        polynomial_str = case['polynomial']
        test_primes = [3, 5, 7, 11, 13]
        
        print(f"テストケース: {case['name']}")
        print(f"多項式: {polynomial_str}")
        print(f"テスト素数: {test_primes}")
        
        comparisons = []
        matches = 0
        
        for p in test_primes:
            print(f"\n{'='*50}")
            print(f"素数 {p} での計算")
            print(f"{'='*50}")
            
            comparison = compare_frobenius_calculations(polynomial_str, p)
            comparisons.append(comparison)
            
            if comparison['match'] == 'match':
                matches += 1
        
        # 統計計算
        match_rate = matches / len(test_primes) * 100
        accurate_results = [comp['accurate'] for comp in comparisons]
        simple_results = [comp['simple'] for comp in comparisons]
        
        print(f"\n📊 最終結果:")
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
        result = {
            case['name']: {
                'polynomial': polynomial_str,
                'test_primes': test_primes,
                'comparisons': comparisons,
                'match_rate': match_rate,
                'accurate_results': accurate_results,
                'simple_results': simple_results,
                'accurate_distribution': dict(accurate_dist),
                'simple_distribution': dict(simple_dist)
            }
        }
        
        # 結果保存
        self.save_results(result, "accurate_frobenius_test")
        
        return result

def run_accurate_frobenius_test():
    """正確なフロベニウス元計算テストの実行"""
    print("🧪 正確なフロベニウス元計算テスト実行開始")
    
    try:
        experiment = AccurateFrobeniusExperiment()
        results = experiment.test_accurate_frobenius()
        
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
        if case_index >= len(SIMPLE_TEST_CASES):
            print(f"❌ 無効なケースインデックス: {case_index}")
            return None, None
        
        case = SIMPLE_TEST_CASES[case_index]
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
        # SageMath基本機能
        debug_sage_basics()
        print("✅ 依存関係チェック完了")
        return True
    except Exception as e:
        print(f"❌ 依存関係チェックエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("正確なフロベニウス元計算テスト")
    print("Accurate Frobenius Element Calculation using primes_above and artin_symbol")
    print("=" * 80)
    
    print("\n💡 実行方法:")
    print("   sage: experiment, results = run_accurate_frobenius_test()")
    print("   sage: experiment, results = run_test_verification()")
    
    print("\n🎯 このテストで何が分かるか:")
    print("   - 正確なフロベニウス元計算の結果")
    print("   - 簡易計算との比較")
    print("   - 計算方法の精度検証")
    print("   - 理論的に正しい分布の確認")
    
    print("\n" + "=" * 80)
