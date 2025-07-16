        # 2. 実行時間
        bars2 = ax2.bar(case_names, execution_times, color='lightcoral', alpha=0.7)
        ax2.set_title('Execution Time by Case')
        ax2.set_ylabel('Execution Time (minutes)')
        ax2.grid(True, alpha=0.3)
        
        # 実行時間の値をバーの上に表示
        for bar, time_val in zip(bars2, execution_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(execution_times)*0.01,
                    '{:.1f}min'.format(time_val), ha='center', va='bottom', fontsize=9)
        
        # 3. 成功計算数
        bars3 = ax3.bar(case_names, total_computations, color='lightgreen', alpha=0.7)
        ax3.set_title('Successful Computations by Case')
        ax3.set_ylabel('Number of Successful Computations')
        ax3.grid(True, alpha=0.3)
        
        # 成功計算数の値をバーの上に表示
        for bar, count in zip(bars3, total_computations):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(total_computations)*0.01,
                    '{:,}'.format(int(count)), ha='center', va='bottom', fontsize=9)
        
        # 4. 計算効率 (成功計算数/実行時間)
        efficiency = [comp/time_val if time_val > 0 else 0 for comp, time_val in zip(total_computations, execution_times)]
        bars4 = ax4.bar(case_names, efficiency, color='gold', alpha=0.7)
        ax4.set_title('Computation Efficiency by Case')
        ax4.set_ylabel('Successful Computations per Minute')
        ax4.grid(True, alpha=0.3)
        
        # 効率の値をバーの上に表示
        for bar, eff in zip(bars4, efficiency):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + max(efficiency)*0.01,
                    '{:.1f}'.format(eff), ha='center', va='bottom', fontsize=9)
        
        # x軸ラベルの回転
        for ax in [ax1, ax2, ax3, ax4]:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.figure_dir, 'computation_statistics.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print("💾 保存: {}".format(filename))
        
        if show:
            plt.show()
        
        return fig
    
    def create_bias_coefficient_comparison(self, save=True, show=True):
        """
        理論バイアス係数の比較グラフ
        """
        print("📊 バイアス係数比較グラフ作成中...")
        
        # データの準備
        case_names = []
        bias_data = []
        
        for case_name, result in self.results.items():
            if 'error' in result:
                continue
                
            case_names.append(case_name.replace('Omar Case ', 'Case '))
            
            bias_coeffs = result.get('total_bias_coeffs', {})
            bias_data.append(bias_coeffs)
        
        if not bias_data:
            print("❌ バイアス係数データが見つかりません")
            return None
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 色の設定
        colors = {
            '1': '#1f77b4',
            '-1': '#ff7f0e',
            'i': '#2ca02c',
            'j': '#d62728',
            'k': '#9467bd'
        }
        
        x = np.arange(len(case_names))
        width = 0.15
        
        # 各共役類のバイアス係数をプロット
        for i, cc in enumerate(['1', '-1', 'i', 'j', 'k']):
            values = [bias.get(cc, 0) for bias in bias_data]
            offset = (i - 2) * width
            ax.bar(x + offset, values, width, label=cc, color=colors[cc], alpha=0.8)
        
        ax.set_xlabel('Cases')
        ax.set_ylabel('Bias Coefficient')
        ax.set_title('Theoretical Bias Coefficients for Omar Cases\n(M + m values)')
        ax.set_xticks(x)
        ax.set_xticklabels(case_names, rotation=45, ha='right')
        ax.legend(title='Conjugacy Class')
        ax.grid(True, alpha=0.3)
        
        # ゼロ線を強調
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.figure_dir, 'bias_coefficients.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print("💾 保存: {}".format(filename))
        
        if show:
            plt.show()
        
        return fig
    
    def create_comprehensive_summary(self, save=True, show=True):
        """
        全体的なサマリーダッシュボード
        """
        print("📊 総合サマリーダッシュボード作成中...")
        
        # データ収集
        case_names = []
        success_rates = []
        execution_times = []
        total_successful = []
        
        # 全ケースの統計
        overall_stats = {
            'total_cases': 0,
            'successful_cases': 0,
            'total_computations': 0,
            'total_successful_computations': 0,
            'total_execution_time': 0
        }
        
        for case_name, result in self.results.items():
            overall_stats['total_cases'] += 1
            
            if 'error' not in result:
                overall_stats['successful_cases'] += 1
                
                case_names.append(case_name.replace('Omar Case ', 'Case '))
                success_rates.append(result.get('success_rate', 0))
                execution_times.append(result.get('execution_time', 0))
                
                stats = result.get('computation_stats', {})
                successful_comps = stats.get('successful_computations', 0)
                total_successful.append(successful_comps)
                
                overall_stats['total_successful_computations'] += successful_comps
                overall_stats['total_computations'] += stats.get('total_primes', 0)
                overall_stats['total_execution_time'] += result.get('execution_time', 0)
        
        # グラフ作成
        fig = plt.figure(figsize=(20, 16))
        
        # グリッドレイアウト
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. 実験概要 (テキスト)
        ax_summary = fig.add_subplot(gs[0, :2])
        ax_summary.axis('off')
        
        summary_text = [
            "Omar's 13 Cases Medium Scale Verification Results",
            "",
            "総実験ケース数: {} / {}".format(overall_stats['successful_cases'], overall_stats['total_cases']),
            "総実行時間: {:.2f} 時間".format(overall_stats['total_execution_time'] / 3600),
            "総計算数: {:,}".format(overall_stats['total_computations']),
            "成功計算数: {:,}".format(overall_stats['total_successful_computations']),
            "全体成功率: {:.2f}%".format(
                overall_stats['total_successful_computations'] / overall_stats['total_computations'] * 100
                if overall_stats['total_computations'] > 0 else 0
            ),
            "平均計算速度: {:.0f} 計算/時間".format(
                overall_stats['total_successful_computations'] / (overall_stats['total_execution_time'] / 3600)
                if overall_stats['total_execution_time'] > 0 else 0
            )
        ]
        
        for i, text in enumerate(summary_text):
            ax_summary.text(0.1, 0.9 - i*0.12, text, fontsize=12, 
                          weight='bold' if i == 0 else 'normal',
                          transform=ax_summary.transAxes)
        
        # 2. 成功率分布
        ax_success = fig.add_subplot(gs[0, 2:])
        ax_success.hist(success_rates, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax_success.set_title('Success Rate Distribution')
        ax_success.set_xlabel('Success Rate (%)')
        ax_success.set_ylabel('Number of Cases')
        ax_success.grid(True, alpha=0.3)
        
        # 3. ケース別成功率
        ax_rates = fig.add_subplot(gs[1, :])
        bars = ax_rates.bar(case_names, success_rates, color='lightcoral', alpha=0.7)
        ax_rates.set_title('Success Rate by Case')
        ax_rates.set_ylabel('Success Rate (%)')
        ax_rates.set_ylim(0, 100)
        ax_rates.grid(True, alpha=0.3)
        plt.setp(ax_rates.get_xticklabels(), rotation=45, ha='right')
        
        # 4. 実行時間 vs 成功計算数
        ax_scatter = fig.add_subplot(gs[2, :2])
        scatter = ax_scatter.scatter(execution_times, total_successful, alpha=0.7, s=100, c=success_rates, 
                                   cmap='viridis', edgecolors='black')
        ax_scatter.set_xlabel('Execution Time (seconds)')
        ax_scatter.set_ylabel('Successful Computations')
        ax_scatter.set_title('Execution Time vs Successful Computations')
        ax_scatter.grid(True, alpha=0.3)
        
        # カラーバー
        cbar = plt.colorbar(scatter, ax=ax_scatter)
        cbar.set_label('Success Rate (%)')
        
        # 5. 効率性分析
        ax_efficiency = fig.add_subplot(gs[2, 2:])
        efficiency = [succ/time_val if time_val > 0 else 0 for succ, time_val in zip(total_successful, execution_times)]
        ax_efficiency.bar(case_names, efficiency, color='gold', alpha=0.7)
        ax_efficiency.set_title('Computation Efficiency (Computations/Second)')
        ax_efficiency.set_ylabel('Computations per Second')
        ax_efficiency.grid(True, alpha=0.3)
        plt.setp(ax_efficiency.get_xticklabels(), rotation=45, ha='right')
        
        # 6. 全体的なフロベニウス分布
        ax_overall_dist = fig.add_subplot(gs[3, :2])
        
        # 全ケースのフロベニウス分布を統合
        overall_frobenius = Counter()
        for case_name, result in self.results.items():
            if 'error' not in result:
                for p, cc in result.get('results', []):
                    overall_frobenius[cc] += 1
        
        if overall_frobenius:
            colors_pie = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            ax_overall_dist.pie(overall_frobenius.values(), labels=overall_frobenius.keys(), 
                              autopct='%1.1f%%', colors=colors_pie, startangle=90)
            ax_overall_dist.set_title('Overall Frobenius Distribution\n(All Cases Combined)')
        
        # 7. ケース比較 (正規化されたメトリクス)
        ax_comparison = fig.add_subplot(gs[3, 2:])
        
        if success_rates and execution_times and total_successful:
            norm_success = [x/max(success_rates) for x in success_rates]
            norm_efficiency = [x/max(efficiency) for x in efficiency]
            norm_computations = [x/max(total_successful) for x in total_successful]
            
            x_pos = np.arange(len(case_names))
            width = 0.25
            
            ax_comparison.bar(x_pos - width, norm_success, width, label='Success Rate', alpha=0.7)
            ax_comparison.bar(x_pos, norm_efficiency, width, label='Efficiency', alpha=0.7)
            ax_comparison.bar(x_pos + width, norm_computations, width, label='Total Computations', alpha=0.7)
            
            ax_comparison.set_title('Normalized Performance Comparison')
            ax_comparison.set_ylabel('Normalized Score (0-1)')
            ax_comparison.set_xticks(x_pos)
            ax_comparison.set_xticklabels(case_names, rotation=45, ha='right')
            ax_comparison.legend()
            ax_comparison.grid(True, alpha=0.3)
        
        plt.suptitle('Omar\'s 13 Cases: Comprehensive Analysis Dashboard', fontsize=16, fontweight='bold')
        
        if save:
            filename = os.path.join(self.figure_dir, 'comprehensive_summary.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print("💾 保存: {}".format(filename))
        
        if show:
            plt.show()
        
        return fig
    
    def create_all_visualizations(self, create_individual_bias=True):
        """
        全ての可視化を一括作成
        """
        print("🎨 全可視化を作成中...")
        
        figures = []
        
        # 1. 個別Chebyshevバイアスプロット（オプション）
        if create_individual_bias:
            for case_name in self.results.keys():
                if 'error' not in self.results[case_name]:
                    try:
                        fig = self.create_chebyshev_bias_plot(case_name, show=False)
                        if fig:
                            figures.append(('chebyshev_bias_{}'.format(case_name), fig))
                    except Exception as e:
                        print("⚠️  {} の処理でエラー: {}".format(case_name, str(e)))
        
        # 2. フロベニウス分布
        fig1 = self.create_frobenius_distribution_chart(show=False)
        if fig1:
            figures.append(('frobenius_distribution', fig1))
        
        # 3. バイアス係数比較
        fig2 = self.create_bias_coefficient_comparison(show=False)
        if fig2:
            figures.append(('bias_coefficients', fig2))
        
        # 4. 計算統計
        fig3 = self.create_computation_statistics_chart(show=False)
        if fig3:
            figures.append(('computation_statistics', fig3))
        
        # 5. 総合サマリー
        fig4 = self.create_comprehensive_summary(show=False)
        if fig4:
            figures.append(('comprehensive_summary', fig4))
        
        print("✅ 全可視化完了！")
        print("📁 図の保存先: {}".format(self.figure_dir))
        print("📊 作成されたグラフ数: {}".format(len(figures)))
        
        return figures

# 便利な関数
def visualize_omar_results(results_dir=None, json_file=None, pickle_file=None, 
                          create_individual_bias=True):
    """
    保存された結果から全ての可視化を作成
    
    Parameters:
    - results_dir: 結果ディレクトリパス
    - json_file: JSONファイルパス（直接指定）
    - pickle_file: Pickleファイルパス（直接指定）
    - create_individual_bias: 個別Chebyshevバイアスプロットを作成するか
    
    Returns:
    - visualizer: 可視化オブジェクト
    """
    print("🎨 Omar結果可視化を開始します...")
    
    # 可視化ツール初期化
    visualizer = ChebyshevBiasVisualizer(
        results_dir=results_dir, 
        json_file=json_file, 
        pickle_file=pickle_file
    )
    
    # 全可視化作成
    figures = visualizer.create_all_visualizations(create_individual_bias=create_individual_bias)
    
    print("\n🎉 可視化完了！")
    print("📁 結果は以下に保存されました: {}".format(visualizer.figure_dir))
    
    return visualizer

def create_single_bias_plot(results_dir, case_name):
    """
    特定ケースのChebyshevバイアスプロットのみ作成
    """
    visualizer = ChebyshevBiasVisualizer(results_dir=results_dir)
    return visualizer.create_chebyshev_bias_plot(case_name)

# メイン実行部分
if __name__ == "__main__":
    print("="*80)
    print("Chebyshevバイアス可視化ツール")
    print("Visualization Tools for Omar's 13 Cases Results")
    print("="*80)
    
    print("\n🎨 使用方法:")
    print("1. visualize_omar_results(results_dir='path/to/results')")
    print("2. visualize_omar_results(json_file='path/to/file.json')")
    print("3. create_single_bias_plot(results_dir='path', case_name='Omar Case 1')")
    
    print("\n💡 使用例:")
    print("   sage: visualizer = visualize_omar_results(results_dir='./medium_scale_results_20240101_120000')")
    print("   sage: visualizer = visualize_omar_results(json_file='results.json')")
    print("   sage: fig = create_single_bias_plot('./results', 'Omar Case 1')")
    
    print("\n📊 作成されるグラフ:")
    print("   - フロベニウス分布比較")
    print("   - バイアス係数比較") 
    print("   - 計算統計（成功率、実行時間等）")
    print("   - 総合サマリーダッシュボード")
    print("   - 個別Chebyshevバイアスプロット（オプション）")
    
    print("\n" + "="*80)
    print("🎯 準備完了 - 結果ディレクトリまたはファイルを指定してください")
    print("="*80)
