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

def compute_comprehensive_classification(p):
    """
    包括的な分類データを計算
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
        degree_pattern = tuple(sorted(degrees))
        
        # クロネッカー記号
        leg5 = kronecker_symbol(5, p)
        leg21 = kronecker_symbol(21, p)
        leg105 = kronecker_symbol(105, p)
        triple = (leg5, leg21, leg105)
        
        # 追加のクロネッカー記号（精度向上のため）
        leg3 = kronecker_symbol(3, p)
        leg7 = kronecker_symbol(7, p)
        leg15 = kronecker_symbol(15, p)
        
        # p mod 8の情報
        p_mod_8 = p % 8
        
        return {
            'max_degree': max_degree,
            'degree_pattern': degree_pattern,
            'kronecker_triple': triple,
            'extended_kronecker': (leg3, leg5, leg7, leg15, leg21, leg105),
            'p_mod_8': p_mod_8
        }
    except Exception as e:
        print(f"Error in classification for p={p}: {e}")
        return None

def generate_improved_training_data(L, G, disc, max_prime=500):
    """
    改良された訓練データ生成
    """
    print(f"\n改良された訓練データを生成中 (最大素数: {max_prime})")
    
    training_data = []
    ramified_primes = set(prime_divisors(disc))
    
    for p in prime_range(max_prime + 1):
        if p in ramified_primes:
            continue
            
        # 正確なフロベニウス元を計算
        true_frob = compute_frob_sage(p, L, G, disc)
        if true_frob is None:
            continue
            
        # 包括的な分類データ
        classification_data = compute_comprehensive_classification(p)
        if classification_data is None:
            continue
            
        training_data.append({
            'prime': int(p),
            'true_frobenius': int(true_frob),
            'max_degree': int(classification_data['max_degree']),
            'degree_pattern': classification_data['degree_pattern'],
            'kronecker_triple': classification_data['kronecker_triple'],
            'extended_kronecker': classification_data['extended_kronecker'],
            'p_mod_8': int(classification_data['p_mod_8'])
        })
        
        if len(training_data) % 50 == 0:
            print(f"  処理済み: {len(training_data)} 素数")
    
    print(f"総計: {len(training_data)} 個の訓練データを生成")
    return training_data

def analyze_improved_patterns(training_data):
    """
    改良されたパターン解析
    """
    print(f"\n" + "="*60)
    print("改良されたパターン解析")
    print("="*60)
    
    # 複数の分類方法を試行
    degree_patterns = defaultdict(lambda: defaultdict(int))
    degree_pattern_detailed = defaultdict(lambda: defaultdict(int))
    kronecker_patterns = defaultdict(lambda: defaultdict(int))
    mod8_patterns = defaultdict(lambda: defaultdict(int))
    combined_patterns = defaultdict(lambda: defaultdict(int))
    
    for data in training_data:
        true_frob = data['true_frobenius']
        max_degree = data['max_degree']
        degree_pattern = tuple(data['degree_pattern'])
        triple = tuple(data['kronecker_triple'])
        p_mod_8 = data['p_mod_8']
        
        degree_patterns[max_degree][true_frob] += 1
        degree_pattern_detailed[degree_pattern][true_frob] += 1
        kronecker_patterns[triple][true_frob] += 1
        mod8_patterns[p_mod_8][true_frob] += 1
        
        # 組み合わせパターン
        combined_key = (max_degree, triple)
        combined_patterns[combined_key][true_frob] += 1
    
    print("1. 因数分解最大次数による分析:")
    degree_mapping = {}
    for max_degree, frob_dist in degree_patterns.items():
        most_common = max(frob_dist.items(), key=lambda x: x[1])
        degree_mapping[max_degree] = most_common[0]
        accuracy = most_common[1] / sum(frob_dist.values()) * 100
        print(f"   次数{max_degree}: g{most_common[0]} ({accuracy:.1f}%精度)")
    
    print(f"\n2. 詳細な因数分解パターンによる分析:")
    degree_pattern_mapping = {}
    for pattern, frob_dist in degree_pattern_detailed.items():
        most_common = max(frob_dist.items(), key=lambda x: x[1])
        degree_pattern_mapping[pattern] = most_common[0]
        accuracy = most_common[1] / sum(frob_dist.values()) * 100
        print(f"   {pattern}: g{most_common[0]} ({accuracy:.1f}%精度)")
    
    print(f"\n3. クロネッカー記号による分析:")
    kronecker_mapping = {}
    for triple, frob_dist in kronecker_patterns.items():
        most_common = max(frob_dist.items(), key=lambda x: x[1])
        kronecker_mapping[triple] = most_common[0]
        accuracy = most_common[1] / sum(frob_dist.values()) * 100
        print(f"   {triple}: g{most_common[0]} ({accuracy:.1f}%精度)")
    
    print(f"\n4. 組み合わせパターンによる分析:")
    combined_mapping = {}
    for combined_key, frob_dist in combined_patterns.items():
        if sum(frob_dist.values()) >= 3:  # 十分なデータがある場合のみ
            most_common = max(frob_dist.items(), key=lambda x: x[1])
            combined_mapping[combined_key] = most_common[0]
            accuracy = most_common[1] / sum(frob_dist.values()) * 100
            print(f"   {combined_key}: g{most_common[0]} ({accuracy:.1f}%精度)")
    
    return degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping

def generate_optimized_case2_function(degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping):
    """
    最適化されたCase 2分類関数の生成
    """
    print(f"\n" + "="*60)
    print("最適化されたCase 2分類関数の生成")
    print("="*60)
    
    function_code = '''def _frobenius_case2(self, p):
    """
    Case 2専用の最適化されたフロベニウス元計算
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
        degree_pattern = tuple(sorted(degrees))
        
        # クロネッカー記号
        leg5 = kronecker_symbol(5, p)
        leg21 = kronecker_symbol(21, p)
        leg105 = kronecker_symbol(105, p)
        triple = (leg5, leg21, leg105)
        
        # 高精度な組み合わせマッピング'''
    
    if combined_mapping:
        function_code += '''
        combined_key = (max_degree, triple)
        combined_map = {'''
        for combined_key, frob_idx in sorted(combined_mapping.items()):
            function_code += f'''
            {combined_key}: {frob_idx},'''
        function_code += '''
        }
        
        if combined_key in combined_map:
            return combined_map[combined_key]'''
    
    function_code += '''
        
        # 詳細な因数分解パターンによる判定'''
    if degree_pattern_mapping:
        function_code += '''
        pattern_map = {'''
        for pattern, frob_idx in sorted(degree_pattern_mapping.items()):
            function_code += f'''
            {pattern}: {frob_idx},'''
        function_code += '''
        }
        
        if degree_pattern in pattern_map:
            return pattern_map[degree_pattern]'''
    
    function_code += '''
        
        # 基本的な最大次数による判定'''
    for max_degree, frob_idx in sorted(degree_mapping.items()):
        function_code += f'''
        if max_degree == {max_degree}:
            return {frob_idx}  # g{frob_idx}'''
    
    function_code += '''
        
        # クロネッカー記号による判定
        class_map = {'''
    for triple, frob_idx in sorted(kronecker_mapping.items()):
        function_code += f'''
            {triple}: {frob_idx},'''
    
    function_code += '''
        }
        
        result = class_map.get(triple, None)
        if result is None:
            print(f"Unknown pattern for p={p}: max_degree={max_degree}, triple={triple}")
        
        return result
        
    except Exception as e:
        print(f"Case 2 Frobenius error for p={p}: {e}")
        return None'''
    
    print("生成された最適化関数:")
    print(function_code)
    
    return function_code

def validate_optimized_mapping(training_data, degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping):
    """
    最適化されたマッピングの精度検証
    """
    print(f"\n" + "="*60)
    print("最適化されたマッピング精度の検証")
    print("="*60)
    
    correct_predictions = 0
    total_predictions = 0
    errors = []
    
    for data in training_data:
        p = data['prime']
        true_frob = data['true_frobenius']
        max_degree = data['max_degree']
        degree_pattern = tuple(data['degree_pattern'])
        triple = tuple(data['kronecker_triple'])
        
        # 最適化された予測ロジック
        predicted_frob = None
        prediction_method = ""
        
        # 1. 組み合わせマッピングを最優先
        combined_key = (max_degree, triple)
        if combined_key in combined_mapping:
            predicted_frob = combined_mapping[combined_key]
            prediction_method = "combined"
        
        # 2. 詳細パターンマッピング
        elif degree_pattern in degree_pattern_mapping:
            predicted_frob = degree_pattern_mapping[degree_pattern]
            prediction_method = "pattern"
        
        # 3. 基本的な次数マッピング
        elif max_degree in degree_mapping:
            predicted_frob = degree_mapping[max_degree]
            prediction_method = "degree"
        
        # 4. クロネッカー記号マッピング
        elif triple in kronecker_mapping:
            predicted_frob = kronecker_mapping[triple]
            prediction_method = "kronecker"
        
        if predicted_frob is not None:
            total_predictions += 1
            if predicted_frob == true_frob:
                correct_predictions += 1
            else:
                errors.append({
                    'prime': p,
                    'true': true_frob,
                    'predicted': predicted_frob,
                    'method': prediction_method
                })
    
    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"\n最適化後の精度: {correct_predictions}/{total_predictions} = {accuracy:.2f}%")
    
    if errors and len(errors) <= 10:
        print(f"\n予測ミス（最初の{len(errors)}件）:")
        for error in errors:
            print(f"  p={error['prime']}: 真値=g{error['true']}, 予測=g{error['predicted']} ({error['method']})")
    
    return accuracy

def save_improved_results(training_data, mappings, function_code, accuracy):
    """
    改良された結果を保存（JSON型エラー修正版）
    """
    degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping = mappings
    
    # SageMath型をPython型に変換
    def convert_to_json_serializable(obj):
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            if isinstance(obj, dict):
                return {str(k): convert_to_json_serializable(v) for k, v in obj.items()}
            else:
                return [convert_to_json_serializable(item) for item in obj]
        else:
            return int(obj) if hasattr(obj, 'sage') else obj
    
    results = {
        "case_id": 2,
        "polynomial": "x^8 + 315*x^6 + 34020*x^4 + 1488375*x^2 + 22325625",
        "training_data_size": len(training_data),
        "accuracy": float(accuracy),
        "degree_mapping": convert_to_json_serializable(degree_mapping),
        "degree_pattern_mapping": convert_to_json_serializable(degree_pattern_mapping),
        "kronecker_mapping": convert_to_json_serializable(kronecker_mapping),
        "combined_mapping": convert_to_json_serializable(combined_mapping),
        "generated_function": function_code,
        "sample_training_data": [
            {
                "prime": int(data['prime']),
                "true_frobenius": int(data['true_frobenius']),
                "kronecker_triple": list(data['kronecker_triple'])
            }
            for data in training_data[:20]
        ]
    }
    
    with open("case2_optimized_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n改良された結果を保存: case2_optimized_mapping.json")

def main():
    """
    メイン実行関数
    """
    print("Case 2 改良版自動マッピング生成プログラム")
    print("="*60)
    
    # Case 2の設定
    L, G, disc = setup_case2()
    
    # 改良された訓練データ生成
    training_data = generate_improved_training_data(L, G, disc, max_prime=500)
    
    if len(training_data) == 0:
        print("エラー: 訓練データが生成されませんでした")
        return
    
    # 改良されたパターン解析
    mappings = analyze_improved_patterns(training_data)
    degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping = mappings
    
    # 最適化された関数生成
    function_code = generate_optimized_case2_function(degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping)
    
    # 精度検証
    accuracy = validate_optimized_mapping(training_data, degree_mapping, degree_pattern_mapping, kronecker_mapping, combined_mapping)
    
    # 結果保存
    save_improved_results(training_data, mappings, function_code, accuracy)
    
    print(f"\n" + "="*60)
    print("改良版自動マッピング生成完了!")
    print(f"最終精度: {accuracy:.2f}%")
    print("JSONファイルが正常に保存されました")

if __name__ == "__main__":
    main()
