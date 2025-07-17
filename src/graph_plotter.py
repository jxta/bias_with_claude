#!/usr/bin/env sage

import json
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
import matplotlib.ticker as ptick

# SageMathの必要な関数をインポート
from sage.all import *

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
    
    def auto_detect_max_x(self, case_id=None, default_max=10**8):
        """
        フロベニウス計算結果から自動的に最大x値を検出
        
        Args:
            case_id: 特定のケースの最大値を検出 (Noneの場合は全ケース)
            default_max: データが見つからない場合のデフォルト値
            
        Returns:
            検出された最大x値
        """
        max_prime = 0
        
        if case_id is not None:
            # 特定のケースのみチェック
            case_ids = [case_id]
        else:
            # 全ケースをチェック
            case_ids = range(1, 14)
        
        for cid in case_ids:
            try:
                if cid not in self.case_data:
                    self.load_case_data(cid)
                
                data = self.case_data[cid]
                frobenius_data = data['frobenius_elements']
                
                # 最大素数を取得
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
        
        # 適切な上限に調整（10の倍数に切り上げ）
        if max_prime < 10**3:
            detected_max = 10**3
        elif max_prime < 10**4:
            detected_max = 10**4
        elif max_prime < 10**5:
            detected_max = 10**5
        elif max_prime < 10**6:
            detected_max = 10**6
        elif max_prime < 10**7:
            detected_max = 10**7
        else:
            detected_max = 10**8
        
        print(f"検出された最大素数: {max_prime:,}")
        print(f"グラフ用最大x値: {detected_max:,}")
        
        return detected_max
    
    def generate_adaptive_sample_points(self, max_x, target_points=1000):
        """
        対数スケールに最適化された適応的サンプリング点を生成
        
        Args:
            max_x: 最大値
            target_points: 目標点数
            
        Returns:
            サンプリング点のリスト
        """
        if max_x <= target_points:
            return list(range(3, max_x + 1))
        
        # 対数スケールで分布を作成
        x_min = 3  # log(log(x))が定義される最小値
        x_max = max_x
        
        # 対数空間での均等分布
        log_min = float(log(x_min))
        log_max = float(log(x_max))
        
        # より細かい分解能を最初に配置
        sample_points = []
        
        # Phase 1: 最初の部分 (3 ～ 1000) - 密度高
        if x_max > 1000:
            phase1_points = int(target_points * 0.4)  # 40%の点を前半に
            for i in range(phase1_points):
                log_x = log_min + (log(1000) - log_min) * i / (phase1_points - 1)
                x = int(exp(log_x))
                if x >= 3 and x not in sample_points:
                    sample_points.append(x)
        
            # Phase 2: 中間部分 (1000 ～ x_max/10) - 中密度
            phase2_points = int(target_points * 0.35)  # 35%の点を中間に
            mid_start = 1000
            mid_end = max(10000, x_max // 10)
            
            if mid_end > mid_start:
                for i in range(phase2_points):
                    log_x = log(mid_start) + (log(mid_end) - log(mid_start)) * i / (phase2_points - 1)
                    x = int(exp(log_x))
                    if x not in sample_points:
                        sample_points.append(x)
        
            # Phase 3: 後半部分 (x_max/10 ～ x_max) - 低密度
            phase3_points = int(target_points * 0.25)  # 25%の点を後半に
            final_start = max(10000, x_max // 10)
            
            for i in range(phase3_points):
                log_x = log(final_start) + (log_max - log(final_start)) * i / (phase3_points - 1)
                x = int(exp(log_x))
                if x not in sample_points:
                    sample_points.append(x)
        else:
            # max_x が小さい場合は単純な対数分布
            for i in range(target_points):
                log_x = log_min + (log_max - log_min) * i / (target_points - 1)
                x = int(exp(log_x))
                if x >= 3 and x not in sample_points:
                    sample_points.append(x)
        
        # 重複削除とソート
        sample_points = sorted(list(set(sample_points)))
        
        # 最大値を確実に含める
        if x_max not in sample_points:
            sample_points.append(x_max)
        
        sample_points.sort()
        
        print(f"適応的サンプリング: {len(sample_points)} points (目標: {target_points})")
        return sample_points
    
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
    
    def compute_pi_half_adaptive(self, primes_dict, sample_points):
        """
        適応的サンプリング点でπ_{1/2}(x; σ) を計算
        
        Args:
            primes_dict: {prime: frobenius_index} の辞書
            sample_points: サンプリング点のリスト
            
        Returns:
            (x_values, pi_half_values) のタプル
        """
        # 素数をソート
        sorted_primes = sorted([p for p in primes_dict.keys()])
        
        if not sorted_primes:
            return [], []
        
        pi_half_values = []
        
        for x in sample_points:
            # x以下の素数について累積
            pi_sum = 0
            for p in sorted_primes:
                if p <= x:
                    pi_sum += 1 / sqrt(p)
                else:
                    break
            
            pi_half_values.append(float(pi_sum))
        
        return sample_points, pi_half_values
    
    def compute_pi_half_by_frobenius_adaptive(self, frobenius_data, sample_points):
        """
        フロベニウス元ごとのπ_{1/2}(x; σ)を計算（適応的サンプリング版）
        
        Args:
            frobenius_data: フロベニウス元のデータ
            sample_points: サンプリング点のリスト
            
        Returns:
            各フロベニウス元ごとの辞書
        """
        print(f"  データ処理中... (サンプル点数: {len(sample_points)})")
        
        # フロベニウス元ごとに素数を分類
        frobenius_primes = defaultdict(list)
        
        for prime_str, frobenius_idx in frobenius_data.items():
            p = int(prime_str)
            frobenius_primes[frobenius_idx].append(p)
        
        # 各フロベニウス元についてπ_{1/2}を計算
        results = {}
        for frobenius_idx in range(8):  # g0からg7まで
            group_key = f'g{frobenius_idx}'
            
            if frobenius_idx in frobenius_primes:
                primes_dict = {p: frobenius_idx for p in frobenius_primes[frobenius_idx]}
                x_vals, pi_vals = self.compute_pi_half_adaptive(primes_dict, sample_points)
                results[group_key] = (x_vals, pi_vals)
            else:
                # 該当する素数がない場合
                results[group_key] = ([], [])
        
        return results
    
    def compute_total_pi_half_adaptive(self, frobenius_data, sample_points):
        """
        全体のπ_{1/2}(x)を計算（適応的サンプリング版）
        
        Args:
            frobenius_data: フロベニウス元のデータ
            sample_points: サンプリング点のリスト
            
        Returns:
            (x_values, pi_half_total) のタプル
        """
        all_primes = {int(p): 0 for p in frobenius_data.keys()}
        return self.compute_pi_half_adaptive(all_primes, sample_points)
    
    def plot_bias_graphs(self, case_id, max_x=None, output_dir="graphs", target_points=1000):
        """
        偏りのグラフを描画（改善版）
        
        Args:
            case_id: ケースID
            max_x: 最大値 (Noneの場合は自動検出)
            output_dir: 出力ディレクトリ
            target_points: 目標サンプリング点数
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # データを読み込み
        if case_id not in self.case_data:
            self.load_case_data(case_id)
        
        data = self.case_data[case_id]
        m_rho0 = data['m_rho0']
        frobenius_data = data['frobenius_elements']
        
        # max_xを自動検出
        if max_x is None:
            max_x = self.auto_detect_max_x(case_id)
        
        print(f"Case {case_id}: グラフ作成開始 (m_ρ0 = {m_rho0}, max_x = {max_x:,})")
        
        # 適応的サンプリング点を生成
        sample_points = self.generate_adaptive_sample_points(max_x, target_points)
        
        # 全体のπ_{1/2}(x)を計算
        print(f"  全体のπ_{1/2}(x)を計算中...")
        x_total, pi_total = self.compute_total_pi_half_adaptive(frobenius_data, sample_points)
        
        # フロベニウス元ごとのπ_{1/2}(x; σ)を計算
        print(f"  フロベニウス元ごとの計算中...")
        pi_by_frobenius = self.compute_pi_half_by_frobenius_adaptive(frobenius_data, sample_points)
        
        # 5つのグラフを作成
        graphs_to_plot = [
            ('g0', 1, '1'),      # S1: identity
            ('g1', 1, '-1'),     # S2: -1
            ('g2', 2, 'i'),      # S3: i (共役類サイズ2)
            ('g3', 2, 'j'),      # S4: j (共役類サイズ2)
            ('g4', 2, 'k')       # S5: k (共役類サイズ2)
        ]
        
        print(f"  グラフ描画中...")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, (group_key, conj_size, label) in enumerate(graphs_to_plot):
            ax = axes[idx]
            
            # π_{1/2}(x; σ)を取得
            x_sigma, pi_sigma = pi_by_frobenius[group_key]
            
            if not x_sigma:  # データがない場合
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"Case {case_id}: S{idx+1} (σ = {label}, m_ρ₀ = {m_rho0})")
                continue
            
            # 偏りの計算
            bias_coeff = self.bias_coefficients[m_rho0][group_key]
            
            y_bias = []
            x_log_log = []
            x_plot = []
            
            # 共通のx点でデータを補間
            for x in x_sigma:
                if x >= 3:  # log(log(x))が定義される範囲
                    # 対応するpi_totalの値を補間で求める
                    pi_total_val = np.interp(x, x_total, pi_total) if x_total else 0
                    
                    # pi_sigmaの値を取得
                    pi_sigma_val = np.interp(x, x_sigma, pi_sigma)
                    
                    # 偏りの計算: π_{1/2}(x) - (8/|c_σ|) * π_{1/2}(x; σ)
                    bias_val = pi_total_val - (8.0 / conj_size) * pi_sigma_val
                    y_bias.append(bias_val)
                    
                    # 理論値: (M(σ) + m(σ)) * log(log(x))
                    log_log_x = float(log(log(x)))
                    theoretical_val = bias_coeff * log_log_x
                    x_log_log.append(theoretical_val)
                    
                    x_plot.append(x)
            
            if x_plot:  # データがある場合のみ描画
                # 実際の偏り（適応的サンプリング済みなので全点描画）
                ax.scatter(x_plot, y_bias, 
                          color="black", marker=".", s=1.5, alpha=0.7, label='Actual bias')
                
                # 理論値
                ax.plot(x_plot, x_log_log, color="red", linewidth=2, 
                       label=f'{bias_coeff} log(log(x))')
                
                ax.set_xscale("log")
                ax.legend(fontsize=8)
            
            ax.set_xlabel("x")
            ax.set_ylabel(f"π₁/₂(x) - {8//conj_size}π₁/₂(x;{label})")
            ax.set_title(f"Case {case_id}: S{idx+1} (σ = {label}, m_ρ₀ = {m_rho0})")
            ax.grid(True, alpha=0.3)
        
        # 6番目のサブプロットを削除
        fig.delaxes(axes[5])
        
        plt.tight_layout()
        
        # グラフを保存
        output_filename = f"{output_dir}/case_{case_id:02d}_bias_graphs.png"
        print(f"  ファイル保存中...")
        plt.savefig(output_filename, dpi=200, bbox_inches='tight')
        plt.close()  # メモリ解放
        
        print(f"Case {case_id}: グラフを保存しました -> {output_filename}")
    
    def analyze_all_cases(self, max_x=None, target_points=1000):
        """
        全ケースを解析してグラフを作成（改善版）
        
        Args:
            max_x: 最大値 (Noneの場合は自動検出)
            target_points: 目標サンプリング点数
        """
        print("全ケースのグラフ作成を開始")
        print("=" * 50)
        
        # max_xを自動検出（全ケースから）
        if max_x is None:
            max_x = self.auto_detect_max_x()
        
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
                self.plot_bias_graphs(case_id, max_x, output_dir, target_points)
                
                print(f"Case {case_id}: 完了")
                
            except Exception as e:
                print(f"Case {case_id}: エラーが発生しました -> {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("\n" + "=" * 50)
        print("全ケースのグラフ作成が完了しました！")
        print(f"出力ディレクトリ: {output_dir}")
        print(f"使用した最大x値: {max_x:,}")
    
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
        
        print(f"\nCase {case_id} の結果:")
        print(f"多項式: {data['polynomial']}")
        print(f"判別式: {data['discriminant']}")
        print(f"m_ρ₀: {data['m_rho0']}")
        print(f"計算した素数の数: {len(frobenius_data)}")
        
        # 最大素数を表示
        if frobenius_data:
            max_prime = max(int(p) for p in frobenius_data.keys())
            print(f"最大素数: {max_prime:,}")
        
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
    print("グラフ描画プログラム開始（改善版）")
    print("=" * 50)
    
    # 解析器を初期化
    analyzer = BiasAnalyzer()
    
    # 設定（改善版）
    max_x = None  # 自動検出を使用
    target_points = 1000  # 適応的サンプリングの目標点数
    
    print(f"設定:")
    print(f"  最大値: 自動検出")
    print(f"  目標サンプル点数: {target_points}")
    print(f"  適応的サンプリング: 有効")
    print()
    
    # 全ケースを処理
    analyzer.analyze_all_cases(max_x, target_points)
    
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
