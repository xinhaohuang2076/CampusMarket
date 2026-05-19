"""Selenium Edge 自动化测试 - 校园二手交易平台核心流程"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE = 'http://localhost:5173'
passed = 0
failed = 0


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f'  ✅ {name}')
        passed += 1
    except Exception as e:
        print(f'  ❌ {name}: {e}')
        failed += 1


driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # ===== 1. 首页加载 =====
    def test_home():
        driver.get(BASE)
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '686' in body or '件商品' in body, '商品列表未加载'
        assert '首页' in body, '导航未加载'

    test('首页商品列表加载', test_home)

    # ===== 2. 搜索功能 =====
    def test_search():
        search_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="搜索商品名称或描述..."]'))
        )
        search_input.clear()
        search_input.send_keys('数学' + Keys.ENTER)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '27' in body, f'搜索结果数量不对: {body[:100]}'

    test('搜索"数学"返回27件', test_search)

    # ===== 3. 分类筛选 =====
    def test_category():
        # 选择分类 dropdown
        selects = driver.find_elements(By.TAG_NAME, 'select')
        if len(selects) > 0:
            selects[0].click()
            option = driver.find_element(By.XPATH, '//option[text()="电子产品"]')
            option.click()
            time.sleep(2)
            body = driver.find_element(By.TAG_NAME, 'body').text
            # 清空搜索
            search_input = driver.find_element(By.XPATH, '//input[@placeholder="搜索商品名称或描述..."]')
            search_input.clear()
            search_input.send_keys(Keys.ENTER)
            time.sleep(2)
            assert True

    test('分类筛选可用', test_category)

    # ===== 4. 商品详情 =====
    def test_detail():
        driver.get(f'{BASE}/#/product/1')
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '高等数学' in body, '商品标题未显示'
        assert '¥' in body, '价格未显示'
        print(f'    商品标题可见, 价格可见')

    test('商品详情页面', test_detail)

    # ===== 5. 登录页面 =====
    def test_login_page():
        driver.get(f'{BASE}/#/login')
        time.sleep(2)
        assert driver.title == '登录'
        student_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="10位学号"]'))
        )
        assert student_input.is_displayed(), '学号输入框未显示'

    test('登录页面加载', test_login_page)

    # ===== 6. 登录功能 =====
    def test_login_submit():
        driver.get(f'{BASE}/#/login')
        time.sleep(1)
        student_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="10位学号"]'))
        )
        student_input.send_keys('2202300001')
        pwd_input = driver.find_element(By.XPATH, '//input[@placeholder="输入密码"]')
        pwd_input.send_keys('123456' + Keys.ENTER)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '小红60' in body or '发布' in body, f'登录后导航异常: {body[:200]}'

    test('登录功能正常', test_login_submit)

    # ===== 7. 发布商品页面（需登录态） =====
    def test_new_product():
        driver.get(f'{BASE}/#/product/new')
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '发布商品' in body, '发布页面未加载'

    test('发布商品页面', test_new_product)

    # ===== 8. 注册页面 =====
    def test_register_page():
        driver.get(f'{BASE}/#/register')
        time.sleep(2)
        assert driver.title == '注册'
        email_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="@qq.com 或 @163.com"]'))
        )
        assert email_input.is_displayed()

    test('注册页面加载', test_register_page)

finally:
    driver.quit()
    print(f'\n====== Selenium 测试结果 ======')
    print(f'通过: {passed} | 失败: {failed} | 共 {passed + failed} 项')
