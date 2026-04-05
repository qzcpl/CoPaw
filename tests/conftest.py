"""
pytest 配置

设置测试路径和导入
"""

import sys
from pathlib import Path

# 添加补丁 src 目录到 Python 路径
patch_src = Path(__file__).parent / "src"
sys.path.insert(0, str(patch_src))
