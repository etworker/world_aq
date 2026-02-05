#!/usr/bin/env python
"""
监控实验进度
"""

import json
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/etworker/Documents/code/others/world_aq")
EXPERIMENTS_DIR = PROJECT_ROOT / "models/experiments"

def get_latest_experiment():
    """获取最新的实验目录"""
    experiments = sorted(EXPERIMENTS_DIR.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
    return experiments[0] if experiments else None

def monitor_experiment():
    """监控实验进度"""
    exp_dir = get_latest_experiment()
    if not exp_dir:
        print("没有找到实验目录")
        return
    
    print(f"监控实验: {exp_dir.name}")
    print("=" * 60)
    
    manifest_path = exp_dir / "manifest.json"
    
    while True:
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                results = manifest.get('results', [])
                total = manifest.get('total_experiments', 0)
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 实验进度: {len(results)}/{total}")
                
                if len(results) > 0:
                    # 显示最新的实验结果
                    latest = results[-1]
                    print(f"最新实验: {latest['mode']} - {latest['algorithm']}")
                    print(f"验证RMSE: {latest['val_metrics'].get('rmse', 'N/A'):.4f}")
                
                if len(results) >= total:
                    print("\n✅ 实验完成！")
                    break
                    
            except Exception as e:
                print(f"读取manifest失败: {e}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 等待实验开始...")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_experiment()