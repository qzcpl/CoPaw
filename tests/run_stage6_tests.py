#!/usr/bin/env python
"""
阶段 6 测试运行脚本

用法：
    python run_stage6_tests.py              # 运行所有测试
    python run_stage6_tests.py --unit       # 只运行单元测试
    python run_stage6_tests.py --integration # 只运行集成测试
    python run_stage6_tests.py --performance # 只运行性能测试
    python run_stage6_tests.py --verbose    # 详细输出
"""

import sys
import os
import argparse
from pathlib import Path

# 添加补丁目录到路径
patch_src = Path(__file__).parent / "src"
sys.path.insert(0, str(patch_src))


def run_tests(test_type="all", verbose=False):
    """运行测试"""
    
    # 构建 pytest 命令
    cmd_parts = ["pytest"]
    
    # 添加测试路径
    test_dir = Path(__file__).parent / "tests"
    
    if test_type == "unit":
        cmd_parts.append(str(test_dir / "unit"))
    elif test_type == "integration":
        cmd_parts.append(str(test_dir / "integration"))
    elif test_type == "performance":
        cmd_parts.append(str(test_dir / "performance"))
    else:  # all
        cmd_parts.append(str(test_dir))
    
    # 添加详细输出选项
    if verbose:
        cmd_parts.append("-v")
        cmd_parts.append("-s")
    
    # 添加覆盖率选项
    if test_type == "all":
        cmd_parts.append("--cov=src/copaw")
        cmd_parts.append("--cov-report=term-missing")
    
    # 添加 junit 输出
    cmd_parts.append(f"--junitxml={Path(__file__).parent / 'test-results.xml'}")
    
    # 执行测试
    cmd_str = " ".join(cmd_parts)
    print(f"\n{'='*60}")
    print(f"运行测试：{cmd_str}")
    print(f"{'='*60}\n")
    
    exit_code = os.system(cmd_str)
    
    # 输出结果
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✅ 测试全部通过！")
    else:
        print(f"❌ 测试失败，退出码：{exit_code}")
    print(f"{'='*60}\n")
    
    return exit_code


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行阶段 6 测试")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 确定测试类型
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.performance:
        test_type = "performance"
    else:
        test_type = "all"
    
    # 运行测试
    exit_code = run_tests(test_type, args.verbose)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
