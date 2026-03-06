#!/usr/bin/env python3
"""
graph_plotter_combined.py

S1〜S5を1つの図に重ねて描画するプログラム。
画像スタイル：
  - 数値データ：ドット（scatter, 小さい点）
  - 理論曲線：破線（dashed line）
  - 色：S1=黒, S2=緑, S3=青, S4=赤, S5=マゼンタ
  - 対数x軸
  - 数式アノテーション（左上）
  - 凡例（右）

使用例:
    # Python版（外部からも利用可能）
    from graph_plotter_combined import CombinedBiasPlotter
    plotter = CombinedBiasPlotter(data_dir='frobenius_data')
    plotter.plot_combined(case_id=1)

    # コマンドラインから
    python3 src/graph_plotter_combined.py --case 1
    python3 src/graph_plotter_combined.py --all
"""

import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import math
import argparse
from collections import defaultdict

# LaTeX風フォント設定（利用可能な場合）
try:
    plt.rcParams.update({
        'text.usetex': False,  # LaTeX不要でもそれらしい表示
        'font.family': 'serif',
        'mathtext.fontset': 'cm',
    })
except:
    pass


# ================================================================
# Omar論文の13ケース定義
# ================================================================
OMARCASES = [
    {'id': 1,  'poly': 'x^8 - x^7 - 34*x^6 + 29*x^5 + 361*x^4 - 305*x^3 - 1090*x^2 + 1345*x - 395',  'm_rho0': 0},
    {'id': 2,  'poly': 'x^8 + 315*x^6 + 34020*x^4 + 1488375*x^2 + 22325625',                             'm_rho0': 1},
    {'id': 3,  'poly': 'x^8 - 205*x^6 + 13940*x^4 - 378225*x^2 + 3404025',                              'm_rho0': 1},
    {'id': 4,  'poly': 'x^8 - 3*x^7 + 142*x^6 - 115*x^5 + 6641*x^4 + 3055*x^3 + 157938*x^2 + 152941*x + 2031361', 'm_rho0': 1},
    {'id': 5,  'poly': 'x^8 - x^7 - 178*x^6 - 550*x^5 + 7225*x^4 + 44407*x^3 + 55928*x^2 - 45392*x + 4096', 'm_rho0': 0},
    {'id': 6,  'poly': 'x^8 - 3*x^7 + 106*x^6 + 381*x^5 + 414*x^4 - 8475*x^3 + 44497*x^2 + 151740*x + 253168', 'm_rho0': 1},
    {'id': 7,  'poly': 'x^8 - 3*x^7 - 475*x^6 + 1401*x^5 + 64350*x^4 - 199578*x^3 - 2518605*x^2 + 8025435*x - 7683597', 'm_rho0': 0},
    {'id': 8,  'poly': 'x^8 + x^7 - 7*x^6 - 6*x^5 + 15*x^4 + 10*x^3 - 10*x^2 - 4*x + 1',              'm_rho0': 0},
    {'id': 9,  'poly': 'x^8 - 4*x^6 + 2*x^4 + 4*x^2 + 1',                                               'm_rho0': 0},
    {'id': 10, 'poly': 'x^8 - 2*x^6 - x^4 + 2*x^2 + 1',                                                 'm_rho0': 0},
    {'id': 11, 'poly': 'x^8 + 2*x^6 - x^4 - 2*x^2 + 1',                                                 'm_rho0': 0},
    {'id': 12, 'poly': 'x^8 - x^4 + 1',                                                                  'm_rho0': 0},
    {'id': 13, 'poly': 'x^8 + x^4 + 1',                                                                  'm_rho0': 0},
]

# バイアス係数 (M(σ) + m(σ)) - m_rho0ごと
BIAS_COEFFS = {
    # S1: π(x) - 8π(x;1),   S2: π(x) - 8π(x;-1)
    # S3: π(x) - 4π(x;i),   S4: π(x) - 4π(x;j),   S5: π(x) - 4π(x;k)
    0: {'1': 1/2,  '-1': 5/2,  'i': -1/2, 'j': -1/2, 'k': -1/2},
    1: {'1': 5/2,  '-1': 1/2,  'i': -1/2, 'j': -1/2, 'k': -1/2},
}

# プロット設定
PLOT_STYLES = [
    # (group_key, conj_size, sigma_label, color, S_label)
    ('g0', 1, '1',  'black',   'S1'),
    ('g1', 1, '-1', 'green',   'S2'),
    ('g2', 2, 'i',  'blue',    'S3'),
    ('g3', 2, 'j',  'red',     'S4'),
    ('g4', 2, 'k',  'magenta', 'S5'),
]


class CombinedBiasPlotter:
    """
    S1〜S5を1つのグラフに重ねて描画するプロッタークラス。
    """

    def __init__(self, data_dir='frobenius_data', output_dir='graphs'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ----------------------------------------------------------------
    # データ読み込み
    # ----------------------------------------------------------------
    def load_data(self, case_id):
        path = os.path.join(self.data_dir, f'case_{case_id:02d}_frobenius.json')
        if not os.path.exists(path):
            raise FileNotFoundError(f'データファイルが見つかりません: {path}')
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    # ----------------------------------------------------------------
    # π_{1/2} 累積計算
    # ----------------------------------------------------------------
    def _compute_cumulative(self, sorted_primes, sample_points):
        """sorted_primes の素数について p ≤ x ごとに 1/√p を累積。"""
        values = []
        cum = 0.0
        ptr = 0
        n_primes = len(sorted_primes)
        for x in sample_points:
            while ptr < n_primes and sorted_primes[ptr] <= x:
                cum += 1.0 / math.sqrt(float(sorted_primes[ptr]))
                ptr += 1
            values.append(cum)
        return values

    def compute_s_values(self, frobenius_data, sample_points):
        """
        S1〜S5 の数値を計算して返す。
        Returns: dict {'S1': [...], 'S2': [...], 'S3': [...], 'S4': [...], 'S5': [...]}
        """
        # フロベニウス元ごとに素数を分類
        frobenius_primes = defaultdict(list)
        for prime_str, idx in frobenius_data.items():
            frobenius_primes[int(idx)].append(int(prime_str))

        # 各グループをソート
        for k in frobenius_primes:
            frobenius_primes[k].sort()

        # 全体 π_{1/2}(x)
        all_sorted = sorted(int(p) for p in frobenius_data.keys())
        pi_total = self._compute_cumulative(all_sorted, sample_points)

        # S_i を計算
        s_vals = {}
        for group_key, conj_size, sigma_label, color, s_label in PLOT_STYLES:
            gidx = int(group_key[1])  # 'g0' -> 0
            primes_sigma = frobenius_primes.get(gidx, [])
            pi_sigma = self._compute_cumulative(primes_sigma, sample_points)
            coeff = 8 // conj_size  # 8 or 4
            s_vals[s_label] = [
                pt - coeff * ps
                for pt, ps in zip(pi_total, pi_sigma)
            ]
        return s_vals

    # ----------------------------------------------------------------
    # サンプリング点生成
    # ----------------------------------------------------------------
    def generate_sample_points(self, max_x, target=1000):
        """対数スケールで target 個のサンプル点を生成。"""
        if max_x <= target:
            return list(range(3, max_x + 1))
        pts = set()
        for i in range(target):
            t = i / (target - 1)
            x = int(math.exp(math.log(3) + t * (math.log(max_x) - math.log(3))))
            if x >= 3:
                pts.add(x)
        pts.add(max_x)
        return sorted(pts)

    # ----------------------------------------------------------------
    # メインプロット関数
    # ----------------------------------------------------------------
    def plot_combined(self, case_id, max_x=None, target_points=1000,
                      save=True, show=True, figsize=(12, 8)):
        """
        Case case_id のS1〜S5を1つの図に重ねて描画する。

        Parameters
        ----------
        case_id      : 1〜13
        max_x        : 最大x値（Noneなら自動検出）
        target_points: サンプリング点数
        save         : グラフをファイルに保存するか
        show         : plt.show() を呼ぶか
        figsize      : 図のサイズ
        """
        print(f'Case {case_id}: データ読み込み中...')
        data = self.load_data(case_id)
        m_rho0 = data.get('m_rho0', 0)
        frobenius_data = data['frobenius_elements']

        # max_x 自動検出
        if max_x is None:
            all_primes = [int(p) for p in frobenius_data.keys()]
            max_x = max(all_primes) if all_primes else 10**6
        print(f'  max_x = {max_x:,},  m_ρ₀ = {m_rho0}')

        # サンプリング点
        sample_points = self.generate_sample_points(max_x, target_points)

        # S値の計算
        print(f'  S1〜S5 計算中 (サンプル点数: {len(sample_points)})...')
        s_vals = self.compute_s_values(frobenius_data, sample_points)

        # 理論値 (bias_coeff * log(log(x)))
        bias_coeffs = BIAS_COEFFS[m_rho0]
        sigma_keys  = {'S1': '1', 'S2': '-1', 'S3': 'i', 'S4': 'j', 'S5': 'k'}

        # ---- 図の作成 ----
        fig, ax = plt.subplots(figsize=figsize)

        for group_key, conj_size, sigma_label, color, s_label in PLOT_STYLES:
            coeff = bias_coeffs[sigma_keys[s_label]]

            y_num = s_vals[s_label]

            # 理論値：bias_coeff * log(log(x))
            # log(log(x)) は x > e (≈2.718) で定義
            y_theory = []
            x_theory = []
            for x, yn in zip(sample_points, y_num):
                if x > 3:
                    ll = math.log(math.log(x))
                    y_theory.append(coeff * ll)
                    x_theory.append(x)

            # 数値データ：ドット (scatter)
            ax.scatter(sample_points, y_num,
                       color=color, s=2, alpha=0.6,
                       label=f'{s_label} (numerical)')

            # 理論曲線：破線
            ax.plot(x_theory, y_theory,
                    color=color, linestyle='--', linewidth=1.8,
                    label=f'{s_label} (theory)')

        # ---- 軸・タイトル設定 ----
        ax.set_xscale('log')
        ax.set_title(
            f'Chebyshev Bias for Omar Case {case_id} '
            f'(m_\u03c1\u2080 = {m_rho0})',
            fontsize=15
        )
        ax.set_xlabel('x', fontsize=12)
        ax.grid(True, which='major', alpha=0.3)
        ax.grid(True, which='minor', alpha=0.1)

        # ---- 数式アノテーション（左上）----
        formula_lines = []
        for _, conj_size, sigma_label, _, s_label in PLOT_STYLES:
            coeff = bias_coeffs[sigma_keys[s_label]]
            mult  = 8 // conj_size
            coeff_str = f'{coeff:g}'
            formula_lines.append(
                f'$\\mathrm{{{s_label}}}:\\;'
                f'\\pi_{{1/2}}(x)-{mult}\\pi_{{1/2}}(x;{sigma_label})'
                f'=\\frac{{{int(coeff*2)}}}{{{2}}}\\log\\log x+c+o(1)$'
                if coeff != int(coeff) else
                f'$\\mathrm{{{s_label}}}:\\;'
                f'\\pi_{{1/2}}(x)-{mult}\\pi_{{1/2}}(x;{sigma_label})'
                f'={coeff_str}\\log\\log x+c+o(1)$'
            )
        annotation = '\n'.join(formula_lines)
        ax.text(
            0.01, 0.98, annotation,
            transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
        )

        # ---- 凡例（右外）----
        leg = ax.legend(
            loc='upper left', bbox_to_anchor=(1.01, 1),
            borderaxespad=0, fontsize=9,
            markerscale=3
        )

        plt.tight_layout(rect=[0, 0, 0.82, 1])

        if save:
            fname = os.path.join(
                self.output_dir,
                f'case_{case_id:02d}_combined_bias.png'
            )
            fig.savefig(fname, dpi=200, bbox_inches='tight')
            print(f'  保存完了: {fname}')

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig

    def plot_all_cases(self, max_x=None, target_points=1000, show=False):
        """全13ケースのグラフを作成。"""
        for case_info in OMARCASES:
            case_id = case_info['id']
            fname = os.path.join(
                self.data_dir, f'case_{case_id:02d}_frobenius.json'
            )
            if not os.path.exists(fname):
                print(f'Case {case_id}: データなし -> スキップ')
                continue
            try:
                self.plot_combined(
                    case_id, max_x=max_x,
                    target_points=target_points,
                    show=show
                )
            except Exception as e:
                print(f'Case {case_id}: エラー -> {e}')


# ================================================================
# コマンドライン実行
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description='S1〜S5を1図に重ねて描画するプログラム'
    )
    parser.add_argument('--case', '-c', type=int, choices=range(1, 14),
                        help='特定のケースのみ処理 (1-13)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='全ケースを処理')
    parser.add_argument('--max-x', '-x', type=int, default=None,
                        help='最大x値 (デフォルト: 自動検出)')
    parser.add_argument('--target-points', '-t', type=int, default=1000,
                        help='サンプリング点数 (デフォルト: 1000)')
    parser.add_argument('--data-dir', '-d', type=str, default='frobenius_data',
                        help='フロベニウスデータのディレクトリ')
    parser.add_argument('--output-dir', '-o', type=str, default='graphs',
                        help='出力ディレクトリ')
    parser.add_argument('--show', action='store_true',
                        help='グラフを画面に表示する')
    args = parser.parse_args()

    plotter = CombinedBiasPlotter(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )

    if args.all:
        plotter.plot_all_cases(
            max_x=args.max_x,
            target_points=args.target_points,
            show=args.show
        )
    elif args.case:
        plotter.plot_combined(
            case_id=args.case,
            max_x=args.max_x,
            target_points=args.target_points,
            show=args.show
        )
    else:
        print('--case または --all を指定してください。')
        parser.print_help()


if __name__ == '__main__':
    main()
