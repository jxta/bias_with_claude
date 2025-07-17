#!/usr/bin/env python3

import json
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
import math

class BiasAnalyzer:
    def __init__(self, data_dir="frobenius_data"):
        """
        素数の偏り解析器の初期化
        """
        self.data_dir = data_dir
        self.case_data = {}
        
        # M(σ) + m(σ) の値 (青木さんの理論より)
        self.bias_coefficients = {
            # m_rho0 = 0 の場合
            0: {
                'g0': 1/2,    'g1': 5/2,    'g2': -1/2,   'g3': -1/2,
                'g4': -1/2,   'g5': -1/2,   'g6': -1/2,   'g7': -1/2
            },
            # m_rho0 = 1 の場合
            1: {
                'g0': 5/2,    'g1': 1/2,    'g2': -1/2,   'g3': -1/2,
                'g4': -1/2,   'g5': -1/2,   'g6': -1/2,   'g7': -1/2
            }
        }
    
    def load_case_data(self, case_id):
        """指定されたケースのデータを読み込み"""
        filename = f"{self.data_dir}/case_{case_id:02d}_frobenius.json"
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"データファイルが見つかりません: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.case_data[case_id] = data
        return data
    
    def auto_detect_max_x(self, case_id=None, default_max=10**5):
        """フロベニウス計算結果から自動的に最大x値を検出"""
        max_prime = 0
        
        if case_id is not None:
            case_ids = [case_id]
        else:
            case_ids = range(1, 14)
        
        for cid in case_ids:
            try:
                if cid not in self.case_data:
                    self.load_case_data(cid)
                
                data = self.case_data[cid]
                frobenius_data = data['frobenius_elements']
                
                primes = [int(p) for p in frobenius_data.keys()]
                if primes:
                    case_max = max(primes)
                    max_prime = max(max_prime, case_max)
                    
            except (FileNotFoundError, KeyError) as e:
                print(f"Case {cid}: データ読み込み失敗 -> {e}")
                continue
        
        if max_prime == 0:
            print(f"データが見つからないため、デフォルト値 {default_max:,} を使用します")
            return default_max
        
        if max_prime < 10**3:
            detected_max = 10**3
        elif max_prime < 10**4:
            detected_max = 10**4
        elif max_prime < 10**5:
            detected_max = 10**5
        else:
            detected_max = max_prime
        
        print(f"検出された最大素数: {max_prime:,}")
        print(f"グラフ用最大x値: {detected_max:,}")
        
        return detected_max
    
    def generate_sample_points(self, max_x, target_points=500):
        """サンプリング点を生成"""
        if max_x <= target_points:
            return list(range(3, max_x + 1))
        
        x_min = 3
        log_min = math.log(x_min)
        log_max = math.log(max_x)
        
        sample_points = []
        for i in range(target_points):
            log_x = log_min + (log_max - log_min) * i / (target_points - 1)
            x = int(math.exp(log_x))
            if x >= 3 and x not in sample_points:
                sample_points.append(x)
        
        if max_x not in sample_points:
            sample_points.append(max_x)
        
        sample_points.sort()
        return sample_points
    
    def compute_pi_half(self, primes_list, sample_points):
        """π_{1/2}(x) を計算"""
        if not primes_list:
            return [], []
        
        sorted_primes = sorted(primes_list)
        pi_half_values = []
        
        for x in sample_points:
            pi_sum = 0.0
            for p in sorted_primes:
                if p <= x:
                    pi_sum += 1.0 / math.sqrt(float(p))
                else:
                    break
            pi_half_values.append(pi_sum)
        
        return sample_points, pi_half_values
    
    def compute_pi_half_by_frobenius(self, frobenius_data, sample_points):
        """フロベニウス元ごとのπ_{1/2}(x; σ)を計算"""
        print(f"  データ処理中... (サンプル点数: {len(sample_points)})")
        
        frobenius_primes = defaultdict(list)
        
        for prime_str, frobenius_idx in frobenius_data.items():
            p = int(prime_str)
            frobenius_primes[frobenius_idx].append(p)
        
        results = {}
        for frobenius_idx in range(8):
            group_key = f'g{frobenius_idx}'
            
            if frobenius_idx in frobenius_primes:
                primes_list = frobenius_primes[frobenius_idx]
                x_vals, pi_vals = self.compute_pi_half(primes_list, sample_points)
                results[group_key] = (x_vals, pi_vals)
                print(f"    {group_key}: {len(primes_list)} primes processed")
            else:
                results[group_key] = ([], [])
        
        return results
    
    def plot_bias_graphs(self, case_id, max_x=None, output_dir="graphs", target_points=500):
        """偏りのグラフを描画"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if case_id not in self.case_data:
            self.load_case_data(case_id)
        
        data = self.case_data[case_id]
        m_rho0 = data['m_rho0']
        frobenius_data = data['frobenius_elements']
        
        if max_x is None:
            max_x = self.auto_detect_max_x(case_id)
        
        print(f"Case {case_id}: グラフ作成開始 (m_ρ0 = {m_rho0}, max_x = {max_x:,})")
        
        sample_points = self.generate_sample_points(max_x, target_points)
        
        print(f"  全体のπ_{1/2}(x)を計算中...")
        all_primes = [int(p) for p in frobenius_data.keys()]
        x_total, pi_total = self.compute_pi_half(all_primes, sample_points)
        
        print(f"  フロベニウス元ごとの計算中...")
        pi_by_frobenius = self.compute_pi_half_by_frobenius(frobenius_data, sample_points)
        
        graphs_to_plot = [
            ('g0', 1, '1'),      ('g1', 1, '-1'),     ('g2', 2, 'i'),
            ('g3', 2, 'j'),      ('g4', 2, 'k')
        ]
        
        print(f"  グラフ描画中...")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, (group_key, conj_size, label) in enumerate(graphs_to_plot):
            ax = axes[idx]
            
            x_sigma, pi_sigma = pi_by_frobenius[group_key]
            
            if not x_sigma:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"Case {case_id}: S{idx+1} (σ = {label}, m_ρ₀ = {m_rho0})")
                continue
            
            bias_coeff = self.bias_coefficients[m_rho0][group_key]
            
            y_bias = []
            x_log_log = []
            x_plot = []
            
            for i, x in enumerate(x_sigma):
                if x >= 3:
                    pi_total_val = pi_total[i] if i < len(pi_total) else 0
                    pi_sigma_val = pi_sigma[i]
                    
                    bias_val = pi_total_val - (8.0 / conj_size) * pi_sigma_val
                    y_bias.append(bias_val)
                    
                    log_log_x = math.log(math.log(x))
                    theoretical_val = bias_coeff * log_log_x
                    x_log_log.append(theoretical_val)
                    
                    x_plot.append(x)
            
            if x_plot:
                ax.scatter(x_plot, y_bias, color="black", marker=".", s=1.5, alpha=0.7, label='Actual bias')
                ax.plot(x_plot, x_log_log, color="red", linewidth=2, label=f'{bias_coeff} log(log(x))')
                ax.set_xscale("log")
                ax.legend(fontsize=8)
            
            ax.set_xlabel("x")
            ax.set_ylabel(f"π₁/₂(x) - {8//conj_size}π₁/₂(x;{label})")
            ax.set_title(f"Case {case_id}: S{idx+1} (σ = {label}, m_ρ₀ = {m_rho0})")
            ax.grid(True, alpha=0.3)
        
        fig.delaxes(axes[5])
        plt.tight_layout()
        
        output_filename = f"{output_dir}/case_{case_id:02d}_bias_graphs.png"
        print(f"  ファイル保存中...")
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Case {case_id}: グラフを保存しました -> {output_filename}")
    
    def print_statistics(self, case_id):
        """ケースの統計情報を表示"""
        if case_id not in self.case_data:
            self.load_case_data(case_id)
        
        data = self.case_data[case_id]
        frobenius_data = data['frobenius_elements']
        
        print(f"\nCase {case_id} の結果:")
        print(f"多項式: {data['polynomial']}")
        print(f"判別式: {data['discriminant']}")
        print(f"m_ρ₀: {data['m_rho0']}")
        print(f"計算した素数の数: {len(frobenius_data)}")
        
        if frobenius_data:
            max_prime = max(int(p) for p in frobenius_data.keys())
            print(f"最大素数: {max_prime:,}")
        
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
    """メイン実行関数"""
    print("グラフ描画プログラム開始")
    print("=" * 50)
    
    analyzer = BiasAnalyzer(data_dir="frobenius_data")
    
    available_cases = []
    for case_id in range(1, 4):
        try:
            filename = f"frobenius_data/case_{case_id:02d}_frobenius.json"
            if os.path.exists(filename):
                available_cases.append(case_id)
        except:
            continue
    
    if not available_cases:
        print("処理可能なデータファイルが見つかりません。")
        print("まずfrobenius_calculator.pyを実行してデータを生成してください。")
        return
    
    print(f"利用可能なケース: {available_cases}")
    
    for case_id in available_cases:
        try:
            print(f"\nCase {case_id} 処理開始...")
            analyzer.plot_bias_graphs(case_id, max_x=None, target_points=300)
            analyzer.print_statistics(case_id)
            print(f"Case {case_id}: 完了")
            
        except Exception as e:
            print(f"Case {case_id}: エラーが発生しました -> {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 50)
    print("グラフ作成が完了しました！")
    print("出力ディレクトリ: graphs/")

if __name__ == "__main__":
    main()
