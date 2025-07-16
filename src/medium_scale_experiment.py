        json_filename = os.path.join(self.output_dir, 'medium_scale_experiment_complete.json')
        json_success, json_error = safe_json_save(final_data, json_filename)
        
        if json_success:
            print("✅ JSON保存成功: {}".format(str(json_filename)))
        else:
            print("❌ JSON保存エラー: {}".format(str(json_error)))
        
        # Pickle保存（常に実行）
        pickle_filename = os.path.join(self.output_dir, 'medium_scale_experiment_complete.pkl')
        try:
            with open(pickle_filename, 'wb') as f:
                pickle.dump(final_data, f)
            pickle_success = True
            print("✅ Pickle保存成功: {}".format(str(pickle_filename)))
        except Exception as e:
            pickle_success = False
            print("❌ Pickle保存エラー: {}".format(str(e)))
        
        print("💾 最終結果保存完了")
        print("   JSON: {}".format('✅' if json_success else '❌'))
        print("   Pickle: {}".format('✅' if pickle_success else '❌'))
    
    def run_full_experiment(self):
        """
        全13ケースの実験実行
        """
        print("="*80)
        print("🚀 Omar論文13ケース中規模検証実験開始")
        print("📊 実験規模: x_max = {:,}".format(int(self.x_max)))
        print("🎯 対象ケース: {}個".format(len(self.omar_cases)))
        print("="*80)
        
        self.experiment_start_time = time.time()
        
        for case_index, case_data in enumerate(self.omar_cases):
            print("\n📍 Progress: {}/{}".format(case_index + 1, len(self.omar_cases)))
            
            case_result = self.run_single_case_experiment(case_data)
            
            # 結果を保存
            case_name = case_data['name']
            self.results[case_name] = case_result
            
            # ケースごとの結果を即座に保存
            self._save_case_result(case_name, case_result)
            
            # 進捗ログ
            if 'error' not in case_result:
                success_count = case_result.get('computation_stats', {}).get('successful_computations', 0)
                execution_time = case_result.get('execution_time', 0)
                
                progress_entry = {
                    'case_index': case_index + 1,
                    'case_name': case_name,
                    'success_count': success_count,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.progress_log.append(progress_entry)
                
                print("✅ {} 完了: {:,}計算, {:.1f}秒".format(
                    str(case_name), int(success_count), float(execution_time)
                ))
            else:
                print("❌ {} 失敗".format(str(case_name)))
        
        total_duration = time.time() - self.experiment_start_time
        
        print("\n" + "="*80)
        print("🎉 全実験完了!")
        print("⏱️  総実行時間: {:.2f}時間".format(float(total_duration/3600)))
        print("="*80)
        
        # 最終結果の保存と分析
        self._save_final_results()
        self._generate_summary_report()
        
        return self.results
    
    def _generate_summary_report(self):
        """サマリーレポートの生成"""
        try:
            print("\n" + "="*80)
            print("📊 実験サマリーレポート")
            print("="*80)
            
            successful_cases = 0
            total_computations = 0
            total_successful_computations = 0
            
            for case_name, result in self.results.items():
                if 'error' not in result:
                    successful_cases += 1
                    stats = result.get('computation_stats', {})
                    total_computations += stats.get('total_primes', 0)
                    total_successful_computations += stats.get('successful_computations', 0)
                    
                    # 個別ケースサマリー
                    print("\n{}:".format(str(case_name)))
                    print("  成功計算数: {:,}".format(int(stats.get('successful_computations', 0))))
                    print("  実行時間: {:.1f}秒".format(float(result.get('execution_time', 0))))
                    print("  成功率: {:.2f}%".format(float(result.get('success_rate', 0))))
                    
                    # フロベニウス分布
                    frobenius_dist = Counter()
                    for p, cc in result.get('results', []):
                        frobenius_dist[cc] += 1
                    
                    if frobenius_dist:
                        total_frob = sum(frobenius_dist.values())
                        print("  フロベニウス分布:")
                        for cc in ['1', '-1', 'i', 'j', 'k']:
                            count = frobenius_dist.get(cc, 0)
                            pct = count / total_frob * 100 if total_frob > 0 else 0
                            print("    {}: {:,} ({:.1f}%)".format(str(cc), int(count), float(pct)))
            
            print("\n📈 全体統計:")
            print("  成功ケース: {}/{}".format(successful_cases, len(self.omar_cases)))
            print("  総計算数: {:,}".format(int(total_computations)))
            print("  成功計算数: {:,}".format(int(total_successful_computations)))
            
            if total_computations > 0:
                overall_success_rate = total_successful_computations / total_computations * 100
                print("  全体成功率: {:.2f}%".format(float(overall_success_rate)))
            
            total_duration = time.time() - self.experiment_start_time
            print("  総実行時間: {:.2f}時間".format(float(total_duration/3600)))
            print("  平均計算速度: {:.0f} 計算/時間".format(
                float(total_successful_computations/(total_duration/3600))
            ))
            
            print("="*80)
            
        except Exception as e:
            print("❌ サマリーレポート生成エラー: {}".format(str(e)))

# 実行用メイン関数
def run_medium_scale_verification():
    """
    中規模検証の実行 (JSON修正版)
    """
    print("🚀 中規模検証実行開始 (JSON修正版)")
    print("⚠️  注意: この計算は数時間かかる可能性があります")
    
    # 実験インスタンス作成
    experiment = MediumScaleExperiment(x_max=10**6)
    
    # 実験実行
    results = experiment.run_full_experiment()
    
    print("🎉 中規模検証完了!")
    print("📁 結果保存先: {}".format(experiment.output_dir))
    
    return experiment, results

# 軽量テスト関数 (小規模での動作確認用)
def run_test_verification(x_max=10**4):
    """
    テスト用の小規模検証 (x_max = 10^4)
    """
    print("🧪 テスト検証実行開始")
    print("📊 実験規模: x_max = {:,} (テストモード)".format(int(x_max)))
    
    experiment = MediumScaleExperiment(x_max=x_max)
    
    # 最初の3ケースのみテスト実行
    test_cases = experiment.omar_cases[:3]
    experiment.omar_cases = test_cases
    
    print("🎯 テストケース数: {}個".format(len(test_cases)))
    
    results = experiment.run_full_experiment()
    
    print("🧪 テスト検証完了!")
    print("📁 結果保存先: {}".format(str(experiment.output_dir)))
    
    return experiment, results

# 単一ケーステスト関数
def run_single_case_test(case_index=0, x_max=10**3):
    """
    単一ケースのテスト実行
    """
    print("🔬 単一ケーステスト実行開始 (Case {})".format(case_index + 1))
    
    experiment = MediumScaleExperiment(x_max=x_max)
    
    if case_index >= len(experiment.omar_cases):
        print("❌ エラー: ケースインデックス {} が範囲外です".format(case_index))
        return None, None
    
    case_data = experiment.omar_cases[case_index]
    print("🎯 テストケース: {}".format(str(case_data['name'])))
    
    case_result = experiment.run_single_case_experiment(case_data)
    
    # 結果保存
    experiment._save_case_result(case_data['name'], case_result)
    
    print("🔬 単一ケーステスト完了!")
    print("📁 結果保存先: {}".format(str(experiment.output_dir)))
    
    return experiment, case_result

# 依存関係チェック関数
def check_dependencies():
    """
    必要な依存関係をチェック
    """
    print("🔍 依存関係チェック開始")
    
    dependencies = {
        'SageMath基本': True,  # SageMathが動いていれば基本機能は利用可能
        'tqdm': TQDM_AVAILABLE,
        'matplotlib': True,  # SageMathに標準で含まれる
        'numpy': True,       # SageMathに標準で含まれる
        'pandas': True,      # 通常SageMathに含まれる
    }
    
    try:
        import pandas as pd
        dependencies['pandas'] = True
    except ImportError:
        dependencies['pandas'] = False
        print("⚠️  pandas が利用できません - 辞書ベースの処理を使用")
    
    try:
        import matplotlib.pyplot as plt
        dependencies['matplotlib'] = True
    except ImportError:
        dependencies['matplotlib'] = False
        print("❌ matplotlib が利用できません")
    
    print("\n📊 依存関係チェック結果:")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        print("   {} {}: {}".format(status, dep, '利用可能' if available else '利用不可'))
    
    critical_deps = ['SageMath基本', 'numpy']
    missing_critical = [dep for dep in critical_deps if not dependencies[dep]]
    
    if missing_critical:
        print("\n❌ 重要な依存関係が不足: {}".format(missing_critical))
        return False
    else:
        print("\n✅ 実行に必要な依存関係は揃っています")
        if not dependencies['tqdm']:
            print("📊 tqdmが無い場合は基本進捗表示を使用します")
        return True

# メイン実行部分
if __name__ == "__main__":
    print("="*80)
    print("Omar論文13ケース中規模検証システム (JSON修正版)")
    print("Numerical Experiments for Chebyshev's Bias in Quaternion Fields")
    print("x_max = 10^6 (Medium Scale Verification)")
    print("="*80)
    
    # 依存関係チェック
    if not check_dependencies():
        print("❌ 依存関係に問題があります。SageMath環境を確認してください。")
        exit(1)
    
    print("\n🚀 実行オプション:")
    print("1. run_medium_scale_verification()     - フル実行 (10^6, 全13ケース)")
    print("2. run_test_verification()             - テスト実行 (10^4, 最初の3ケース)")
    print("3. run_single_case_test()              - 単一ケーステスト (10^3, 1ケース)")
    print("4. check_dependencies()                - 依存関係のみチェック")
    
    print("\n💡 使用例:")
    print("   sage: experiment, results = run_medium_scale_verification()")
    print("   sage: experiment, results = run_test_verification(x_max=5000)")
    print("   sage: experiment, result = run_single_case_test(case_index=1, x_max=1000)")
    
    print("\n" + "="*80)
    print("🎯 準備完了 - 上記の関数を呼び出してください")
    print("="*80)
