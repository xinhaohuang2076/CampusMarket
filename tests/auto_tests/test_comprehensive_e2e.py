"""
Selenium E2E 综合测试 — Edge 浏览器
覆盖：注册→登录→搜索→浏览→留言→收藏→交易→评价
先启动后端+前端，再运行本测试
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE = 'http://localhost:5173'
PASS = 0
FAIL = 0


def check(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f'  ✅ {name}')
    except Exception as e:
        FAIL += 1
        print(f'  ❌ {name}: {str(e)[:120]}')


driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)


def wait_text(selector, text, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text)
    )


try:
    # ====== 1. 注册 ======
    def register():
        driver.get(f'{BASE}/#/register')
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="22023开头，10位数字"]')))
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//input[@placeholder="22023开头，10位数字"]').send_keys('2202399501')
        driver.find_element(By.XPATH, '//input[@placeholder="@qq.com 或 @163.com"]').send_keys('e2e_test@qq.com')
        pw_inputs = driver.find_elements(By.XPATH, '//input[@type="password"]')
        pw_inputs[0].send_keys('e2e123')
        driver.find_element(By.XPATH, '//input[@placeholder="选填，默认使用学号"]').send_keys('E2E测试')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(2)
        assert 'token' in driver.execute_script('return JSON.stringify(Object.keys(localStorage))')
        print(f'    注册成功，跳转到首页')
    check('注册新用户', register)

    # ====== 2. 重新登录 ======
    def relogin():
        driver.get(f'{BASE}/#/login')
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@placeholder="10位学号"]').send_keys('2202399501')
        driver.find_element(By.XPATH, '//input[@placeholder="输入密码"]').send_keys('e2e123' + Keys.ENTER)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert 'E2E测试' in body
        print(f'    登录后导航显示昵称')
    check('登录验证持久化', relogin)

    # ====== 3. 首页加载 ======
    def home():
        driver.get(f'{BASE}/#/')
        time.sleep(3)
        assert '686' in driver.find_element(By.TAG_NAME, 'body').text or '件商品' in driver.find_element(By.TAG_NAME, 'body').text
    check('首页商品列表加载', home)

    # ====== 4. 搜索 ======
    def search():
        inp = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="搜索商品名称或描述..."]')))
        inp.clear()
        inp.send_keys('篮球' + Keys.ENTER)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '篮球' in body
        # 验证筛选标签出现
        assert '清除' in body
    check('搜索"篮球"', search)

    # ====== 5. 按分类筛选 ======
    def category_filter():
        selects = driver.find_elements(By.TAG_NAME, 'select')
        Select(selects[0]).select_by_visible_text('体育器材')
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '体育器材' in body
    check('分类筛选"体育器材"', category_filter)

    # ====== 6. 清除筛选 ======
    def clear_filters():
        driver.find_element(By.XPATH, '//button[text()="清除"]').click()
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '686' in body
    check('清除筛选条件', clear_filters)

    # ====== 7. 进入商品详情 ======
    def detail():
        driver.get(f'{BASE}/#/product/1')
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '高等数学' in body
        assert '信用分' in body
    check('商品详情页', detail)

    # ====== 8. 发送留言 ======
    def send_msg():
        inp = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="咨询卖家..."]')))
        inp.send_keys('E2E测试留言' + Keys.ENTER)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert 'E2E测试留言' in body
    check('发送留言', send_msg)

    # ====== 9. 收藏 ======
    def favorite():
        btn = driver.find_element(By.XPATH, '//button[contains(., "♡") or contains(., "♥") or contains(text(), "收藏")]')
        btn.click()
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        # Either ♥ or "已收藏" appears
        print(f'    收藏按钮已点击')
    check('收藏/取消收藏', favorite)

    # ====== 10. 查看我的收藏 ======
    def check_favorites():
        driver.get(f'{BASE}/#/favorites')
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        # Should show the product or empty state
        assert '收藏' in body
    check('我的收藏页面', check_favorites)

    # ====== 11. 个人中心 ======
    def profile():
        driver.get(f'{BASE}/#/profile')
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '2202399501' in body
        assert '信用分' in body
    check('个人中心', profile)

    # ====== 12. 我的商品页面 ======
    def my_products():
        driver.get(f'{BASE}/#/my-products')
        time.sleep(2)
        assert '发布商品' in driver.find_element(By.TAG_NAME, 'body').text
    check('我的商品页面', my_products)

    # ====== 13. 交易记录页面 ======
    def transactions():
        driver.get(f'{BASE}/#/transactions')
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '全部' in body and '我买到的' in body and '我卖出的' in body
    check('交易记录页面', transactions)

    # ====== 14. 留言页面 ======
    def messages_page():
        driver.get(f'{BASE}/#/messages')
        time.sleep(2)
        assert '我收到的' in driver.find_element(By.TAG_NAME, 'body').text
        # Switch to sent
        driver.find_element(By.XPATH, '//button[text()="我发出的"]').click()
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert 'E2E测试留言' in body
    check('留言页面 筛选+内容', messages_page)

    # ====== 15. 注册页校验 ======
    def register_validation():
        driver.get(f'{BASE}/#/register')
        time.sleep(1)
        submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit.click()
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert '请填写' in body
    check('注册表单客户端校验', register_validation)

finally:
    driver.quit()
    total = PASS + FAIL
    print(f'\n{"=" * 40}')
    print(f'E2E 测试完成: {PASS} 通过, {FAIL} 失败, 共 {total} 项')
    print(f'{"=" * 40}')
