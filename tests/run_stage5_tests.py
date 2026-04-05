"""
运行阶段 5 测试
"""

import sys
from pathlib import Path

# 添加补丁目录到路径
patch_src = Path(__file__).parent / "src"
sys.path.insert(0, str(patch_src))

# 运行 pytest
import pytest

if __name__ == "__main__":
    # 运行队列测试
    print("=" * 60)
    print("Running Queue Tests...")
    print("=" * 60)
    
    exit_code = pytest.main([
        "tests/queue/test_queue.py",
        "-v",
        "--tb=short",
    ])
    
    print("\n" + "=" * 60)
    print("Running Monitor Tests...")
    print("=" * 60)
    
    exit_code2 = pytest.main([
        "tests/monitor/test_monitor.py",
        "-v",
        "--tb=short",
    ])
    
    sys.exit(max(exit_code, exit_code2))
