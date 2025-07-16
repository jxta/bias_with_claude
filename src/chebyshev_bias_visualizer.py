#!/usr/bin/env sage

"""
Chebyshevバイアス可視化ツール
Omar's 13 Cases結果の総合的な可視化

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
"""

import json
import os
import pickle
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンド
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

class ChebyshevBiasVisualizer:
    """Chebyshevバイアス結果の可視化クラス"""
    
    def __init__(self, results_dir=None, json_file=None, pickle_file=None):
        """
        初期化
        
        Parameters:
        - results_dir: 結果ディレクトリパス
        - json_file: JSONファイルパス（直接指定）
        - pickle_file: Pickleファイルパス（直接指定）
        """
        self.results = {}
        self.figure_dir = None
        
        # データの読み込み
        if results_dir:
            self.load_from_directory(results_dir)
        elif json_file:
            self.load_from_json(json_file)
        elif pickle_file:
            self.load_from_pickle(pickle_file)
        else:
            print("⚠️  データソースが指定されていません")
    
    def load_from_directory(self, results_dir):
        """ディレクトリから結果を読み込み"""
        print(f"📁 ディレクトリから読み込み: {results_dir}")
        
        if not os.path.exists(results_dir):
            print(f"❌ ディレクトリが存在しません: {results_dir}")
            return
        
        self.figure_dir = os.path.join(results_dir, "figures")
        os.makedirs(self.figure_dir, exist_ok=True)
        
        # JSONファイルを探す
        json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
        
        if json_files:
            json_path = os.path.join(results_dir, json_files[0])
            self.load_from_json(json_path)
        else:
            # Pickleファイルを探す
            pickle_files = [f for f in os.listdir(results_dir) if f.endswith('.pkl')]
            if pickle_files:
                pickle_path = os.path.join(results_dir, pickle_files[0])
                self.load_from_pickle(pickle_path)
            else:
                print("❌ JSONまたはPickleファイルが見つかりません")
    
    def load_from_json(self, json_file):
        """JSONファイルから読み込み"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            print(f"✅ JSON読み込み成功: {len(self.results)} ケース")
            
            if not self.figure_dir:
                self.figure_dir = os.path.join(os.path.dirname(json_file), "figures")
                os.makedirs(self.figure_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ JSON読み込みエラー: {e}")
    
    def load_from_pickle(self, pickle_file):
        """Pickleファイルから読み込み"""
        try:
            with open(pickle_file, 'rb') as f:
                self.results = pickle.load(f)
            print(f"✅ Pickle読み込み成功: {len(self.results)} ケース")
            
            if not self.figure_dir:
                self.figure_dir = os.path.join(os.path.dirname(pickle_file), "figures")
                os.makedirs(self.figure_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ Pickle読み込みエラー: {e}")
    
    def create_frobenius_distribution_chart(self, save=True, show=True):
        """フロベニウス分布比較チャート"""
        print("📊 フロベニウス分布チャート作成中...")
        
        if not self.results:
            print("❌ データがありません")
            return None
        
        # データの準備
        case_names = []
        case_distributions = []
        
        for case_name, result in self.results.items():
            if isinstance(result, dict) and 'results' in result:
                case_names.append(case_name.replace('Simple Test Case ', 'Case '))
                
                # フロベニウス分布を計算
                frobenius_count = Counter()
                for p, frobenius in result['results']:
                    frobenius_count[frobenius] += 1
                
                case_distributions.append(frobenius_count)
        
        if not case_distributions:
            print("❌ 有効なデータが見つかりません")
            return None
        
        # グラフ作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. ケース別分布（積み上げ棒グラフ）
        frobenius_elements = ['1', '-1', 'i', 'j']
        colors = {'1': '#1f77b4', '-1': '#ff7f0e', 'i': '#2ca02c', 'j': '#d62728'}
        
        bottoms = [0] * len(case_names)
        
        for element in frobenius_elements:
            values = [dist.get(element, 0) for dist in case_distributions]
            ax1.bar(case_names, values, bottom=bottoms, 
                   label=f'Frobenius: {element}', color=colors[element], alpha=0.8)
            bottoms = [b + v for b, v in zip(bottoms, values)]
        
        ax1.set_title('Frobenius Distribution by Case')
        ax1.set_ylabel('Count')
        ax1.legend()
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # 2. 全体分布（円グラフ）
        overall_distribution = Counter()
        for dist in case_distributions:
            for element, count in dist.items():
                overall_distribution[element] += count
        
        if overall_distribution:
            ax2.pie(overall_distribution.values(), labels=overall_distribution.keys(),
                   autopct='%1.1f%%', colors=[colors.get(k, '#gray') for k in overall_distribution.keys()],
                   startangle=90)
            ax2.set_title('Overall Frobenius Distribution')
        
        plt.tight_layout()
        
        if save and self.figure_dir:
            filename = os.path.join(self.figure_dir, 'frobenius_distribution.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 保存: {filename}")
        
        if show:
            plt.show()
        
        return fig
    
    def create_computation_statistics_chart(self, save=True, show=True):
        """計算統計チャート"""
        print("📊 計算統計チャート作成中...")
        
        if not self.results:
            print("❌ データがありません")
            return None
        
        # データの準備
        case_names = []
        success_counts = []
        total_counts = []
        
        for case_name, result in self.results.items():
            if isinstance(result, dict) and 'results' in result:
                case_names.append(case_name.replace('Simple Test Case ', 'Case '))
                success_counts.append(len(result['results']))
                # デフォルトでは結果数をトータルとして使用
                total_counts.append(len(result['results']))
        
        if not case_names:
            print("❌ 有効なデータが見つかりません")
            return None
        
        # グラフ作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. 成功計算数
        bars1 = ax1.bar(case_names, success_counts, color='lightblue', alpha=0.7)
        ax1.set_title('Successful Computations by Case')
        ax1.set_ylabel('Number of Successful Computations')
        ax1.grid(True, alpha=0.3)
        
        # 値をバーの上に表示
        for bar, count in zip(bars1, success_counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(success_counts)*0.01,
                    f'{count}', ha='center', va='bottom', fontsize=9)
        
        # 2. 成功率
        success_rates = [s/t*100 if t > 0 else 0 for s, t in zip(success_counts, total_counts)]
        bars2 = ax2.bar(case_names, success_rates, color='lightgreen', alpha=0.7)
        ax2.set_title('Success Rate by Case')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_ylim(0, 105)
        ax2.grid(True, alpha=0.3)
        
        # 値をバーの上に表示
        for bar, rate in zip(bars2, success_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # x軸ラベルの回転
        for ax in [ax1, ax2]:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save and self.figure_dir:
            filename = os.path.join(self.figure_dir, 'computation_statistics.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 保存: {filename}")
        
        if show:
            plt.show()
        
        return fig
    
    def create_summary_dashboard(self, save=True, show=True):
        """総合サマリーダッシュボード"""
        print("📊 総合サマリー作成中...")
        
        if not self.results:
            print("❌ データがありません")
            return None
        
        # データ統計
        total_cases = len(self.results)
        successful_cases = 0
        total_computations = 0
        successful_computations = 0
        
        for case_name, result in self.results.items():
            if isinstance(result, dict) and 'results' in result:
                successful_cases += 1
                case_computations = len(result['results'])
                successful_computations += case_computations
                total_computations += case_computations
        
        # グラフ作成
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 実験概要（テキスト）
        ax1.axis('off')
        summary_text = [
            "Experiment Summary",
            "",
            f"Total Cases: {successful_cases}/{total_cases}",
            f"Total Computations: {total_computations:,}",
            f"Successful Computations: {successful_computations:,}",
            f"Overall Success Rate: {successful_computations/total_computations*100:.1f}%" if total_computations > 0 else "Overall Success Rate: 0%"
        ]
        
        for i, text in enumerate(summary_text):
            ax1.text(0.1, 0.9 - i*0.15, text, fontsize=14, 
                    weight='bold' if i == 0 else 'normal',
                    transform=ax1.transAxes)
        
        # 2. フロベニウス全体分布
        overall_frobenius = Counter()
        for case_name, result in self.results.items():
            if isinstance(result, dict) and 'results' in result:
                for p, frobenius in result['results']:
                    overall_frobenius[frobenius] += 1
        
        if overall_frobenius:
            colors_pie = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            ax2.pie(overall_frobenius.values(), labels=overall_frobenius.keys(),
                   autopct='%1.1f%%', colors=colors_pie, startangle=90)
            ax2.set_title('Overall Frobenius Distribution')
        
        # 3. ケース別成功計算数
        case_names = []
        success_counts = []
        
        for case_name, result in self.results.items():
            if isinstance(result, dict) and 'results' in result:
                case_names.append(case_name.replace('Simple Test Case ', 'Case '))
                success_counts.append(len(result['results']))
        
        if case_names:
            ax3.bar(case_names, success_counts, color='lightcoral', alpha=0.7)
            ax3.set_title('Successful Computations by Case')
            ax3.set_ylabel('Count')
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            ax3.grid(True, alpha=0.3)
        
        # 4. 統計サマリー
        ax4.axis('off')
        if case_names and success_counts:
            stats_text = [
                "Statistics",
                "",
                f"Average computations per case: {np.mean(success_counts):.1f}",
                f"Max computations: {max(success_counts)}",
                f"Min computations: {min(success_counts)}",
                f"Standard deviation: {np.std(success_counts):.1f}"
            ]
            
            for i, text in enumerate(stats_text):
                ax4.text(0.1, 0.9 - i*0.15, text, fontsize=12,
                        weight='bold' if i == 0 else 'normal',
                        transform=ax4.transAxes)
        
        plt.suptitle('Experiment Summary Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save and self.figure_dir:
            filename = os.path.join(self.figure_dir, 'summary_dashboard.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 保存: {filename}")
        
        if show:
            plt.show()
        
        return fig
    
    def create_all_visualizations(self):
        """全ての可視化を一括作成"""
        print("🎨 全可視化を作成中...")
        
        figures = []
        
        try:
            # 1. フロベニウス分布
            fig1 = self.create_frobenius_distribution_chart(show=False)
            if fig1:
                figures.append(('frobenius_distribution', fig1))
        except Exception as e:
            print(f"⚠️  フロベニウス分布作成エラー: {e}")
        
        try:
            # 2. 計算統計
            fig2 = self.create_computation_statistics_chart(show=False)
            if fig2:
                figures.append(('computation_statistics', fig2))
        except Exception as e:
            print(f"⚠️  計算統計作成エラー: {e}")
        
        try:
            # 3. 総合サマリー
            fig3 = self.create_summary_dashboard(show=False)
            if fig3:
                figures.append(('summary_dashboard', fig3))
        except Exception as e:
            print(f"⚠️  サマリーダッシュボード作成エラー: {e}")
        
        print(f"✅ 可視化完了！作成されたグラフ数: {len(figures)}")
        if self.figure_dir:
            print(f"📁 図の保存先: {self.figure_dir}")
        
        return figures

# 便利な関数
def visualize_omar_results(results_dir=None, json_file=None, pickle_file=None):
    """
    保存された結果から全ての可視化を作成
    
    Parameters:
    - results_dir: 結果ディレクトリパス
    - json_file: JSONファイルパス（直接指定）
    - pickle_file: Pickleファイルパス（直接指定）
    
    Returns:
    - visualizer: 可視化オブジェクト
    """
    print("🎨 結果可視化を開始します...")
    
    # 可視化ツール初期化
    visualizer = ChebyshevBiasVisualizer(
        results_dir=results_dir, 
        json_file=json_file, 
        pickle_file=pickle_file
    )
    
    # 全可視化作成
    figures = visualizer.create_all_visualizations()
    
    print("\\n🎉 可視化完了！")
    if visualizer.figure_dir:
        print(f"📁 結果は以下に保存されました: {visualizer.figure_dir}")
    
    return visualizer

# メイン実行部分
if __name__ == "__main__":
    print("="*80)
    print("Chebyshevバイアス可視化ツール")
    print("Visualization Tools for Experiment Results")
    print("="*80)
    
    print("\\n🎨 使用方法:")
    print("1. visualize_omar_results(results_dir='path/to/results')")
    print("2. visualize_omar_results(json_file='path/to/file.json')")
    
    print("\\n💡 使用例:")
    print("   sage: visualizer = visualize_omar_results(results_dir='./debug_results_20240101_120000')")
    print("   sage: visualizer = visualize_omar_results(json_file='results.json')")
    
    print("\\n📊 作成されるグラフ:")
    print("   - フロベニウス分布比較")
    print("   - 計算統計（成功率、計算数等）")
    print("   - 総合サマリーダッシュボード")
    
    print("\\n" + "="*80)
    print("🎯 準備完了 - 結果ディレクトリまたはファイルを指定してください")
    print("="*80)
