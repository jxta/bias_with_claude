#!/usr/bin/env sage

import json
from collections import defaultdict
from sage.all import *

def analyze_degree4_deeper():
    """
    次数4の更なる詳細分析
    """
    print("次数4の詳細分析プログラム")
    print("="*50)
    
    # Case 2の設定
    x = polygen(ZZ)
    h = x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625
    L = NumberField(h, 'a')
    G = L.galois_group()
    disc = L.discriminant()
    ramified_primes = set(prime_divisors(disc))
    
    print(f"Case 2設定完了")
    
    # データ収集
    degree4_data = []
    
    for p in prime_range(500):
        if p in ramified_primes:
            continue
            
        try:
            # 正確なフロベニウス元
            P = L.primes_above(p)[0]
            frob = G.artin_symbol(P)
            true_frob = None
            for i, g in enumerate(G):
                if g == frob:
                    true_frob = i
                    break
            
            if true_frob is None:
                continue
                
            # 因数分解
            R = PolynomialRing(QQ, 'x')
            x_var = R.gen()
            f = x_var**8 + 315*x_var**6 + 34020*x_var**4 + 1488375*x_var**2 + 22325625
            f_mod = f.change_ring(GF(p))
            factors = f_mod.factor()
            degrees = [int(fac[0].degree()) for fac in factors]
            max_degree = max(degrees)
            
            if max_degree == 4:
                # 詳細情報を収集
                data = {
                    'p': int(p),
                    'true_frob': int(true_frob),
                    'degrees': degrees,
                    'num_factors': len(degrees),
                    'leg5': int(kronecker_symbol(5, p)),
                    'leg21': int(kronecker_symbol(21, p)),
                    'leg105': int(kronecker_symbol(105, p)),
                    'leg3': int(kronecker_symbol(3, p)),
                    'leg7': int(kronecker_symbol(7, p)),
                    'leg15': int(kronecker_symbol(15, p)),
                    'leg35': int(kronecker_symbol(35, p)),
                    'p_mod_8': int(p % 8),
                    'p_mod_16': int(p % 16),
                    'p_mod_24': int(p % 24),
                    'p_mod_105': int(p % 105)
                }
                degree4_data.append(data)
                
        except Exception as e:
            continue
    
    print(f"次数4のデータ: {len(degree4_data)}個")
    
    # g1とg3の分離分析
    g1_data = [d for d in degree4_data if d['true_frob'] == 1]
    g3_data = [d for d in degree4_data if d['true_frob'] == 3]
    
    print(f"g1: {len(g1_data)}個, g3: {len(g3_data)}個")
    
    # 各特徴でg1/g3を分離できるかテスト
    features_to_test = [
        'leg3', 'leg7', 'leg15', 'leg35', 
        'p_mod_8', 'p_mod_16', 'p_mod_24', 'p_mod_105'
    ]
    
    print(f"\n特徴別分離性能:")
    best_features = []
    
    for feature in features_to_test:
        g1_values = [d[feature] for d in g1_data]
        g3_values = [d[feature] for d in g3_data]
        
        g1_counts = defaultdict(int)
        g3_counts = defaultdict(int)
        
        for val in g1_values:
            g1_counts[val] += 1
        for val in g3_values:
            g3_counts[val] += 1
        
        # 分離性能を計算
        total_correct = 0
        total_count = len(g1_data) + len(g3_data)
        
        all_values = set(g1_values + g3_values)
        feature_map = {}
        
        for val in all_values:
            g1_count = g1_counts[val]
            g3_count = g3_counts[val]
            
            if g1_count > g3_count:
                feature_map[val] = 1
                total_correct += g1_count
            else:
                feature_map[val] = 3
                total_correct += g3_count
        
        accuracy = total_correct / total_count * 100
        print(f"  {feature}: {accuracy:.1f}% (マップ: {dict(feature_map)})")
        
        if accuracy > 60:
            best_features.append((feature, accuracy, feature_map))
    
    # 組み合わせテスト
    print(f"\n組み合わせテスト:")
    
    # クロネッカー記号 + 他の特徴
    for feature, acc, feature_map in best_features:
        combined_correct = 0
        combined_total = 0
        combined_map = {}
        
        for d in degree4_data:
            triple = (d['leg5'], d['leg21'], d['leg105'])
            feature_val = d[feature]
            combined_key = (triple, feature_val)
            true_frob = d['true_frob']
            
            if combined_key not in combined_map:
                # この組み合わせの統計を計算
                same_combo = [x for x in degree4_data 
                             if (x['leg5'], x['leg21'], x['leg105']) == triple 
                             and x[feature] == feature_val]
                
                frob_counts = defaultdict(int)
                for x in same_combo:
                    frob_counts[x['true_frob']] += 1
                
                if frob_counts:
                    predicted = max(frob_counts.items(), key=lambda x: x[1])[0]
                    combined_map[combined_key] = predicted
            
            if combined_key in combined_map:
                combined_total += 1
                if combined_map[combined_key] == true_frob:
                    combined_correct += 1
        
        if combined_total > 0:
            combined_accuracy = combined_correct / combined_total * 100
            print(f"  Kronecker + {feature}: {combined_accuracy:.1f}%")
            
            if combined_accuracy > 70:
                print(f"    🎉 高精度発見! マッピング:")
                for key, val in sorted(combined_map.items()):
                    print(f"      {key}: g{val}")
    
    return degree4_data

def test_enhanced_classifier():
    """
    強化された分類器をテスト
    """
    degree4_data = analyze_degree4_deeper()
    
    # 最良の組み合わせを実装
    print(f"\n強化された分類器の実装:")
    
    enhanced_code = '''def _frobenius_case2_enhanced(self, p):
    """
    Case 2専用の強化されたフロベニウス元計算
    """
    try:
        R = PolynomialRing(QQ, 'x')
        x = R.gen()
        f = x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625
        
        f_mod = f.change_ring(GF(p))
        factors = f_mod.factor()
        degrees = [fac[0].degree() for fac in factors]
        max_degree = max(degrees)
        
        if max_degree == 1:
            return 0  # g0
        elif max_degree == 2:
            return 1  # g1
        elif max_degree == 4:
            # 次数4の強化判定
            leg5 = kronecker_symbol(5, p)
            leg21 = kronecker_symbol(21, p)
            leg105 = kronecker_symbol(105, p)
            triple = (leg5, leg21, leg105)
            
            # 追加の判定要素
            leg3 = kronecker_symbol(3, p)
            p_mod_8 = p % 8
            
            # 強化されたマッピング（実際のデータから決定）
            enhanced_map = {
                # (triple, leg3, p_mod_8): frobenius_element
                # この部分は実際の分析結果で埋める
            }
            
            enhanced_key = (triple, leg3, p_mod_8)
            if enhanced_key in enhanced_map:
                return enhanced_map[enhanced_key]
            
            # フォールバック: 従来の方法
            if triple in [(-1, -1, 1), (-1, 1, -1), (1, -1, -1)]:
                return 3
            else:
                return 1
        
        return None
        
    except Exception as e:
        print(f"Enhanced Case 2 error for p={p}: {e}")
        return None'''
    
    print(enhanced_code)

if __name__ == "__main__":
    test_enhanced_classifier()
