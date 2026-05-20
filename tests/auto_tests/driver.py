"""Selenium Edge 驱动共用模块"""
import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE = os.getenv('E2E_BASE', 'http://localhost:5173')
WAIT_TIMEOUT = 15


class E2ETest:
    """E2E 测试基类，封装浏览器管理和报告"""

    def __init__(self, name: str):
        self.name = name
        self.driver = None
        self.wait = None
        self.passed = 0
        self.failed = 0

    def setup(self):
        self.driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def teardown(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

    def check(self, name: str, fn, retries=2):
        for attempt in range(retries + 1):
            try:
                fn()
                self.passed += 1
                print(f'  ✅ {name}')
                return
            except Exception as e:
                if attempt < retries:
                    time.sleep(2)
                    continue
                self.failed += 1
                try:
                    os.makedirs('logs', exist_ok=True)
                    safe = name.replace('/', '_')
                    self.driver.save_screenshot(f'logs/e2e_fail_{safe}.png')
                except Exception:
                    pass
                print(f'  ❌ {name}: {str(e)[:150]}')

    def run(self, tests: list):
        """运行测试项列表 [(name, fn), ...]"""
        print(f'\n{"=" * 50}')
        print(f'  {self.name}')
        print(f'{"=" * 50}')
        try:
            self.setup()
            for name, fn in tests:
                self.check(name, fn)
        finally:
            self.teardown()
            total = self.passed + self.failed
            print(f'\n  ✅ 通过: {self.passed} | ❌ 失败: {self.failed} | 共 {total} 项')
            return self.failed == 0
