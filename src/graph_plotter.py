#!/usr/bin/env sage

import json
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
import matplotlib.ticker as ptick

class BiasAnalyzer:
    def __init__(self, data_dir="frobenius_data"):
        """
        素数の偏り解析器の初期化
        
        Args:
            data_dir: フロベニウス元データのディレクトリ
        """
        self.data_dir = data_dir
        self.case_data = {}
        
        # M(σ) + m(σ) の値 (青木さんのメモより)
        self.bias_coefficients = {
            # m_rho0 = 0 の場合
            0: {
                'g0': 1/2,    # M(1) + m(1) = 1/2 + 0
                'g1': 5/2,    # M(-1) + m(-1) = 5/2 + 0  
                'g2': -1/2,   # M(i) + m(i) = -1/2 + 0
                'g3': -1/2,   # M(j) + m(j) = -1/2 + 0
                'g4': -1/2,   # M(k) + m(k) = -1/2 + 0
                'g5': -1/2,   # M(-i) + m(-i) = -1/2 + 0
                'g6': -1/2,   # M(-j) + m(-j) = -1/2 + 0
                'g7': -1/2    # M(-k) + m(-k) = -1/2 + 0
            },
            # m_rho0 = 1 の場合
            1: {
                'g0': 5/2,    # M(1) + m(1) = 1/2 + 2
                'g1': 1/2,    # M(-1) + m(-1) = 5/2 + (-2)
                'g2': -1/2,   # M(i) + m(i) = -1/2 + 0
                'g3': -1/2,   # M(j) + m(j) = -1/2 + 0
                'g4': -1/2,   # M(k) + m(k) = -1/2 + 0
                'g5': -1/2,   # M(-i) + m(-i) = -1/2 + 0
                'g6': -1/2,   # M(-j) + m(-j) = -1/2 + 0
                'g7': -1/2    # M(-k) + m(-k) = -1/2 + 0
            }
        }
        
        # 共役類のサイズ
        self.conjugacy_class_sizes = {
            'g0': 1,   # {1}
            'g1': 1,   # {-1}
            'g2': 2,   # {i, -i}
            'g3': 2,   # {j, -j}  
            'g4': 2,   # {k, -k}
            'g5': 2,   # {i, -i} (g2と同じ共役類)
            'g6': 2,   # {j, -j} (g3と同じ共役類)
            'g7': 2    # {k, -k} (g4と同じ共役類)
        }
    
    def load_case_data(self, case_id):
        """
        指定されたケースのデータを読み込み
        
        Args:
            case_id: ケースID
            
        Returns:
            読み込まれたデータ
        """
        filename = f"{self.data_dir}/case_{case_id:02d}_frobenius.json"
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"データファイルが見つかりません: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.case_data[case_id] = data
        return data
    
    def compute_pi_half(self, primes_dict, max_x):
        """
        π_{1/2}(x; σ) を計算
        
        Args:
            primes_dict: {prime: frobenius_index} の辞書
            max_x: 最大値
            
        Returns:
            (x_values, pi_half_values) のタプル
        """
        # 素数をソート
        sorted_primes = sorted([p for p in primes_dict.keys() if p <= max_x])
        
        x_values = list(range(2, max_x + 1))
        pi_half_values = []
        
        pi_sum = 0
        prime_idx = 0
        
        for x in x_values:
            # x以下の素数について累積
            while prime_idx < len(sorted_primes) and sorted_primes[prime_idx] <= x:
                p = sorted_primes[prime_idx]
                pi_sum += 1 / sqrt(p)
                prime_idx += 1
            
            pi_half_values.append(float(pi_sum))
        
        return x_values, pi_half_values
    
    def compute_pi_half_by_frobenius(self, frobenius_data, max_x):
        """
        フロベニウス元ごとのπ_{1/2}(x; σ)を計算
        
        Args:
            frobenius_data: フロベニウス元のデータ
            max_x: 最大値
            
        Returns:
            各フロベニウス元ごとの辞書
        """
        # フロベニウス元ごとに素数を分類
        frobenius_primes = defaultdict(list)
        
        for prime_str, frobenius_idx in frobenius_data.items():
            p = int(prime_str)
            if p <= max_x:
                frobenius_primes[frobenius_idx].append(p)
        
        # 各フロベニウス元についてπ_{1/2}を計算
        results = {}
        for frobenius_idx in range(8):  # g0からg7まで
            group_key = f'g{frobenius_idx}'
            
            if frobenius_idx in frobenius_primes:
                primes_dict = {p: frobenius_idx for p in frobenius_primes[frobenius_idx]}
                x_vals, pi_vals = self.compute_pi_half(primes_dict, max_x)
                results[group_key] = (x_vals, pi_vals)
            else:
                # 該当する素数がない場合
                x_vals = list(range(2, max_x + 1))
                pi_vals = [0.0] * len(x_vals)
                results[group_key] = (x_vals, pi_vals)
        
        return results
    
    def compute_total_pi_half(self, frobenius_data, max_x):
        """
        全体のπ_{1/2}(x)を計算
        
        Args:
            frobenius_data: フロベニウス元のデータ
            max_x: 最大値
            
        Returns:
            (x_values, pi_half_total) のタプル
        """
        all_primes = {int(p): 0 for p in frobenius_data.keys() if int(p) <= max_x}
        return self.compute_pi_half(all_primes, max_x)
    
    def plot_bias_graphs(self, case_id, max_x=10**5, output_dir="graphs"):
        """
        偏りのグラフを描画
        
        Args:
            case_id: ケースID
            max_x: 最大値
            output_dir: 出力ディレクトリ
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # データを読み込み
        if case_id not in self.case_data:
            self.load_case_data(case_id)
        
        data = self.case_data[case_id]
        m_rho0 = data['m_rho0']
        frobenius_data = data['frobenius_elements']
        
        print(f"Case {case_id}: グラフ作成開始 (m_ρ0 = {m_rho0})")
        
        # 全体のπ_{1/2}(x)を計算
        x_total, pi_total = self.compute_total_pi_half(frobenius_data, max_x)
        
        # フロベニウス元ごとのπ_{1/2}(x; σ)を計算
        pi_by_frobenius = self.compute_pi_half_by_frobenius(frobenius_data, max_x)
        
        # 5つのグラフを作成 (青木さんのメモより)
        graphs_to_plot = [
            ('g0', 1, '1'),      # S1: identity
            ('g1', 1, '-1'),     # S2: -1
            ('g2', 2, 'i'),      # S3: i (共役類サイズ2)
            ('g3', 2, 'j'),      # S4: j (共役類サイズ2)
            ('g4', 2, 'k')       # S5: k (共役類サイズ2)
        ]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, (group_key, conj_size, label) in enumerate(graphs_to_plot):
            ax = axes[idx]
            
            # π_{1/2}(x; σ)を取得
            x_sigma, pi_sigma = pi_by_frobenius[group_key]
            
            # 偏りの計算: π_{1/2}(x) - (8/|c_σ|) * π_{1/2}(x; σ)
            bias_coeff = self.bias_coefficients[m_rho0][group_key]
            conjugacy_size = conj_size
            
            y_bias = []
            x_log_log = []
            
            for i, x in enumerate(x_sigma):
                if i < len(pi_total) and x >= 3:  # log(log(x))が定義される範囲
                    pi_total_val = pi_total[i] if i < len(pi_total) else 0
                    pi_sigma_val = pi_sigma[i]
                    
                    # 偏りの計算: π_{1/2}(x) - (8/|c_σ|) * π_{1/2}(x; σ)
                    bias_val = pi_total_val - (8.0 / conjugacy_size) * pi_sigma_val
                    y_bias.append(bias_val)
                    
                    # 理論値: (M(σ) + m(σ)) * log(log(x))
                    log_log_x = float(log(log(x)))
                    theoretical_val = bias_coeff * log_log_x
                    x_log_log.append(theoretical_val)
                else:
                    y_bias.append(0)
                    x_log_log.append(0)
            
            # グラフを描画
            x_plot = [x for x in x_sigma if x >= 3]
            y_bias_plot = y_bias[:len(x_plot)]
            x_log_log_plot = x_log_log[:len(x_plot)]
            
            # 実際の偏り
            ax.scatter(x_plot, y_bias_plot, color="black", marker=".", s=0.5, alpha=0.6, label='Actual bias')
            
            # 理論値
            ax.plot(x_plot, x_log_log_plot, color="red", linewidth=2, label=f'{bias_coeff} log(log(x))')
            
            ax.set_xscale("log")
            ax.set_xlabel("x")
            ax.set_ylabel(f"π₁/₂(x) - {8//conjugacy_size}π₁/₂(x;{label})")
            ax.set_title(f"Case {case_id}: S{idx+1} (σ = {label}, m_ρ₀ = {m_rho0})")
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        # 6番目のサブプロットを削除
        fig.delaxes(axes[5])
        
        plt.tight_layout()
        
        # グラフを保存
        output_filename = f"{output_dir}/case_{case_id:02d}_bias_graphs.png"
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        
        print(f"Case {case_id}: グラフを保存しました -> {output_filename}")
        
        # 個別のグラフも作成
        self.plot_individual_graphs(case_id, max_x, output_dir)
    
    def plot_individual_graphs(self, case_id, max_x, output_dir):
        """
        個別のグラフを作成
        """
        data = self.case_data[case_id]
        m_rho0 = data['m_rho0']
        frobenius_data = data['frobenius_elements']
        
        # 全体のπ_{1/2}(x)を計算
        x_total, pi_total = self.compute_total_pi_half(frobenius_data, max_x)
        
        # フロベニウス元ごとのπ_{1/2}(x; σ)を計算
        pi_by_frobenius = self.compute_pi_half_by_frobenius(frobenius_data, max_x)
        
        graphs_to_plot = [
            ('g0', 1, '1'),      
            ('g1', 1, '-1'),     
            ('g2', 2, 'i'),      
            ('g3', 2, 'j'),      
            ('g4', 2, 'k')       
        ]
        
        for idx, (group_key, conj_size, label) in enumerate(graphs_to_plot):
            plt.figure(figsize=(10, 6))
            
            # データを準備
            x_sigma, pi_sigma = pi_by_frobenius[group_key]
            bias_coeff = self.bias_coefficients[m_rho0][group_key]
            
            y_bias = []
            x_log_log = []
            
            for i, x in enumerate(x_sigma):
                if i < len(pi_total) and x >= 3:
                    pi_total_val = pi_total[i] if i < len(pi_total) else 0
                    pi_sigma_val = pi_sigma[i]
                    
                    bias_val = pi_total_val - (8.0 / conj_size) * pi_sigma_val
                    y_bias.append(bias_val)
                    
                    log_log_x = float(log(log(x)))
                    theoretical_val = bias_coeff * log_log_x
                    x_log_log.append(theoretical_val)
                else:
                    y_bias.append(0)
                    x_log_log.append(0)
            
            x_plot = [x for x in x_sigma if x >= 3]
            y_bias_plot = y_bias[:len(x_plot)]
            x_log_log_plot = x_log_log[:len(x_plot)]
            
            # プロット
            plt.scatter(x_plot, y_bias_plot, color="black", marker=".", s=0.3, alpha=0.7, label='Actual bias')
            plt.plot(x_plot, x_log_log_plot, color="red", linewidth=2, label=f'{bias_coeff} log(log(x))')
            
            plt.xscale("log")
            plt.xlabel("x", fontsize=12)
            plt.ylabel(f"π₁/₂(x) - {8//conj_size}π₁/₂(x;{label})", fontsize=12)
            plt.title(f"Case {case_id}: Prime Bias for σ = {label} (m_ρ₀ = {m_rho0})", fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=10)
            
            # 個別保存
            individual_filename = f"{output_dir}/case_{case_id:02d}_S{idx+1}_{label.replace('-','minus')}.png"
            plt.savefig(individual_filename, dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Case {case_id}: 個別グラフも保存しました")
    
    def analyze_all_cases(self, max_x=10**5):
        """
        全ケースを解析してグラフを作成
        
        Args:
            max_x: 最大値
        """
        print("全ケースのグラフ作成を開始")
        print("=" * 50)
        
        # 出力ディレクトリを作成
        output_dir = "graphs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 各ケースを処理
        for case_id in range(1, 14):  # Case 1-13
            try:
                print(f"\nCase {case_id} 処理開始...")
                
                # データファイルが存在するかチェック
                filename = f"{self.data_dir}/case_{case_id:02d}_frobenius.json"
                if not os.path.exists(filename):
                    print(f"Case {case_id}: データファイルが見つかりません -> {filename}")
                    continue
                
                # グラフを作成
                self.plot_bias_graphs(case_id, max_x, output_dir)
                
                print(f"Case {case_id}: 完了")
                
            except Exception as e:
                print(f"Case {case_id}: エラーが発生しました -> {e}")
                continue
        
        print("\n" + "=" * 50)
        print("全ケースのグラフ作成が完了しました！")
        print(f"出力ディレクトリ: {output_dir}")
    
    def print_statistics(self, case_id):
        """
        ケースの統計情報を表示
        
        Args:
            case_id: ケースID
        """
        if case_id not in self.case_data:
            self.load_case_data(case_id)
        
        data = self.case_data[case_id]
        frobenius_data = data['frobenius_elements']
        
        print(f"\nCase {case_id} 統計情報:")
        print(f"多項式: {data['polynomial']}")
        print(f"判別式: {data['discriminant']}")
        print(f"m_ρ₀: {data['m_rho0']}")
        print(f"計算した素数の個数: {len(frobenius_data)}")
        
        # フロベニウス元の分布
        frobenius_count = defaultdict(int)
        for frobenius_idx in frobenius_data.values():
            frobenius_count[frobenius_idx] += 1
        
        print("\nフロベニウス元の分布:")
        total_primes = len(frobenius_data)
        for i in range(8):
            count = frobenius_count[i]
            percentage = (count / total_primes) * 100 if total_primes > 0 else 0
            group_name = ['1', '-1', 'i', 'j', 'k', '-i', '-j', '-k'][i]
            print(f"  g{i} ({group_name}): {count} primes ({percentage:.2f}%)")

def main():
    """
    メイン実行関数
    """
    print("グラフ描画プログラム開始")
    print("=" * 50)
    
    # 解析器を初期化
    analyzer = BiasAnalyzer()
    
    # 設定
    max_x = 10**5  # グラフの最大値
    
    print(f"設定:")
    print(f"  最大値: {max_x:,}")
    print()
    
    # 全ケースを処理
    analyzer.analyze_all_cases(max_x)
    
    # 各ケースの統計情報を表示
    print("\n" + "=" * 50)
    print("統計情報:")
    
    for case_id in range(1, 14):
        try:
            analyzer.print_statistics(case_id)
        except Exception as e:
            print(f"Case {case_id}: 統計情報の取得に失敗 -> {e}")

if __name__ == "__main__":
    main()
