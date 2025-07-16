#!/usr/bin/env sage

"""
軽量可視化ツール (正確なフロベニウス元計算対応版)
新しいデータ形式に対応したレポート作成

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
"""

import json
import os
import pickle
from datetime import datetime
from collections import Counter

class EnhancedReportGenerator:
    """強化されたレポート生成クラス"""
    
    def __init__(self, results_dir=None, json_file=None, pickle_file=None):
        """
        初期化
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
        
        # ディレクトリ内容の詳細確認
        print(f"📂 ディレクトリ内容の詳細分析:")
        files = os.listdir(results_dir)
        print(f"  ファイル数: {len(files)}")
        
        for file in files:
            filepath = os.path.join(results_dir, file)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  📄 {file}: {file_size} bytes")
                
                # ファイルの種類別処理
                if file.endswith('.json'):
                    self.load_from_json(filepath)
                elif file.endswith('.pkl'):
                    self.load_from_pickle(filepath)
                elif file.endswith('.txt'):
                    print(f"    テキストファイル（スキップ）")
        
        # データが見つからない場合のデバッグ情報作成
        if not self.results:
            print("❌ データが見つかりません。デバッグ情報を作成します。")
            self.create_debug_info(results_dir)
    
    def load_from_json(self, json_file):
        """JSONファイルから読み込み"""
        try:
            print(f"📄 JSON読み込み試行: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # データ構造の分析
            print(f"  📊 データ構造分析:")
            print(f"    トップレベルキー: {list(data.keys()) if isinstance(data, dict) else 'リスト形式'}")
            
            # 新しいフロベニウス計算形式に対応
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        # 新しい形式（正確なフロベニウス計算）の検出
                        if 'comparisons' in value and 'accurate_results' in value:
                            print(f"    ✅ 正確なフロベニウス計算形式を検出: {key}")
                            self.results[key] = self.convert_accurate_format(value)
                        # 従来形式の検出
                        elif 'results' in value:
                            print(f"    ✅ 従来形式を検出: {key}")
                            self.results[key] = value
                        else:
                            print(f"    ⚠️  不明な形式: {key}")
                            self.results[key] = value
            
            print(f"✅ JSON読み込み成功: {len(self.results)} ケース")
            
            if not self.report_dir:
                self.report_dir = os.path.join(os.path.dirname(json_file), "reports")
                os.makedirs(self.report_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ JSON読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
    
    def convert_accurate_format(self, accurate_data):
        """正確なフロベニウス計算形式を従来形式に変換"""
        try:
            # comparisons から results 形式を作成
            results = []
            
            comparisons = accurate_data.get('comparisons', [])
            for comp in comparisons:
                prime = comp.get('prime')
                accurate_result = comp.get('accurate_result')
                if prime and accurate_result:
                    results.append([prime, accurate_result])
            
            # 従来形式に変換
            converted = {
                'polynomial': accurate_data.get('polynomial', 'Unknown'),
                'results': results,
                'successful': len(results),
                'failed': 0,
                'success_rate': 100.0 if results else 0.0,
                'test_primes': accurate_data.get('test_primes', []),
                'match_rate': accurate_data.get('match_rate', 0),
                'accurate_results': accurate_data.get('accurate_results', []),
                'simple_results': accurate_data.get('simple_results', []),
                'mismatches': accurate_data.get('mismatches', [])
            }
            
            print(f"    🔄 変換完了: {len(results)} 結果")
            return converted
            
        except Exception as e:
            print(f"    ❌ 変換エラー: {e}")
            return accurate_data
    
    def load_from_pickle(self, pickle_file):
        """Pickleファイルから読み込み"""
        try:
            print(f"📄 Pickle読み込み試行: {pickle_file}")
            with open(pickle_file, 'rb') as f:
                data = pickle.load(f)
            
            # データ構造の分析（Pickleの場合）
            print(f"  📊 Pickleデータ分析:")
            if isinstance(data, dict):
                print(f"    キー: {list(data.keys())}")
                self.results.update(data)
            else:
                print(f"    型: {type(data)}")
                self.results['pickle_data'] = data
            
            print(f"✅ Pickle読み込み成功: {len(self.results)} ケース")
            
            if not self.report_dir:
                self.report_dir = os.path.join(os.path.dirname(pickle_file), "reports")
                os.makedirs(self.report_dir, exist_ok=True)
                
        except Exception as e:
            print(f"❌ Pickle読み込みエラー: {e}")
    
    def create_debug_info(self, results_dir):
        """デバッグ情報の作成"""
        try:
            print("📝 デバッグ情報作成中...")
            
            files = os.listdir(results_dir)
            debug_info = {
                "debug_info": {
                    "directory": results_dir,
                    "files": files,
                    "file_details": {},
                    "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # 各ファイルの詳細情報
            for file in files:
                filepath = os.path.join(results_dir, file)
                if os.path.isfile(filepath):
                    try:
                        file_size = os.path.getsize(filepath)
                        debug_info["debug_info"]["file_details"][file] = {
                            "size": file_size,
                            "type": file.split('.')[-1] if '.' in file else "unknown"
                        }
                        
                        # ファイル内容の一部を読み取り試行
                        if file.endswith('.txt'):
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read(200)  # 最初の200文字
                                debug_info["debug_info"]["file_details"][file]["preview"] = content
                    except Exception as e:
                        debug_info["debug_info"]["file_details"][file] = {"error": str(e)}
            
            self.results = debug_info
            print("✅ デバッグ情報作成完了")
            
        except Exception as e:
            print(f"❌ デバッグ情報作成エラー: {e}")
    
    def analyze_results(self):
        """結果の詳細分析"""
        if not self.results:
            return {"error": "データなし"}
        
        analysis = {
            'total_cases': 0,
            'successful_cases': 0,
            'total_computations': 0,
            'successful_computations': 0,
            'frobenius_distribution': Counter(),
            'case_statistics': {},
            'data_format_info': {},
            'debug_info': {}
        }
        
        for case_name, result in self.results.items():
            analysis['total_cases'] += 1
            
            # デバッグ情報の場合
            if case_name == "debug_info":
                analysis['debug_info'] = result
                continue
            
            # データ形式の分析
            if isinstance(result, dict):
                analysis['data_format_info'][case_name] = {
                    'keys': list(result.keys()),
                    'has_results': 'results' in result,
                    'has_comparisons': 'comparisons' in result,
                    'has_accurate_results': 'accurate_results' in result
                }
                
                # results形式の処理
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
                    
                    analysis['case_statistics'][case_name] = {
                        'computations': case_computations,
                        'frobenius_distribution': dict(case_frobenius),
                        'success_rate': result.get('success_rate', 100.0),
                        'match_rate': result.get('match_rate', 'N/A'),
                        'mismatches': result.get('mismatches', [])
                    }
                
                # accurate_results形式の処理
                elif 'accurate_results' in result:
                    analysis['successful_cases'] += 1
                    accurate_results = result.get('accurate_results', [])
                    analysis['successful_computations'] += len(accurate_results)
                    analysis['total_computations'] += len(accurate_results)
                    
                    # accurate_resultsからフロベニウス分布を作成
                    for frobenius in accurate_results:
                        analysis['frobenius_distribution'][frobenius] += 1
                    
                    analysis['case_statistics'][case_name] = {
                        'computations': len(accurate_results),
                        'frobenius_distribution': dict(Counter(accurate_results)),
                        'success_rate': result.get('success_rate', 100.0),
                        'match_rate': result.get('match_rate', 'N/A'),
                        'mismatches': result.get('mismatches', [])
                    }
        
        return analysis
    
    def create_enhanced_text_report(self):
        """強化されたテキストレポートの作成"""
        print("📝 強化されたテキストレポート作成中...")
        
        analysis = self.analyze_results()
        
        # レポート内容
        report_lines = [
            "=" * 80,
            "強化された実験結果レポート",
            "=" * 80,
            "",
            f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "■ 実験概要",
            f"  総ケース数: {analysis.get('total_cases', 0)}",
            f"  成功ケース数: {analysis.get('successful_cases', 0)}",
            f"  総計算数: {analysis.get('total_computations', 0):,}",
            f"  成功計算数: {analysis.get('successful_computations', 0):,}",
        ]
        
        # 成功率計算
        if analysis.get('total_computations', 0) > 0:
            success_rate = analysis['successful_computations'] / analysis['total_computations'] * 100
            report_lines.append(f"  全体成功率: {success_rate:.2f}%")
        else:
            report_lines.append("  全体成功率: 計算なし")
        
        # データ形式情報
        report_lines.extend(["", "■ データ形式分析"])
        data_format_info = analysis.get('data_format_info', {})
        if data_format_info:
            for case_name, format_info in data_format_info.items():
                report_lines.append(f"  {case_name}:")
                report_lines.append(f"    キー: {format_info['keys']}")
                report_lines.append(f"    results形式: {format_info['has_results']}")
                report_lines.append(f"    comparisons形式: {format_info['has_comparisons']}")
                report_lines.append(f"    accurate_results形式: {format_info['has_accurate_results']}")
        
        # フロベニウス分布
        report_lines.extend(["", "■ フロベニウス分布（全体）"])
        frobenius_dist = analysis.get('frobenius_distribution', {})
        if frobenius_dist:
            total_frobenius = sum(frobenius_dist.values())
            for element, count in sorted(frobenius_dist.items()):
                percentage = count / total_frobenius * 100 if total_frobenius > 0 else 0
                report_lines.append(f"  {element}: {count:,} ({percentage:.1f}%)")
        else:
            report_lines.append("  データなし")
        
        # ケース別詳細
        report_lines.extend(["", "■ ケース別詳細"])
        case_stats = analysis.get('case_statistics', {})
        for case_name, stats in case_stats.items():
            report_lines.extend([
                "",
                f"◆ {case_name}",
                f"  計算数: {stats.get('computations', 0):,}",
                f"  成功率: {stats.get('success_rate', 0):.1f}%",
                f"  一致率: {stats.get('match_rate', 'N/A')}"
            ])
            
            if 'frobenius_distribution' in stats:
                report_lines.append("  フロベニウス分布:")
                for element, count in sorted(stats['frobenius_distribution'].items()):
                    total_case = stats.get('computations', 0)
                    percentage = count / total_case * 100 if total_case > 0 else 0
                    report_lines.append(f"    {element}: {count} ({percentage:.1f}%)")
            
            # 不一致情報
            mismatches = stats.get('mismatches', [])
            if mismatches:
                report_lines.append("  不一致詳細:")
                for mismatch in mismatches[:5]:  # 最初の5つのみ表示
                    report_lines.append(f"    p={mismatch['prime']}: 正確={mismatch['accurate']}, 簡易={mismatch['simple']}")
                if len(mismatches) > 5:
                    report_lines.append(f"    ... 他 {len(mismatches) - 5} 件")
        
        # デバッグ情報
        debug_info = analysis.get('debug_info', {})
        if debug_info:
            report_lines.extend(["", "■ デバッグ情報"])
            report_lines.append(f"  ディレクトリ: {debug_info.get('directory', 'N/A')}")
            files = debug_info.get('files', [])
            report_lines.append(f"  ファイル数: {len(files)}")
            
            file_details = debug_info.get('file_details', {})
            for filename, details in file_details.items():
                if isinstance(details, dict):
                    report_lines.append(f"    {filename}: {details.get('size', 'unknown')} bytes ({details.get('type', 'unknown')})")
                else:
                    report_lines.append(f"    {filename}: {details}")
        
        report_lines.extend(["", "=" * 80, "レポート終了", "=" * 80])
        
        # ファイルに保存
        if self.report_dir:
            report_file = os.path.join(self.report_dir, 'enhanced_experiment_report.txt')
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                print(f"💾 強化レポート保存: {report_file}")
            except Exception as e:
                print(f"❌ レポート保存エラー: {e}")
        
        # コンソールにも表示
        print('\n'.join(report_lines))
        
        return report_lines

# 便利な関数
def visualize_omar_results(results_dir=None, json_file=None, pickle_file=None):
    """
    保存された結果から強化されたレポートを作成
    """
    print("📝 強化された結果レポート作成を開始します...")
    
    try:
        # レポート生成ツール初期化
        generator = EnhancedReportGenerator(
            results_dir=results_dir, 
            json_file=json_file, 
            pickle_file=pickle_file
        )
        
        # レポート作成
        generator.create_enhanced_text_report()
        
        print("\n✅ 強化レポート作成完了！")
        if generator.report_dir:
            print(f"📁 レポートは以下に保存されました: {generator.report_dir}")
        
        return generator
        
    except Exception as e:
        print(f"❌ レポート作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

# メイン実行部分
if __name__ == "__main__":
    print("="*80)
    print("強化された可視化ツール")
    print("Enhanced Report Generator for Frobenius Element Calculations")
    print("="*80)
    
    print("\n📝 使用方法:")
    print("1. visualize_omar_results(results_dir='path/to/results')")
    print("2. visualize_omar_results(json_file='path/to/file.json')")
    
    print("\n💡 特徴:")
    print("   - 新旧データ形式の自動検出")
    print("   - 正確なフロベニウス計算結果の解析")
    print("   - 詳細なデバッグ情報")
    print("   - 不一致分析")
    
    print("\n" + "="*80)
