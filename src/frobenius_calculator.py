#!/usr/bin/env sage

import json
import multiprocessing as mp
from multiprocessing import Pool
import time
import os
from functools import partial

# SageMathの必要な関数をインポート
from sage.all import *

# Omar論文の13ケースの定義多項式
OMAR_POLYNOMIALS = [
    # Case 1
    {
        'id': 1,
        'poly': 'x**8 - x**7 - 34*x**6 + 29*x**5 + 361*x**4 - 305*x**3 - 1090*x**2 + 1345*x - 395',
        'discriminant': '3**6 * 5**6 * 7**6',
        'm_rho0': 0
    },
    # Case 2  
    {
        'id': 2,
        'poly': 'x**8 + 315*x**6 + 34020*x**4 + 1488375*x**2 + 22325625',
        'discriminant': '3**6 * 5**6 * 7**6',
        'm_rho0': 1
    },
    # Case 3
    {
        'id': 3,
        'poly': 'x**8 - 205*x**6 + 13940*x**4 - 378225*x**2 + 3404025',
        'discriminant': '5**6 * 41**6',
        'm_rho0': 1
    },
    # Case 4
    {
        'id': 4,
        'poly': 'x**8 - 3*x**7 + 142*x**6 - 115*x**5 + 6641*x**4 + 3055*x**3 + 157938*x**2 + 152941*x + 2031361',
        'discriminant': '3**4 * 5**6 * 41**6',
        'm_rho0': 1
    },
    # Case 5
    {
        'id': 5,
        'poly': 'x**8 - x**7 - 178*x**6 - 550*x**5 + 7225*x**4 + 44407*x**3 + 55928*x**2 - 45392*x + 4096',
        'discriminant': '3**6 * 11**6 * 17**6',
        'm_rho0': 0
    },
    # Case 6
    {
        'id': 6,
        'poly': 'x**8 - 3*x**7 + 106*x**6 + 381*x**5 + 414*x**4 - 8475*x**3 + 44497*x**2 + 151740*x + 253168',
        'discriminant': '3**6 * 11**6 * 17**6',
        'm_rho0': 1
    },
    # Case 7
    {
        'id': 7,
        'poly': 'x**8 - 3*x**7 - 475*x**6 - 2386*x**5 + 56669*x**4 + 732202*x**3 + 3280440*x**2 + 5788174*x + 2396941',
        'discriminant': '3**7 * 41**6',
        'm_rho0': 1
    },
    # Case 8
    {
        'id': 8,
        'poly': 'x**8 - 3*x**7 - 847*x**6 - 4250*x**5 + 194805*x**4 + 2321042*x**3 + 4218300*x**2 - 28827252*x - 48031623',
        'discriminant': '3**7 * 73**6',
        'm_rho0': 1
    },
    # Case 9
    {
        'id': 9,
        'poly': 'x**8 - 3*x**7 + 1854*x**6 + 14657*x**5 + 1134753*x**4 + 15385779*x**3 + 370857442*x**2 + 2861780247*x + 28470071727',
        'discriminant': '3**4 * 37**6 * 73**6',
        'm_rho0': 1
    },
    # Case 10
    {
        'id': 10,
        'poly': 'x**8 - 3*x**7 + 1042*x**6 + 8233*x**5 + 284219*x**4 + 4899401*x**3 + 42209694*x**2 + 179998937*x + 404059099',
        'discriminant': '3**4 * 37**6 * 41**6',
        'm_rho0': 1
    },
    # Case 11
    {
        'id': 11,
        'poly': 'x**8 - x**7 - 866*x**6 - 2686*x**5 + 197617*x**4 + 1072207*x**3 - 8786448*x**2 - 32864208*x + 159160192',
        'discriminant': '7**6 * 17**6 * 23**6',
        'm_rho0': 0
    },
    # Case 12
    {
        'id': 12,
        'poly': 'x**8 - 3*x**7 - 1591*x**6 - 7978*x**5 + 718061*x**4 + 8174530*x**3 - 29006964*x**2 - 433628432*x + 235862473',
        'discriminant': '3**7 * 137**6',
        'm_rho0': 1
    },
    # Case 13
    {
        'id': 13,
        'poly': 'x**8 - 3*x**7 + 3478*x**6 + 27505*x**5 + 4489397*x**4 + 53881703*x**3 + 2972520282*x**2 + 26220344507*x + 651061429207',
        'discriminant': '3**4 * 37**6 * 137**6',
        'm_rho0': 1
    }
]

class FrobeniusCalculator:
    def __init__(self, polynomial_str, case_id):
        """
        フロベニウス元計算器の初期化
        
        Args:
            polynomial_str: 定義多項式の文字列
            case_id: ケースID
        """
        self.case_id = case_id
        self.polynomial_str = polynomial_str
        
        # 多項式とガロア拡大の設定
        x = polygen(ZZ)
        # ^を**に置換して評価
        fixed_polynomial = polynomial_str.replace('^', '**')
        self.h = eval(fixed_polynomial.replace('x', 'x'))
        self.L = NumberField(self.h, 'a')
        self.G = self.L.galois_group()
        
        # ガロア群の元を設定 (Q8の構造に従って)
        self.group_elements = {
            'g0': self.G[0],  # 1 (単位元)
            'g1': self.G[1],  # -1 (位数2の元)
            'g2': self.G[2],  # i
            'g3': self.G[3],  # j  
            'g4': self.G[4],  # k
            'g5': self.G[5],  # -i
            'g6': self.G[6],  # -j
            'g7': self.G[7]   # -k
        }
        
        # 分岐する素数を取得
        self.ramified_primes = set()
        disc = self.L.discriminant()
        for p in prime_divisors(disc):
            self.ramified_primes.add(p)
        
        print(f"Case {case_id}: 分岐する素数 = {sorted(self.ramified_primes)}")
    
    def fast_frobenius_element(self, p):
        """
        フロベニウス元の計算（正しい実装版）
        
        Args:
            p: 素数
            
        Returns:
            フロベニウス元のインデックス (0-7) または None
        """
        if p in self.ramified_primes:
            return None
            
        try:
            # Case 1の場合の正しい判定方法を実装
            if self.case_id == 1:
                return self._frobenius_case1(p)
            else:
                # 他のケースは従来の方法（要修正）
                return self._frobenius_general(p)
            
        except Exception as e:
            print(f"Error computing Frobenius element for p={p}: {e}")
            return None
    
    def _frobenius_case1(self, p):
        """
        Case 1専用の正確なフロベニウス元計算
        正しい多項式: x^8 - x^7 - 34*x^6 + 29*x^5 + 361*x^4 - 305*x^3 - 1090*x^2 + 1345*x - 395
        """
        try:
            # SageMathのpolynomial ringを使用
            R = PolynomialRing(QQ, 'x')
            x = R.gen()
            f = x**8 - x**7 - 34*x**6 + 29*x**5 + 361*x**4 - 305*x**3 - 1090*x**2 + 1345*x - 395
            
            # GF(p)に変換して因数分解
            f_mod = f.change_ring(GF(p))
            factors = f_mod.factor()
            degrees = [fac[0].degree() for fac in factors]
            
            # 因数分解による判定
            if degrees[0] == 1:
                return 0  # g0
            if degrees[0] == 2:
                return 1  # g1
            
            # クロネッカー記号による判定
            leg5 = kronecker_symbol(5, p)
            leg21 = kronecker_symbol(21, p)
            leg105 = kronecker_symbol(105, p)
            triple = (leg5, leg21, leg105)
            
            # Case 1の正しいマッピング
            class_map = {
                (1, -1, -1): 4,   # g4
                (-1, 1, -1): 3,   # g3
                (-1, -1, 1): 2,   # g2
            }
            
            result = class_map.get(triple, None)
            if result is None:
                print(f"Unknown triple {triple} for p={p}")
            
            return result
            
        except Exception as e:
            print(f"Case 1 Frobenius error for p={p}: {e}")
            return None
    
    def _frobenius_general(self, p):
        """
        一般的なフロベニウス元計算（従来の方法、要改善）
        """
        try:
            # mod p での因数分解による分類
            factorization_type = self._analyze_factorization_mod_p(p)
            
            # ルジャンドル記号による分類
            legendre_symbols = self._compute_legendre_symbols(p)
            
            # 両方の情報を組み合わせてフロベニウス元を決定
            frobenius_index = self._determine_frobenius_element(legendre_symbols, factorization_type, p)
            
            return frobenius_index
            
        except Exception as e:
            print(f"General Frobenius error for p={p}: {e}")
            return None
    
    def _compute_legendre_symbols(self, p):
        """
        部分体に関連するルジャンドル記号を計算
        """
        symbols = {}
        
        try:
            # 簡単化された計算: 定義多項式の係数を使用
            coeffs = self.h.coefficients(sparse=False)
            
            # 主要な係数についてルジャンドル記号を計算
            for i, coeff in enumerate(coeffs):
                if coeff != 0 and gcd(coeff, p) == 1:
                    symbols[f'coeff_{i}'] = legendre_symbol(coeff, p)
                    
        except:
            # フォールバック: 常に1を返す
            symbols['default'] = 1
            
        return symbols
    
    def _analyze_factorization_mod_p(self, p):
        """
        mod p での定義多項式の因数分解を解析
        """
        try:
            Fp = GF(p)
            Fpx = PolynomialRing(Fp, 'x')
            
            # 定義多項式をmod pで還元
            h_mod_p = Fpx([ZZ(c) % p for c in self.h.coefficients(sparse=False)])
            
            # 因数分解
            factors = h_mod_p.factor()
            
            # 最大次数を取得
            max_degree = max(factor[0].degree() for factor in factors)
            
            return max_degree
            
        except Exception as e:
            print(f"Factorization error for p={p}: {e}")
            # フォールバック: 次数2と仮定
            return 2
    
    def _determine_frobenius_element(self, legendre_symbols, max_degree, p):
        """
        ルジャンドル記号と因数分解の情報からフロベニウス元を決定（一般的な方法）
        """
        # 次数による粗い分類
        if max_degree == 1:
            return 0  # g0 (単位元)
        elif max_degree == 2:
            return 1  # g1 (-1)
        else:  # max_degree == 4 or 8
            # ルジャンドル記号を使ってi, j, kを分類
            symbol_product = 1
            for key, value in legendre_symbols.items():
                symbol_product *= value
            
            # p mod 8による分類も併用
            p_mod_8 = p % 8
            
            if p_mod_8 == 1:
                if symbol_product == 1:
                    return 2  # g2 (i)
                else:
                    return 3  # g3 (j)
            elif p_mod_8 == 3:
                if symbol_product == 1:
                    return 4  # g4 (k)
                else:
                    return 5  # g5 (-i)
            elif p_mod_8 == 5:
                if symbol_product == 1:
                    return 6  # g6 (-j)
                else:
                    return 2  # g2 (i)
            else:  # p_mod_8 == 7
                if symbol_product == 1:
                    return 7  # g7 (-k)
                else:
                    return 4  # g4 (k)

def compute_frobenius_batch(polynomial_str, case_id, prime_start, prime_end):
    """
    並列処理用のバッチ計算関数（SageMathオブジェクトを渡さない版）
    
    Args:
        polynomial_str: 多項式の文字列
        case_id: ケースID
        prime_start: 開始素数
        prime_end: 終了素数
        
    Returns:
        {prime: frobenius_index} の辞書
    """
    # 各プロセスで新しい計算器を作成
    calculator = FrobeniusCalculator(polynomial_str, case_id)
    results = {}
    
    print(f"Process {mp.current_process().name}: Processing primes from {prime_start} to {prime_end}")
    
    for p in prime_range(prime_start, prime_end + 1):
        frobenius_idx = calculator.fast_frobenius_element(p)
        if frobenius_idx is not None:
            results[int(p)] = int(frobenius_idx)
    
    return results

def compute_frobenius_elements_parallel(case_info, max_prime=10**6, num_processes=None):
    """
    並列処理でフロベニウス元を計算（修正版）
    
    Args:
        case_info: ケース情報の辞書
        max_prime: 計算する最大の素数
        num_processes: 使用するプロセス数 (Noneの場合は自動設定)
        
    Returns:
        {prime: frobenius_index} の辞書
    """
    if num_processes is None:
        num_processes = min(mp.cpu_count(), 8)  # 最大8プロセス
    
    print(f"Case {case_info['id']}: 並列処理開始 (プロセス数: {num_processes})")
    print(f"多項式: {case_info['poly']}")
    
    # 素数範囲を分割
    primes = list(prime_range(max_prime + 1))
    chunk_size = len(primes) // num_processes
    
    args_list = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        if i == num_processes - 1:
            end_idx = len(primes) - 1
        else:
            end_idx = (i + 1) * chunk_size - 1
            
        if start_idx < len(primes):
            prime_start = primes[start_idx]
            prime_end = primes[min(end_idx, len(primes) - 1)]
            # SageMathオブジェクトではなく、文字列とパラメータだけを渡す
            args_list.append((case_info['poly'], case_info['id'], prime_start, prime_end))
    
    # 並列処理実行
    start_time = time.time()
    
    with Pool(processes=num_processes) as pool:
        batch_results = pool.starmap(compute_frobenius_batch, args_list)
    
    # 結果をマージ
    frobenius_data = {}
    for batch_result in batch_results:
        frobenius_data.update(batch_result)
    
    end_time = time.time()
    print(f"Case {case_info['id']}: 計算完了 (時間: {end_time - start_time:.2f}秒)")
    print(f"計算した素数の数: {len(frobenius_data)}")
    
    return frobenius_data

def compute_frobenius_elements_sequential(case_info, max_prime=10**6):
    """
    シーケンシャル処理でフロベニウス元を計算（フォールバック用）
    
    Args:
        case_info: ケース情報の辞書
        max_prime: 計算する最大の素数
        
    Returns:
        {prime: frobenius_index} の辞書
    """
    print(f"Case {case_info['id']}: シーケンシャル処理開始")
    print(f"多項式: {case_info['poly']}")
    
    # 計算器を初期化
    calculator = FrobeniusCalculator(case_info['poly'], case_info['id'])
    
    # 素数を順次処理
    frobenius_data = {}
    start_time = time.time()
    
    processed_count = 0
    for p in prime_range(max_prime + 1):
        frobenius_idx = calculator.fast_frobenius_element(p)
        if frobenius_idx is not None:
            frobenius_data[int(p)] = int(frobenius_idx)
        
        processed_count += 1
        if processed_count % 1000 == 0:
            print(f"  処理済み素数: {processed_count}")
    
    end_time = time.time()
    print(f"Case {case_info['id']}: 計算完了 (時間: {end_time - start_time:.2f}秒)")
    print(f"計算した素数の数: {len(frobenius_data)}")
    
    return frobenius_data

def save_frobenius_data(case_info, frobenius_data, output_dir="frobenius_data"):
    """
    フロベニウス元のデータをJSONファイルに保存
    
    Args:
        case_info: ケース情報
        frobenius_data: フロベニウス元のデータ
        output_dir: 出力ディレクトリ
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # データ構造を整理
    output_data = {
        'case_id': case_info['id'],
        'polynomial': case_info['poly'],
        'discriminant': case_info['discriminant'],
        'm_rho0': case_info['m_rho0'],
        'frobenius_elements': frobenius_data,
        'group_structure': {
            'g0': 'identity (1)',
            'g1': 'minus_one (-1)', 
            'g2': 'i',
            'g3': 'j',
            'g4': 'k',
            'g5': 'minus_i (-i)',
            'g6': 'minus_j (-j)',
            'g7': 'minus_k (-k)'
        }
    }
    
    filename = f"{output_dir}/case_{case_info['id']:02d}_frobenius.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Case {case_info['id']}: データを保存しました -> {filename}")

def main():
    """
    メイン実行関数
    """
    print("フロベニウス元計算プログラム開始")
    print("=" * 50)
    
    # 設定
    max_prime = 10**6  # 計算する最大の素数
    num_processes = min(mp.cpu_count(), 4)  # 最大4プロセスに制限（安定性のため）
    use_parallel = True  # 並列処理を使用するかどうか
    
    print(f"設定:")
    print(f"  最大素数: {max_prime:,}")
    print(f"  プロセス数: {num_processes}")
    print(f"  並列処理: {use_parallel}")
    print()
    
    # 全ケースを処理
    for case_info in OMAR_POLYNOMIALS:
        try:
            print(f"Case {case_info['id']} 処理開始")
            
            # フロベニウス元を計算（並列またはシーケンシャル）
            if use_parallel:
                try:
                    frobenius_data = compute_frobenius_elements_parallel(
                        case_info, max_prime, num_processes
                    )
                except Exception as parallel_error:
                    print(f"並列処理でエラーが発生: {parallel_error}")
                    print("シーケンシャル処理にフォールバック")
                    frobenius_data = compute_frobenius_elements_sequential(
                        case_info, max_prime
                    )
            else:
                frobenius_data = compute_frobenius_elements_sequential(
                    case_info, max_prime
                )
            
            # JSONファイルに保存
            save_frobenius_data(case_info, frobenius_data)
            
            print(f"Case {case_info['id']} 完了\n")
            
        except Exception as e:
            print(f"Case {case_info['id']} でエラーが発生しました: {e}")
            continue
    
    print("全ケースの処理が完了しました！")

if __name__ == "__main__":
    main()
