#!/usr/bin/env sage

"""
軽量可視化ツール (matplotlib依存なし)
Omar's 13 Cases結果の基本的なレポート作成

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
"""

import json
import os
import pickle
from datetime import datetime
from collections import Counter

class SimpleReportGenerator:
    """軽量レポート生成クラス（matplotlib不要）"""
    
    def __init__(self, results_dir=None, json_file=None, pickle_file=None):
        """
        初期化
        
        Parameters:
        - results_dir: 結果ディレクトリパス
        - json_file: JSONファイルパス（直接指定）
        - pickle_file: Pickleファイルパス（直接指定）
        """
        self.results = {}
        self.report_dir = None
        
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
        
        self.report_dir = os.path.join(results_dir, "reports")
        os.makedirs(self.report_dir, exist_ok=True)
        
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
                # デバッグ用の簡単なレポートを作成
                self.create_debug_report(results_dir)
    
    def load_from_json(self, json_file):
        """JSONファイルから読み込み"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            print(f"✅ JSON読み込み成功: {len(self.results)} ケース")
            
            if not self.report_dir:
                self.report_dir = os.path.join(os.path.dirname(json_file), "reports")
                os.makedirs(self.report_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ JSON読み込みエラー: {e}")
    
    def load_from_pickle(self, pickle_file):
        """Pickleファイルから読み込み"""
        try:
            with open(pickle_file, 'rb') as f:
                self.results = pickle.load(f)
            print(f"✅ Pickle読み込み成功: {len(self.results)} ケース")
            
            if not self.report_dir:
                self.report_dir = os.path.join(os.path.dirname(pickle_file), "reports")
                os.makedirs(self.report_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ Pickle読み込みエラー: {e}")
    
    def create_debug_report(self, results_dir):
        """デバッグディレクトリの簡単なレポート作成"""
        try:
            print("📝 デバッグレポートを作成中...")
            
            # ディレクトリ内容の確認
            files = os.listdir(results_dir)
            print(f"📁 ディレクトリ内容: {files}")
            
            # 簡単な統計を作成
            self.results = {
                "debug_info": {
                    "directory": results_dir,
                    "files": files,
                    "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # レポート作成
            self.create_text_report()
            
        except Exception as e:
            print(f"❌ デバッグレポート作成エラー: {e}")
    
    def analyze_results(self):
        """結果の分析"""
        if not self.results:
            return {}
        
        analysis = {
            'total_cases': 0,
            'successful_cases': 0,
            'total_computations': 0,
            'successful_computations': 0,
            'frobenius_distribution': Counter(),
            'case_statistics': {}
        }
        
        for case_name, result in self.results.items():
            analysis['total_cases'] += 1
            
            # デバッグ情報の場合はスキップ
            if case_name == "debug_info":
                continue
                
            if isinstance(result, dict):
                if 'results' in result and isinstance(result['results'], list):
                    analysis['successful_cases'] += 1
                    case_computations = len(result['results'])
                    analysis['successful_computations'] += case_computations
                    analysis['total_computations'] += case_computations
                    
                    # フロベニウス分布
                    case_frobenius = Counter()
                    for computation in result['results']:
                        if isinstance(computation, (list, tuple)) and len(computation) >= 2:
                            frobenius = computation[1]
                            analysis['frobenius_distribution'][frobenius] += 1
                            case_frobenius[frobenius] += 1
                    
                    # ケース統計
                    analysis['case_statistics'][case_name] = {
                        'computations': case_computations,
                        'frobenius_distribution': dict(case_frobenius),
                        'success_rate': 100.0  # デフォルト値
                    }
                    
                elif 'successful' in result and 'failed' in result:
                    # 別の結果形式
                    analysis['successful_cases'] += 1
                    successful = result['successful']
                    failed = result['failed']
                    total = successful + failed
                    
                    analysis['successful_computations'] += successful
                    analysis['total_computations'] += total
                    
                    analysis['case_statistics'][case_name] = {
                        'computations': successful,
                        'total_attempted': total,
                        'success_rate': successful / total * 100 if total > 0 else 0
                    }
        
        return analysis
    
    def create_text_report(self):
        """テキストレポートの作成"""
        print("📝 テキストレポート作成中...")
        
        analysis = self.analyze_results()
        
        # レポート内容
        report_lines = [
            "=" * 80,
            "実験結果レポート",
            "=" * 80,
            "",
            f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "■ 実験概要",
            f"  総ケース数: {analysis.get('total_cases', 0)}",
            f"  成功ケース数: {analysis.get('successful_cases', 0)}",
            f"  総計算数: {analysis.get('total_computations', 0):,}",
            f"  成功計算数: {analysis.get('successful_computations', 0):,}",
            ""
        ]
        
        # 成功率計算
        if analysis.get('total_computations', 0) > 0:
            success_rate = analysis['successful_computations'] / analysis['total_computations'] * 100
            report_lines.append(f"  全体成功率: {success_rate:.2f}%")
        else:
            report_lines.append("  全体成功率: 計算なし")
        
        report_lines.extend(["", "■ フロベニウス分布（全体）"])
        
        frobenius_dist = analysis.get('frobenius_distribution', {})
        if frobenius_dist:
            total_frobenius = sum(frobenius_dist.values())
            for element, count in sorted(frobenius_dist.items()):
                percentage = count / total_frobenius * 100 if total_frobenius > 0 else 0
                report_lines.append(f"  {element}: {count:,} ({percentage:.1f}%)")
        else:
            report_lines.append("  データなし")
        
        report_lines.extend(["", "■ ケース別詳細"])
        
        case_stats = analysis.get('case_statistics', {})
        for case_name, stats in case_stats.items():
            report_lines.extend([
                "",
                f"◆ {case_name}",
                f"  計算数: {stats.get('computations', 0):,}",
                f"  成功率: {stats.get('success_rate', 0):.1f}%"
            ])
            
            if 'frobenius_distribution' in stats:
                report_lines.append("  フロベニウス分布:")
                for element, count in sorted(stats['frobenius_distribution'].items()):
                    total_case = stats.get('computations', 0)
                    percentage = count / total_case * 100 if total_case > 0 else 0
                    report_lines.append(f"    {element}: {count} ({percentage:.1f}%)")
        
        report_lines.extend(["", "=" * 80, "レポート終了", "=" * 80])
        
        # ファイルに保存
        if self.report_dir:
            report_file = os.path.join(self.report_dir, 'experiment_report.txt')
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                print(f"💾 レポート保存: {report_file}")
            except Exception as e:
                print(f"❌ レポート保存エラー: {e}")
        
        # コンソールにも表示
        print('\n'.join(report_lines))
        
        return report_lines
    
    def create_summary_stats(self):
        """統計サマリーを作成"""
        print("📊 統計サマリー作成中...")
        
        analysis = self.analyze_results()
        
        # 基本統計
        basic_stats = {
            'cases': {
                'total': analysis.get('total_cases', 0),
                'successful': analysis.get('successful_cases', 0),
                'success_rate': 0
            },
            'computations': {
                'total': analysis.get('total_computations', 0),
                'successful': analysis.get('successful_computations', 0),
                'success_rate': 0
            },
            'frobenius': dict(analysis.get('frobenius_distribution', {}))
        }
        
        # 成功率計算
        if basic_stats['cases']['total'] > 0:
            basic_stats['cases']['success_rate'] = basic_stats['cases']['successful'] / basic_stats['cases']['total'] * 100
        
        if basic_stats['computations']['total'] > 0:
            basic_stats['computations']['success_rate'] = basic_stats['computations']['successful'] / basic_stats['computations']['total'] * 100
        
        # コンソール表示
        print(f"\n📈 統計サマリー:")
        print(f"  ケース成功率: {basic_stats['cases']['success_rate']:.1f}% ({basic_stats['cases']['successful']}/{basic_stats['cases']['total']})")
        print(f"  計算成功率: {basic_stats['computations']['success_rate']:.1f}% ({basic_stats['computations']['successful']:,}/{basic_stats['computations']['total']:,})")
        
        if basic_stats['frobenius']:
            print(f"  フロベニウス分布: {basic_stats['frobenius']}")
        
        return basic_stats

# 便利な関数
def visualize_omar_results(results_dir=None, json_file=None, pickle_file=None):
    """
    保存された結果からレポートを作成（matplotlib不要版）
    
    Parameters:
    - results_dir: 結果ディレクトリパス
    - json_file: JSONファイルパス（直接指定）
    - pickle_file: Pickleファイルパス（直接指定）
    
    Returns:
    - generator: レポート生成オブジェクト
    """
    print("📝 結果レポート作成を開始します...")
    
    try:
        # レポート生成ツール初期化
        generator = SimpleReportGenerator(
            results_dir=results_dir, 
            json_file=json_file, 
            pickle_file=pickle_file
        )
        
        # レポート作成
        generator.create_text_report()
        generator.create_summary_stats()
        
        print("\n✅ レポート作成完了！")
        if generator.report_dir:
            print(f"📁 レポートは以下に保存されました: {generator.report_dir}")
        
        return generator
        
    except Exception as e:
        print(f"❌ レポート作成エラー: {e}")
        print("📝 基本情報のみ表示します:")
        
        # 最低限の情報表示
        if results_dir and os.path.exists(results_dir):
            files = os.listdir(results_dir)
            print(f"📁 結果ディレクトリ: {results_dir}")
            print(f"📄 ファイル数: {len(files)}")
            print(f"📄 ファイル: {files[:10]}{'...' if len(files) > 10 else ''}")
        
        return None

# メイン実行部分
if __name__ == "__main__":
    print("="*80)
    print("軽量レポート生成ツール")
    print("Report Generator for Experiment Results (No matplotlib required)")
    print("="*80)
    
    print("\n📝 使用方法:")
    print("1. visualize_omar_results(results_dir='path/to/results')")
    print("2. visualize_omar_results(json_file='path/to/file.json')")
    
    print("\n💡 使用例:")
    print("   sage: generator = visualize_omar_results(results_dir='./debug_results_20240101_120000')")
    print("   sage: generator = visualize_omar_results(json_file='results.json')")
    
    print("\n📊 作成されるレポート:")
    print("   - テキスト形式の詳細レポート")
    print("   - 統計サマリー")
    print("   - フロベニウス分布分析")
    print("   - ケース別成功率")
    
    print("\n" + "="*80)
    print("🎯 準備完了 - matplotlib依存なしで動作します")
    print("="*80)
