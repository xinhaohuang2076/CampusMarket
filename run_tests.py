#!/usr/bin/env python3
"""
CampusMarket 全量测试运行器
用法:
  python run_tests.py              # 运行全部测试
  python run_tests.py --unit       # 仅单元测试
  python run_tests.py --api        # 仅 API 测试
  python run_tests.py --e2e        # 仅 E2E 测试
  python run_tests.py --all        # 运行全部
"""
import sys
import os
import subprocess
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(ROOT, '.venv', 'Scripts', 'python.exe')
VENV_PYTEST = [VENV_PYTHON, '-m', 'pytest']

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'


def banner(text):
    print(f'\n{CYAN}{"=" * 50}')
    print(f'  {text}')
    print(f'{"=" * 50}{RESET}\n')


def run_test(label, cmd, cwd=ROOT, timeout=300):
    print(f'{YELLOW}[运行] {label}{RESET}')
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f'{GREEN}[通过] {label}{RESET}')
        else:
            print(f'{RED}[失败] {label} (exit={result.returncode}){RESET}')
        # Show summary lines
        for line in result.stdout.split('\n'):
            if any(kw in line for kw in ['passed', 'failed', 'error', 'PASSED', 'FAILED', 'ERROR']):
                print(f'  {line.strip()}')
        if result.stderr.strip():
            for line in result.stderr.split('\n')[-3:]:
                if line.strip():
                    print(f'  {RED}{line.strip()}{RESET}')
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f'{RED}[超时] {label}{RESET}')
        return -1
    except FileNotFoundError as e:
        print(f'{RED}[错误] 找不到命令: {e}{RESET}')
        return -1


def main():
    parser = argparse.ArgumentParser(description='CampusMarket 全量测试运行器')
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--api', action='store_true', help='运行 API 测试（需后端运行）')
    parser.add_argument('--e2e', action='store_true', help='运行 E2E 测试（需前后端运行）')
    parser.add_argument('--all', action='store_true', help='运行全部测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    args = parser.parse_args()

    # 默认运行全部
    run_all = args.all or not (args.unit or args.api or args.e2e)

    exit_code = 0

    # ---- 单元测试 ----
    if run_all or args.unit or args.coverage:
        banner('单元测试 (Unit Tests)')
        cmd = VENV_PYTEST + ['tests/unit_tests/', '-v']
        if args.coverage or run_all:
            cmd += ['--cov=project/backend', '--cov-report=term', '--cov-report=html']
        rc = run_test('单元测试', cmd)
        exit_code += rc

    # ---- API 测试 ----
    if run_all or args.api:
        banner('API 测试 (API Tests)')
        rc = run_test('API 测试', VENV_PYTEST + ['tests/api_tests/', '-v'], timeout=180)
        exit_code += rc

    # ---- E2E 测试 ----
    if run_all or args.e2e:
        banner('E2E 测试 (Selenium + Edge)')
        rc = run_test('E2E 测试', VENV_PYTEST + ['tests/auto_tests/test_comprehensive_e2e.py', '-v'], timeout=180)
        exit_code += rc

    # ---- 总览 ----
    print(f'\n{CYAN}{"=" * 50}')
    if exit_code == 0:
        print(f'  {GREEN}所有测试通过！{RESET}')
    else:
        print(f'  {RED}部分测试失败 (exit code: {exit_code}){RESET}')
    print(f'{CYAN}{"=" * 50}{RESET}\n')

    if args.coverage or run_all:
        cov_dir = os.path.join(ROOT, 'htmlcov')
        if os.path.isdir(cov_dir):
            print(f'覆盖率报告: file://{os.path.join(cov_dir, "index.html")}')

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
