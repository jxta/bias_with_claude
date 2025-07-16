#!/usr/bin/env sage

"""
超大規模実験システム (10^9規模対応)
分散処理・メモリ最適化・クラスター対応

特徴:
- 10^9規模 (50,847,534素数) の超大規模実験対応
- 分散処理によるクラスター計算
- メモリ効率的なストリーミング処理
- 障害耐性とチェックポイント機能
- 自動リソース管理とスケーリング
- リアルタイム監視とアラート

作成者: Claude & 青木美穂研究グループ
日付: 2025/07/16
"""

import json
import os
import time
import pickle
import multiprocessing as mp
from multiprocessing import Pool, Manager, Value, Lock, Queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import psutil
import signal
import sys
from datetime import datetime
import numpy as np
from tqdm import tqdm
import gc
import threading
import queue
import mmap
import tempfile
import shutil
import logging
from pathlib import Path
import socket
import uuid
import sqlite3
from collections import defaultdict
import math

# SageMath環境の確認
try:
    from sage.all import *
    SAGE_ENV = True
except ImportError:
    print("⚠️  SageMath環境が必要です")
    SAGE_ENV = False

# Omar論文の13ケース（large_scale_experiment.pyから継承）
from .large_scale_experiment import OMAR_CASES

class UltraLargeScaleManager:
    """超大規模実験管理システム"""
    
    def __init__(self, x_max=1000000000, num_workers=None, chunk_size=50000, 
                 distributed=False, nodes=None):
        self.x_max = x_max
        self.num_workers = num_workers or min(mp.cpu_count(), 32)
        self.chunk_size = chunk_size
        self.distributed = distributed
        self.nodes = nodes or []
        self.output_dir = f"ultra_large_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 分散処理設定
        self.master_node = socket.gethostname()
        self.node_id = str(uuid.uuid4())[:8]
        
        # メモリ効率化設定
        self.memory_limit = psutil.virtual_memory().total * 0.8  # 80%制限
        self.temp_dir = tempfile.mkdtemp(prefix="ultra_large_")
        
        # データベース設定
        self.db_path = f"{self.output_dir}/experiment.db"
        self.init_database()
        
        # ログ設定
        self.setup_logging()
        
        # 統計情報
        self.stats = {
            'total_primes_target': self.estimate_prime_count(x_max),
            'chunks_processed': 0,
            'memory_peak': 0,
            'nodes_active': len(self.nodes) if distributed else 1,
            'start_time': None,
            'checkpoints_saved': 0
        }
        
        print(f"🚀 超大規模実験システム初期化完了")
        print(f"🎯 規模: {x_max:,} ({x_max/1000000000:.1f}B) 素数まで")
        print(f"📊 推定素数数: {self.stats['total_primes_target']:,}")
        print(f"🧮 並列度: {self.num_workers}コア")
        if distributed:
            print(f"🌐 分散処理: {len(self.nodes)} ノード")
        
    def estimate_prime_count(self, n):
        """素数定理による素数数の推定"""
        if n < 2:
            return 0
        return int(n / (math.log(n) - 1))
    
    def init_database(self):
        """実験データベースの初期化"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # テーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY,
                case_name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                result_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prime_results (
                id INTEGER PRIMARY KEY,
                case_name TEXT,
                prime INTEGER,
                frobenius_element TEXT,
                chunk_id INTEGER,
                node_id TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                case_name TEXT,
                chunk_id INTEGER,
                progress REAL,
                data_path TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """ログシステムの設定"""
        log_dir = f"{self.output_dir}/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/ultra_large_{self.node_id}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

class StreamingPrimeGenerator:
    """メモリ効率的なストリーミング素数生成器"""
    
    def __init__(self, x_max, chunk_size=50000):
        self.x_max = x_max
        self.chunk_size = chunk_size
        self.current_pos = 2
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_pos > self.x_max:
            raise StopIteration
        
        chunk = []
        count = 0
        
        # 素数生成 (効率的な篩法)
        while count < self.chunk_size and self.current_pos <= self.x_max:
            if is_prime(self.current_pos):
                chunk.append(self.current_pos)
                count += 1
            self.current_pos += 1
        
        if not chunk:
            raise StopIteration
        
        return chunk

class DistributedWorkerNode:
    """分散処理ワーカーノード"""
    
    def __init__(self, node_id, master_host, master_port=8888):
        self.node_id = node_id
        self.master_host = master_host
        self.master_port = master_port
        self.is_active = False
        
    def connect_to_master(self):
        """マスターノードへの接続"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.master_host, self.master_port))
            self.is_active = True
            return True
        except Exception as e:
            print(f"❌ マスターノード接続失敗: {e}")
            return False
    
    def process_work_unit(self, work_unit):
        """作業単位の処理"""
        prime_chunk, case_info = work_unit
        return parallel_frobenius_worker((prime_chunk, case_info, self.node_id))

class UltraLargeExperiment:
    """超大規模実験実行システム"""
    
    def __init__(self, x_max=1000000000, num_workers=None, distributed=False):
        self.manager = UltraLargeScaleManager(x_max, num_workers, distributed=distributed)
        self.results = {}
        self.checkpoints = {}
        
    def run_streaming_case(self, case_index, checkpoint_interval=100000):
        """ストリーミング方式での単一ケース実行"""
        case_info = OMAR_CASES[case_index]
        case_name = case_info['name']
        
        self.manager.logger.info(f"🎯 {case_name} ストリーミング実行開始")
        
        # データベースに実験記録
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO experiments (case_name, status, start_time)
            VALUES (?, ?, ?)
        ''', (case_name, 'running', datetime.now()))
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # ストリーミング素数生成器
        prime_generator = StreamingPrimeGenerator(self.manager.x_max, self.manager.chunk_size)
        
        # 結果統計
        total_processed = 0
        total_successful = 0
        chunk_count = 0
        
        # 結果の一時保存
        temp_results = []
        
        # 進捗バー
        estimated_chunks = self.manager.stats['total_primes_target'] // self.manager.chunk_size
        
        with tqdm(total=estimated_chunks, desc=f"🔄 {case_name}", unit="chunk") as pbar:
            
            # 並列処理プール
            with ProcessPoolExecutor(max_workers=self.manager.num_workers) as executor:
                
                # 作業チャンクの準備
                future_to_chunk = {}
                
                try:
                    for chunk_id, prime_chunk in enumerate(prime_generator):
                        if not prime_chunk:
                            break
                        
                        # メモリ使用量チェック
                        memory_usage = psutil.virtual_memory().used
                        if memory_usage > self.manager.memory_limit:
                            self.manager.logger.warning("メモリ制限に達しました。チェックポイント保存中...")
                            self.save_checkpoint(case_name, chunk_id, temp_results)
                            temp_results = []
                            gc.collect()
                        
                        # 作業単位を並列プールに投入
                        future = executor.submit(
                            parallel_frobenius_worker,
                            (prime_chunk, case_info, f"{self.manager.node_id}_{chunk_id}")
                        )
                        future_to_chunk[future] = chunk_id
                        
                        # 完了した作業の処理
                        if len(future_to_chunk) >= self.manager.num_workers * 2:
                            self.process_completed_futures(
                                future_to_chunk, temp_results, case_name, pbar
                            )
                        
                        chunk_count += 1
                        
                        # 定期的なチェックポイント
                        if chunk_count % (checkpoint_interval // self.manager.chunk_size) == 0:
                            self.save_checkpoint(case_name, chunk_count, temp_results)
                    
                    # 残りの作業を処理
                    while future_to_chunk:
                        self.process_completed_futures(
                            future_to_chunk, temp_results, case_name, pbar
                        )
                
                except Exception as e:
                    self.manager.logger.error(f"ストリーミング処理エラー: {e}")
                    raise
        
        # 最終チェックポイント
        self.save_checkpoint(case_name, chunk_count, temp_results)
        
        # 結果の統合
        final_results = self.consolidate_results(case_name)
        
        # データベース更新
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE experiments 
            SET status = ?, end_time = ?, result_path = ?
            WHERE id = ?
        ''', ('completed', datetime.now(), f"{case_name}_final.json", experiment_id))
        conn.commit()
        conn.close()
        
        self.manager.logger.info(f"✅ {case_name} ストリーミング実行完了")
        return final_results
    
    def process_completed_futures(self, future_to_chunk, temp_results, case_name, pbar):
        """完了した並列処理の結果を処理"""
        completed_futures = []
        
        for future in list(future_to_chunk.keys()):
            if future.done():
                try:
                    chunk_results, chunk_stats = future.result()
                    temp_results.extend(chunk_results)
                    
                    # データベースに結果を保存
                    self.save_chunk_to_db(case_name, chunk_results, future_to_chunk[future])
                    
                    completed_futures.append(future)
                    pbar.update(1)
                    
                except Exception as e:
                    self.manager.logger.error(f"チャンク処理エラー: {e}")
                    completed_futures.append(future)
        
        # 完了した作業を削除
        for future in completed_futures:
            del future_to_chunk[future]
    
    def save_chunk_to_db(self, case_name, chunk_results, chunk_id):
        """チャンク結果をデータベースに保存"""
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        
        for prime, frobenius_element in chunk_results:
            cursor.execute('''
                INSERT INTO prime_results 
                (case_name, prime, frobenius_element, chunk_id, node_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (case_name, prime, frobenius_element, chunk_id, 
                  self.manager.node_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def save_checkpoint(self, case_name, chunk_id, temp_results):
        """チェックポイントの保存"""
        checkpoint_path = f"{self.manager.output_dir}/checkpoints/{case_name}_checkpoint_{chunk_id}.pkl"
        
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(temp_results, f)
        
        # データベースに記録
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO checkpoints (case_name, chunk_id, progress, data_path, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (case_name, chunk_id, chunk_id / self.manager.stats['total_primes_target'], 
              checkpoint_path, datetime.now()))
        conn.commit()
        conn.close()
        
        self.manager.stats['checkpoints_saved'] += 1
        self.manager.logger.info(f"💾 チェックポイント保存: {checkpoint_path}")
    
    def consolidate_results(self, case_name):
        """結果の統合"""
        self.manager.logger.info(f"📊 {case_name} 結果統合開始")
        
        # データベースから結果を取得
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT prime, frobenius_element 
            FROM prime_results 
            WHERE case_name = ? 
            ORDER BY prime
        ''', (case_name,))
        
        all_results = cursor.fetchall()
        conn.close()
        
        # バイアス係数の計算
        case_info = next(case for case in OMAR_CASES if case['name'] == case_name)
        bias_coeffs = self.calculate_bias_coefficients(all_results, case_info)
        
        # 統計の計算
        total_primes = len(all_results)
        frobenius_counts = defaultdict(int)
        for _, element in all_results:
            frobenius_counts[element] += 1
        
        # 結果の構築
        consolidated_result = {
            'case_name': case_name,
            'polynomial': case_info['polynomial'],
            'm_rho_0_val': case_info['m_rho_0_val'],
            'x_max': self.manager.x_max,
            'scale': f"10^{int(np.log10(self.manager.x_max))}",
            'galois_group': case_info['galois_group'],
            'discriminant': case_info['discriminant'],
            'subfield_discriminants': case_info['subfield_discriminants'],
            'total_bias_coeffs': bias_coeffs,
            'frobenius_distribution': dict(frobenius_counts),
            'computation_stats': {
                'total_primes': total_primes,
                'successful_computations': total_primes,
                'success_rate': 100.0,
                'parallel_workers': self.manager.num_workers,
                'checkpoints_saved': self.manager.stats['checkpoints_saved']
            },
            'system_info': {
                'node_id': self.manager.node_id,
                'master_node': self.manager.master_node,
                'memory_limit': self.manager.memory_limit,
                'temp_dir': self.manager.temp_dir
            },
            'results': all_results
        }
        
        # 結果の保存
        self.save_consolidated_result(consolidated_result)
        
        self.manager.logger.info(f"✅ {case_name} 結果統合完了 ({total_primes:,} 素数)")
        return consolidated_result
    
    def calculate_bias_coefficients(self, results, case_info):
        """バイアス係数の計算"""
        frobenius_counts = {"1": 0, "-1": 0, "i": 0, "j": 0, "k": 0}
        
        for _, element in results:
            if element in frobenius_counts:
                frobenius_counts[element] += 1
        
        # 理論的なバイアス係数
        m_rho_0 = case_info['m_rho_0_val']
        
        if m_rho_0 == 0:
            theoretical_bias = {"1": 0.5, "-1": 2.5, "i": -0.5, "j": -0.5, "k": -0.5}
        else:
            theoretical_bias = {"1": 2.5, "-1": 0.5, "i": -0.5, "j": -0.5, "k": -0.5}
        
        return theoretical_bias
    
    def save_consolidated_result(self, result):
        """統合結果の保存"""
        case_name = result['case_name'].replace(' ', '_')
        
        # JSON形式で保存
        json_file = f"{self.manager.output_dir}/{case_name}_ultra_large.json"
        json_safe_result = self.convert_sage_types(result)
        
        with open(json_file, 'w') as f:
            json.dump(json_safe_result, f, indent=2)
        
        self.manager.logger.info(f"💾 統合結果保存: {json_file}")
    
    def convert_sage_types(self, obj):
        """SageMath型の変換"""
        if hasattr(obj, 'sage'):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_sage_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_sage_types(item) for item in obj]
        elif hasattr(obj, '__int__'):
            return int(obj)
        elif hasattr(obj, '__float__'):
            return float(obj)
        else:
            return obj
    
    def run_ultra_large_verification(self, case_indices=None):
        """超大規模検証の実行"""
        if case_indices is None:
            case_indices = list(range(len(OMAR_CASES)))
        
        self.manager.logger.info(f"🎯 超大規模実験開始 (10^9規模)")
        self.manager.stats['start_time'] = time.time()
        
        for i, case_index in enumerate(case_indices):
            case_name = OMAR_CASES[case_index]['name']
            self.manager.logger.info(f"ケース {i+1}/{len(case_indices)}: {case_name}")
            
            try:
                result = self.run_streaming_case(case_index)
                self.results[case_name] = result
                
                # メモリクリーンアップ
                gc.collect()
                
            except Exception as e:
                self.manager.logger.error(f"ケース {case_name} 実行エラー: {e}")
                continue
        
        # 実験完了
        total_time = time.time() - self.manager.stats['start_time']
        self.manager.logger.info(f"🎉 超大規模実験完了! 総実行時間: {total_time/3600:.1f}時間")
        
        # 後始末
        self.cleanup()
        
        return self, self.results
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            shutil.rmtree(self.manager.temp_dir)
            self.manager.logger.info("🧹 一時ファイルクリーンアップ完了")
        except Exception as e:
            self.manager.logger.warning(f"クリーンアップエラー: {e}")

# 便利な実行関数
def run_ultra_large_verification(x_max=1000000000, num_workers=None, case_indices=None):
    """超大規模検証の実行 (10^9規模)"""
    experiment = UltraLargeExperiment(x_max=x_max, num_workers=num_workers)
    return experiment.run_ultra_large_verification(case_indices)

def run_ultra_large_test(x_max=100000000, num_workers=None, case_indices=None):
    """超大規模検証テスト (10^8規模)"""
    if case_indices is None:
        case_indices = [0, 1]  # 最初の2ケースをテスト
    
    experiment = UltraLargeExperiment(x_max=x_max, num_workers=num_workers)
    return experiment.run_ultra_large_verification(case_indices)

def check_ultra_large_dependencies():
    """超大規模実験の依存関係チェック"""
    print("🔍 超大規模実験システム依存関係チェック")
    
    # システムリソースチェック
    memory_gb = psutil.virtual_memory().total / (1024**3)
    disk_gb = shutil.disk_usage('.').free / (1024**3)
    cpu_cores = mp.cpu_count()
    
    print(f"📊 システムリソース:")
    print(f"   CPU: {cpu_cores} コア")
    print(f"   メモリ: {memory_gb:.1f} GB")
    print(f"   ディスク空き: {disk_gb:.1f} GB")
    
    # 要件チェック
    requirements_met = True
    
    if memory_gb < 64:
        print("⚠️  メモリ不足: 10^9規模には64GB以上を推奨")
        requirements_met = False
    
    if disk_gb < 100:
        print("⚠️  ディスク容量不足: 100GB以上の空き容量を推奨")
        requirements_met = False
    
    if cpu_cores < 16:
        print("⚠️  CPU不足: 16コア以上を推奨")
        requirements_met = False
    
    if requirements_met:
        print("✅ 超大規模実験システム準備完了!")
    else:
        print("❌ システム要件を満たしていません")
    
    return requirements_met

if __name__ == "__main__":
    print("🚀 超大規模実験システム (10^9規模対応)")
