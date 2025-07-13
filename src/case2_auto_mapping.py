#!/usr/bin/env sage

import json
from collections import defaultdict
from sage.all import *

def setup_case2():
    """
    Case 2の数体とガロア群を設定
    """
    x = polygen(ZZ)
    h = x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625
    L = NumberField(h, 'a')
    G = L.galois_group()
    disc = L.discriminant()
    
    print(f"Case 2 設定:")
    print(f"多項式: {h}")
    print(f"ガロア群: {G}")
    print(f"判別式の素因数: {prime_divisors(disc)}")
    
    return L, G, disc

def frob_label_from_element(frob_element):
    """
    フロベニウス元からラベル（インデックス）を取得
    """
    # ガロア群の元のリストでのインデックスを取得
    G = frob_element.parent()
    for i, g in enumerate(G):
        if g == frob_element:
            return i
    return None

def compute_frob_sage(p, L, G, disc):
    """
    SageMathのartin_symbolを使った正確なフロベニウス元計算
    """
    if gcd(p, disc) != 1:
        return None
    try:
        P = L.primes_above(p)[0]
        frob = G.artin_symbol(P)
        label = frob_label_from_element(frob)  
        return label
    except Exception as e:
        print(f"Error computing Frobenius for p={p}: {e}")
        return None

def compute_kronecker_classification(p):
    """
    クロネッカー記号による分類
    """
    # 因数分解パターン
    R = PolynomialRing(QQ, 'x')
    x = R.gen()
    f = x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625
    
    try:
        f_mod = f.change_ring(GF(p))
        factors = f_mod.factor()
        degrees = [fac[0].degree() for fac in factors]
        max_degree = max(degrees)
        
        # クロネッカー記号
        leg5 = kronecker_symbol(5, p)
        leg21 = kronecker_symbol(21, p)
        leg105 = kronecker_symbol(105, p)
        triple = (leg5, leg21, leg105)
        
        return {
            'max_degree': max_degree,
            'kronecker_triple': triple,
            'degrees_list': degrees
        }
    except Exception as e:
        print(f"Error in Kronecker classification for p={p}: {e}")
        return None

def generate_training_data(L, G, disc, max_prime=500):
    """
    正確なフロベニウス元と分類データの対応を生成
    """
    print(f"\n正確なフロベニウス元データを生成中 (最大素数: {max_prime})")
    
    training_data = []
    ramified_primes = set(prime_divisors(disc))
    
    for p in prime_range(max_prime + 1):
        if p in ramified_primes:
            continue
            
        # 正確なフロベニウス元を計算
        true_frob = compute_frob_sage(p, L, G, disc)
        if true_frob is None:
            continue
            
        # クロネッカー記号による分類
        kronecker_data = compute_kronecker_classification(p)
        if kronecker_data is None:
            continue
            
        training_data.append({
            'prime': p,
            'true_frobenius': true_frob,
            'max_degree': kronecker_data['max_degree'],
            'kronecker_triple': kronecker_data['kronecker_triple'],
            'degrees_list': kronecker_data['degrees_list']
        })
        
        if len(training_data) % 50 == 0:
            print(f"  処理済み: {len(training_data)} 素数")
    
    print(f"総計: {len(training_data)} 個の訓練データを生成")
    return training_data

def analyze_patterns(training_data):
    """
    パターンを解析してマッピングを決定
    """
    print(f"\n" + "="*60)
    print("パターン解析とマッピング決定")
    print("="*60)
    
    # 因数分解パターンによる分析
    degree_patterns = defaultdict(lambda: defaultdict(int))
    kronecker_patterns = defaultdict(lambda: defaultdict(int))
    
    for data in training_data:
        p = data['prime']
        true_frob = data['true_frobenius']
        max_degree = data['max_degree']
        triple = data['kronecker_triple']
        
        degree_patterns[max_degree][true_frob] += 1
        kronecker_patterns[triple][true_frob] += 1
    
    print("1. 因数分解パターンによる分析:")
    degree_mapping = {}
    for max_degree, frob_dist in degree_patterns.items():
        print(f"   最大次数 {max_degree}:")
        for frob_idx, count in sorted(frob_dist.items()):
            print(f"     g{frob_idx}: {count} 回")
        
        # 最頻出のフロベニウス元を選択
        if frob_dist:
            most_common_frob = max(frob_dist.items(), key=lambda x: x[1])
            degree_mapping[max_degree] = most_common_frob[0]
            print(f"   -> 選択: 次数{max_degree} -> g{most_common_frob[0]}")
    
    print(f"\n2. クロネッカー記号パターンによる分析:")
    kronecker_mapping = {}
    for triple, frob_dist in kronecker_patterns.items():
        print(f"   {triple}:")
        for frob_idx, count in sorted(frob_dist.items()):
            print(f"     g{frob_idx}: {count} 回")
        
        # 最頻出のフロベニウス元を選択
        if frob_dist:
            most_common_frob = max(frob_dist.items(), key=lambda x: x[1])
            kronecker_mapping[triple] = most_common_frob[0]
            print(f"   -> 選択: {triple} -> g{most_common_frob[0]}")
    
    return degree_mapping, kronecker_mapping

def generate_case2_function(degree_mapping, kronecker_mapping):
    """
    Case 2用の分類関数のコードを生成
    """
    print(f"\n" + "="*60)
    print("Case 2用分類関数の生成")
    print("="*60)
    
    function_code = '''def _frobenius_case2(self, p):
    """
    Case 2専用の正確なフロベニウス元計算
    """
    try:
        # SageMathのpolynomial ringを使用
        R = PolynomialRing(QQ, 'x')
        x = R.gen()
        f = x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625
        
        # GF(p)に変換して因数分解
        f_mod = f.change_ring(GF(p))
        factors = f_mod.factor()
        degrees = [fac[0].degree() for fac in factors]
        max_degree = max(degrees)
        
        # 因数分解による判定'''
    
    for max_degree, frob_idx in sorted(degree_mapping.items()):
        function_code += f'''
        if max_degree == {max_degree}:
            return {frob_idx}  # g{frob_idx}'''
    
    function_code += '''
        
        # クロネッカー記号による詳細判定
        leg5 = kronecker_symbol(5, p)
        leg21 = kronecker_symbol(21, p)
        leg105 = kronecker_symbol(105, p)
        triple = (leg5, leg21, leg105)
        
        # Case 2の正確なマッピング
        class_map = {'''
    
    for triple, frob_idx in sorted(kronecker_mapping.items()):
        function_code += f'''
            {triple}: {frob_idx},   # g{frob_idx}'''
    
    function_code += '''
        }
        
        result = class_map.get(triple, None)
        if result is None:
            print(f"Unknown triple {triple} for p={p}")
        
        return result
        
    except Exception as e:
        print(f"Case 2 Frobenius error for p={p}: {e}")
        return None'''
    
    print("生成された関数:")
    print(function_code)
    
    return function_code

def compare_with_case1(kronecker_mapping):
    """
    Case 1との比較
    """
    print(f"\n" + "="*60)
    print("Case 1との比較")
    print("="*60)
    
    case1_mapping = {
        (1, -1, -1): 4,   # g4
        (-1, 1, -1): 3,   # g3
        (-1, -1, 1): 2,   # g2
    }
    
    print("Case 1のマッピング:")
    for triple, frob_idx in case1_mapping.items():
        print(f"  {triple} -> g{frob_idx}")
    
    print(f"\nCase 2のマッピング:")
    for triple, frob_idx in sorted(kronecker_mapping.items()):
        print(f"  {triple} -> g{frob_idx}")
    
    print(f"\n相違点:")
    for triple in set(case1_mapping.keys()) | set(kronecker_mapping.keys()):
        case1_frob = case1_mapping.get(triple, "なし")
        case2_frob = kronecker_mapping.get(triple, "なし")
        if case1_frob != case2_frob:
            print(f"  {triple}: Case1=g{case1_frob}, Case2=g{case2_frob}")

def validate_mapping(training_data, degree_mapping, kronecker_mapping):
    """
    生成されたマッピングの精度を検証
    """
    print(f"\n" + "="*60)
    print("マッピング精度の検証")
    print("="*60)
    
    correct_predictions = 0
    total_predictions = 0
    
    for data in training_data:
        p = data['prime']
        true_frob = data['true_frobenius']
        max_degree = data['max_degree']
        triple = data['kronecker_triple']
        
        # 因数分解による予測
        predicted_frob = None
        if max_degree in degree_mapping:
            predicted_frob = degree_mapping[max_degree]
        elif triple in kronecker_mapping:
            predicted_frob = kronecker_mapping[triple]
        
        if predicted_frob is not None:
            total_predictions += 1
            if predicted_frob == true_frob:
                correct_predictions += 1
            else:
                if total_predictions <= 10:  # 最初の10個のエラーを表示
                    print(f"  予測ミス: p={p}, 真値=g{true_frob}, 予測=g{predicted_frob}")
    
    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"\n精度: {correct_predictions}/{total_predictions} = {accuracy:.2f}%")
    
    return accuracy

def save_results(training_data, degree_mapping, kronecker_mapping, function_code):
    """
    結果を保存
    """
    results = {
        "case_id": 2,
        "polynomial": "x^8 + 315*x^6 + 34020*x^4 + 1488375*x^2 + 22325625",
        "training_data_size": len(training_data),
        "degree_mapping": {str(k): int(v) for k, v in degree_mapping.items()},
        "kronecker_mapping": {str(k): int(v) for k, v in kronecker_mapping.items()},
        "generated_function": function_code,
        "sample_training_data": [
            {
                "prime": int(data['prime']),
                "true_frobenius": int(data['true_frobenius']),
                "kronecker_triple": data['kronecker_triple']
            }
            for data in training_data[:20]  # 最初の20個をサンプルとして保存
        ]
    }
    
    with open("case2_auto_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果を保存: case2_auto_mapping.json")

def main():
    """
    メイン実行関数
    """
    print("Case 2 自動マッピング生成プログラム")
    print("="*60)
    
    # Case 2の設定
    L, G, disc = setup_case2()
    
    # 訓練データ生成
    training_data = generate_training_data(L, G, disc, max_prime=500)
    
    if len(training_data) == 0:
        print("エラー: 訓練データが生成されませんでした")
        return
    
    # パターン解析
    degree_mapping, kronecker_mapping = analyze_patterns(training_data)
    
    # 関数生成
    function_code = generate_case2_function(degree_mapping, kronecker_mapping)
    
    # Case 1との比較
    compare_with_case1(kronecker_mapping)
    
    # 精度検証
    accuracy = validate_mapping(training_data, degree_mapping, kronecker_mapping)
    
    # 結果保存
    save_results(training_data, degree_mapping, kronecker_mapping, function_code)
    
    print(f"\n" + "="*60)
    print("自動マッピング生成完了!")
    print(f"精度: {accuracy:.2f}%")
    print("次のステップ: 生成された関数をfrobenius_calculator.pyに組み込んでください")

if __name__ == "__main__":
    main()
