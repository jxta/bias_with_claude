#!/usr/bin/env sage

"""
中規模実験システム (デバッグ強化版)
正確なフロベニウス元計算のデバッグとフォールバック

特徴:
- 段階的なエラーハンドリング
- フォールバック機能
- 詳細なデバッグ出力

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
更新: デバッグ強化版
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

# テストケース（単純化）
SIMPLE_TEST_CASES = [
    {
        'name': 'Test Case 1 (x^2 - 2)',
        'polynomial': 'x**2 - 2',
        'description': '√2の最小多項式'
    },
    {
        'name': 'Test Case 2 (x^2 - 3)', 
        'polynomial': 'x**2 - 3',
        'description': '√3の最小多項式'
    },
    {
        'name': 'Test Case 3 (x^2 + 1)',
        'polynomial': 'x**2 + 1',
        'description': 'iの最小多項式'
    }
]

def test_basic_numberfield():
    """基本的な数体機能のテスト"""
    print("\n🔬 === 基本数体機能テスト ===")
    
    try:
        # 最も基本的なケース
        print("Step 1: QQ[x]の作成")
        QQ_x = QQ['x']
        x = QQ_x.gen()
        print(f"✅ 成功: {QQ_x}")
        
        print("Step 2: 多項式の作成")
        f = x**2 - 2
        print(f"✅ 成功: {f}")
        
        print("Step 3: 既約性チェック")
        is_irreducible = f.is_irreducible()
        print(f"✅ 既約性: {is_irreducible}")
        
        print("Step 4: 数体の作成")
        K = NumberField(f, 'alpha')
        print(f"✅ 成功: {K}")
        
        print("Step 5: 判別式の計算")
        disc = K.discriminant()
        print(f"✅ 判別式: {disc}")
        
        print("Step 6: 素数分解のテスト")
        primes_3 = K.primes_above(3)
        print(f"✅ 素数3の分解: {primes_3}")
        print(f"✅ 素数イデアル数: {len(primes_3)}")
        
        print("Step 7: ルジャンドル記号のテスト")
        legendre = kronecker_symbol(disc, 3)
        print(f"✅ ルジャンドル記号 ({disc}/3): {legendre}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本数体機能テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_frobenius_safe(polynomial_str, prime):
    """安全なフロベニウス元計算（段階的エラーハンドリング）"""
    print(f"\n🛡️ === 安全なフロベニウス元計算 (p={prime}) ===")
    
    try:
        # Phase 1: 多項式の準備
        print("Phase 1: 多項式の準備")
        QQ_x = QQ['x']
        x = QQ_x.gen()
        
        # 多項式の作成
        polynomial_str = polynomial_str.replace('^', '**')
        f = eval(polynomial_str)
        print(f"  多項式: {f}")
        
        # 既約性チェック
        if not f.is_irreducible():
            print(f"  ⚠️ 多項式が既約でありません")
            return "reducible", {"error": "not_irreducible"}
        print(f"  ✅ 既約性確認")
        
        # Phase 2: 数体の作成
        print("Phase 2: 数体の作成")
        K = NumberField(f, 'alpha')
        print(f"  数体: {K}")
        
        # 判別式
        disc = K.discriminant()
        print(f"  判別式: {disc}")
        
        # Phase 3: 分岐チェック
        print("Phase 3: 分岐チェック")
        if disc % prime == 0:
            print(f"  ⚠️ 素数{prime}は分岐します")
            return "ramified", {"discriminant": disc, "prime": prime}
        print(f"  ✅ 分岐なし")
        
        # Phase 4: 素数分解
        print("Phase 4: 素数分解")
        primes_above = K.primes_above(prime)
        print(f"  素数イデアル: {primes_above}")
        print(f"  素数イデアル数: {len(primes_above)}")
        
        if not primes_above:
            print(f"  ❌ 素数イデアルが見つかりません")
            return "error", {"error": "no_primes_above"}
        
        # Phase 5: フロベニウス元の決定
        print("Phase 5: フロベニウス元の決定")
        
        # 簡単な分類
        if len(primes_above) == 2:
            frobenius_element = "1"  # 完全分解
            frobenius_type = "split"
        elif len(primes_above) == 1:
            P = primes_above[0]
            if P.ramification_index() == 1:
                frobenius_element = "sigma"  # 不活性
                frobenius_type = "inert"
            else:
                frobenius_element = "ramified"  # 分岐
                frobenius_type = "ramified"
        else:
            frobenius_element = "unknown"
            frobenius_type = "unknown"
        
        print(f"  → フロベニウス元: {frobenius_element}")
        print(f"  → 分解タイプ: {frobenius_type}")
        
        # Phase 6: ルジャンドル記号による検証
        print("Phase 6: ルジャンドル記号による検証")
        legendre = kronecker_symbol(disc, prime)
        print(f"  ルジャンドル記号: {legendre}")
        
        # 予想との比較
        if legendre == 1:
            expected = "split"
        elif legendre == -1:
            expected = "inert"
        else:
            expected = "ramified"
        
        print(f"  理論的予想: {expected}")
        print(f"  実際の結果: {frobenius_type}")
        
        if expected == frobenius_type:
            print(f"  ✅ 理論と一致")
        else:
            print(f"  ❌ 理論と不一致")
        
        return frobenius_element, {
            'polynomial': str(f),
            'discriminant': disc,
            'prime': prime,
            'frobenius_element': frobenius_element,
            'frobenius_type': frobenius_type,
            'legendre_symbol': legendre,
            'expected_type': expected,
            'theory_match': expected == frobenius_type
        }
        
    except Exception as e:
        print(f"❌ 安全計算エラー: {e}")
        import traceback
        traceback.print_exc()
        return "error", {"error": str(e), "polynomial": polynomial_str, "prime": prime}

def calculate_frobenius_fallback(polynomial_str, prime):
    """フォールバック用の簡易フロベニウス元計算"""
    print(f"\n🔄 === フォールバック計算 (p={prime}) ===")
    
    try:
        # 有限体での根の計算
        R = ZZ['x']
        x = R.gen()
        
        # 多項式の作成
        polynomial_str = polynomial_str.replace('^', '**')
        f = eval(polynomial_str)
        
        # 有限体上での計算
        K = GF(prime)
        R_K = K['x']
        f_p = R_K(f)
        
        # 根の計算
        roots = f_p.roots()
        num_roots = len(roots)
        
        print(f"  多項式: {f_p}")
        print(f"  根の数: {num_roots}")
        
        # 分類
        if num_roots == 0:
            frobenius = "sigma"  # 不活性
        elif num_roots == 2:
            frobenius = "1"  # 完全分解
        else:
            frobenius = "unknown"
        
        print(f"  → フォールバック結果: {frobenius}")
        
        return frobenius, {
            'polynomial': str(f_p),
            'num_roots': num_roots,
            'classification': frobenius
        }
        
    except Exception as e:
        print(f"❌ フォールバック計算エラー: {e}")
        return "error", {"error": str(e)}

class RobustFrobeniusExperiment:
    """堅牢なフロベニウス元計算実験クラス"""
    
    def __init__(self):
        self.output_dir = f"robust_frobenius_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("🚀 堅牢なフロベニウス元計算実験初期化")
        print(f"💾 出力ディレクトリ: {self.output_dir}")
        
        # 基本機能テスト
        if not test_basic_numberfield():
            print("❌ 基本数体機能テストに失敗しました")
            print("⚠️ フォールバックモードで継続します")
    
    def test_single_case_robust(self, case_index=0):
        """単一ケースの堅牢なテスト"""
        if case_index >= len(SIMPLE_TEST_CASES):
            print(f"❌ 無効なケースインデックス: {case_index}")
            return None
        
        case = SIMPLE_TEST_CASES[case_index]
        print(f"\n{'='*60}")
        print(f"堅牢テスト: {case['name']}")
        print(f"多項式: {case['polynomial']}")
        print(f"{'='*60}")
        
        test_primes = [3, 5, 7, 11, 13]
        results = []
        successful = 0
        
        for prime in test_primes:
            print(f"\n--- 素数 {prime} ---")
            
            # 安全な計算を試行
            safe_result, safe_data = calculate_frobenius_safe(case['polynomial'], prime)
            
            if safe_result != "error":
                results.append([prime, safe_result])
                successful += 1
                print(f"✅ 安全計算成功: {safe_result}")
            else:
                # フォールバックを試行
                print("🔄 フォールバックモードに切り替え")
                fallback_result, fallback_data = calculate_frobenius_fallback(case['polynomial'], prime)
                
                if fallback_result != "error":
                    results.append([prime, fallback_result])
                    successful += 1
                    print(f"✅ フォールバック成功: {fallback_result}")
                else:
                    print(f"❌ 計算失敗: p={prime}")
        
        # 統計
        print(f"\n📊 ケース結果:")
        print(f"  成功: {successful}/{len(test_primes)}")
        print(f"  結果: {results}")
        
        if results:
            frobenius_dist = Counter(elem for _, elem in results)
            print(f"  分布: {dict(frobenius_dist)}")
        
        # 結果を構造化
        case_result = {
            case['name']: {
                'polynomial': case['polynomial'],
                'test_primes': test_primes,
                'results': results,
                'successful': successful,
                'failed': len(test_primes) - successful,
                'success_rate': successful / len(test_primes) * 100,
                'frobenius_distribution': dict(Counter(elem for _, elem in results)) if results else {}
            }
        }
        
        # 結果保存
        self.save_results(case_result, f"robust_test_case_{case_index}")
        
        return case_result
    
    def test_all_cases_robust(self):
        """全ケースの堅牢なテスト"""
        print(f"\n{'='*80}")
        print("全ケース堅牢テスト")
        print(f"{'='*80}")
        
        all_results = {}
        
        for i, case in enumerate(SIMPLE_TEST_CASES):
            print(f"\n🧪 ケース {i+1}/{len(SIMPLE_TEST_CASES)}: {case['name']}")
            result = self.test_single_case_robust(i)
            if result:
                all_results.update(result)
        
        # 全体統計
        print(f"\n{'='*80}")
        print("全体統計")
        print(f"{'='*80}")
        
        total_tests = 0
        total_successful = 0
        
        for case_name, case_data in all_results.items():
            successful = case_data['successful']
            failed = case_data['failed']
            total = successful + failed
            
            total_tests += total
            total_successful += successful
            
            print(f"{case_name}:")
            print(f"  成功率: {case_data['success_rate']:.1f}% ({successful}/{total})")
            print(f"  分布: {case_data['frobenius_distribution']}")
        
        overall_success_rate = total_successful / total_tests * 100 if total_tests > 0 else 0
        print(f"\n全体成功率: {overall_success_rate:.1f}% ({total_successful}/{total_tests})")
        
        # 結果保存
        self.save_results(all_results, "all_cases_robust")
        
        return all_results
    
    def save_results(self, results, experiment_name):
        """結果保存"""
        try:
            print(f"\n💾 結果保存中: {experiment_name}")
            
            # JSON形式で保存
            json_file = os.path.join(self.output_dir, f'{experiment_name}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json_data = self._make_json_serializable(results)
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON保存: {json_file}")
            
            # テキストサマリー
            text_file = os.path.join(self.output_dir, f'{experiment_name}_summary.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"堅牢なフロベニウス元計算結果: {experiment_name}\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for case_name, case_data in results.items():
                    f.write(f"ケース: {case_name}\n")
                    f.write(f"  多項式: {case_data.get('polynomial', 'N/A')}\n")
                    f.write(f"  成功率: {case_data.get('success_rate', 0):.1f}%\n")
                    f.write(f"  結果: {case_data.get('results', [])}\n")
                    f.write(f"  分布: {case_data.get('frobenius_distribution', {})}\n")
                    f.write("\n")
            
            print(f"✅ テキスト保存: {text_file}")
            
        except Exception as e:
            print(f"❌ 結果保存エラー: {e}")
    
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

def run_robust_frobenius_test():
    """堅牢なフロベニウス元計算テストの実行"""
    print("🧪 堅牢なフロベニウス元計算テスト実行開始")
    
    try:
        experiment = RobustFrobeniusExperiment()
        results = experiment.test_all_cases_robust()
        
        print("✅ 堅牢なフロベニウス元計算テスト完了")
        return experiment, results
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def run_test_verification():
    """テスト検証の実行 - medium-testで呼び出される関数"""
    print("🧪 堅牢なフロベニウス元計算テスト実行開始")
    
    try:
        # 基本的な数体機能テスト
        if not test_basic_numberfield():
            print("❌ 基本数体機能テストに失敗")
            print("⚠️ フォールバックモードで継続")
        
        # 堅牢なフロベニウス元計算テスト
        experiment, results = run_robust_frobenius_test()
        
        print("✅ 堅牢なフロベニウス元計算テスト完了")
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
        # 堅牢なフロベニウス元計算テスト
        experiment, results = run_robust_frobenius_test()
        
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
        experiment = RobustFrobeniusExperiment()
        result = experiment.test_single_case_robust(case_index)
        
        print(f"✅ 単一ケーステスト完了")
        return experiment, result
        
    except Exception as e:
        print(f"❌ 単一ケーステストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_dependencies():
    """依存関係チェック"""
    print("🔍 依存関係チェック")
    try:
        test_basic_numberfield()
        print("✅ 依存関係チェック完了")
        return True
    except Exception as e:
        print(f"❌ 依存関係チェックエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("堅牢なフロベニウス元計算テスト")
    print("Robust Frobenius Element Calculation with Error Handling")
    print("=" * 80)
    
    print("\n💡 実行方法:")
    print("   sage: experiment, results = run_robust_frobenius_test()")
    print("   sage: experiment, results = run_test_verification()")
    
    print("\n🎯 このテストで何が分かるか:")
    print("   - 段階的エラーハンドリングによる問題の特定")
    print("   - フォールバック機能による計算の継続")
    print("   - 数体計算の各段階での成功/失敗")
    print("   - 理論的予測との比較")
    
    print("\n🛡️ 堅牢性の特徴:")
    print("   - 段階的計算による問題の早期発見")
    print("   - フォールバック機能による計算継続")
    print("   - 詳細なエラー報告")
    print("   - 部分的成功でも有用な結果を取得")
    
    print("\n" + "=" * 80)
