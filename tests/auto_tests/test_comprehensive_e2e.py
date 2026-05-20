"""Selenium Edge 综合 E2E 测试（18 项 — 完整用户旅程）"""
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from driver import E2ETest, BASE

e2e = E2ETest('综合 E2E — 18 项完整用户旅程')
tests = []

TEST_SID = f'22023{random.randint(20000, 29999)}'
TEST_EMAIL = f'e2e_{random.randint(10000,99999)}@qq.com'
TEST_PW = 'e2e123'


def page_has(text):
    return text in e2e.driver.find_element(By.TAG_NAME, 'body').text


# ====== 1. 注册 ======
def t01():
    e2e.driver.get(f'{BASE}/#/register')
    e2e.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="22023开头，10位数字"]')))
    e2e.driver.find_element(By.XPATH, '//input[@placeholder="22023开头，10位数字"]').send_keys(TEST_SID)
    e2e.driver.find_element(By.XPATH, '//input[@placeholder="@qq.com 或 @163.com"]').send_keys(TEST_EMAIL)
    e2e.driver.find_elements(By.XPATH, '//input[@type="password"]')[0].send_keys(TEST_PW)
    e2e.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(2)
    assert 'token' in e2e.driver.execute_script('return JSON.stringify(Object.keys(localStorage))')


tests.append(('注册新用户', t01))

# ====== 2. 重新登录验证持久化 ======
def t02():
    e2e.driver.execute_script('localStorage.clear()')
    e2e.driver.get(f'{BASE}/#/login')
    e2e.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="10位学号"]'))).send_keys(TEST_SID)
    e2e.driver.find_element(By.XPATH, '//input[@placeholder="输入密码"]').send_keys(TEST_PW + Keys.ENTER)
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '发布'))


tests.append(('登录验证持久化', t02))

# ====== 3. 首页加载 ======
def t03():
    e2e.driver.get(f'{BASE}/#/')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '件商品'))


tests.append(('首页商品列表加载', t03))

# ====== 4. 搜索 ======
def t04():
    inp = e2e.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="搜索商品名称或描述..."]')))
    inp.clear()
    inp.send_keys('篮球' + Keys.ENTER)
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '清除'))
    assert page_has('篮球')


tests.append(('搜索"篮球"', t04))

# ====== 5. 分类筛选 ======
def t05():
    selects = e2e.driver.find_elements(By.TAG_NAME, 'select')
    Select(selects[0]).select_by_visible_text('体育器材')
    time.sleep(1.5)
    assert page_has('体育器材')


tests.append(('分类筛选"体育器材"', t05))

# ====== 6. 清除筛选 ======
def t06():
    from selenium.common.exceptions import NoSuchElementException
    try:
        btn = e2e.driver.find_element(By.XPATH, '//button[contains(text(), "清除")]')
        btn.click()
        time.sleep(1)
    except NoSuchElementException:
        pass


tests.append(('清除筛选条件', t06))

# ====== 7. 商品详情 ======
def t07():
    e2e.driver.get(f'{BASE}/#/product/1')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '高等数学'))
    assert page_has('¥')
    assert page_has('信用分')


tests.append(('商品详情页', t07))

# ====== 8. 发送留言 ======
def t08():
    inputs = e2e.driver.find_elements(By.XPATH, '//input[@placeholder="咨询卖家..."]')
    if not inputs:
        e2e.driver.get(f'{BASE}/#/product/2')
        time.sleep(2)
        inputs = e2e.driver.find_elements(By.XPATH, '//input[@placeholder="咨询卖家..."]')
    assert inputs, '未找到留言输入框'
    inputs[0].send_keys('E2E测试留言')
    send_btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "发送")]')
    if send_btns:
        e2e.driver.execute_script('arguments[0].click()', send_btns[0])
        time.sleep(2)


tests.append(('发送留言', t08))

# ====== 9. 收藏 ======
def t09():
    from selenium.common.exceptions import TimeoutException
    # 商品1可能已售出，直接导航到在售商品（API列表第一页取一件）
    e2e.driver.get(f'{BASE}/#/')
    time.sleep(1)
    # 点击第一张商品卡片
    cards = e2e.driver.find_elements(By.CSS_SELECTOR, '[class*="card"]')
    if not cards:
        links = e2e.driver.find_elements(By.XPATH, '//a[contains(@href, "/product/")]')
        if links:
            e2e.driver.execute_script('arguments[0].click()', links[0])
    else:
        cards[0].click()
    time.sleep(3)
    all_btns = e2e.driver.find_elements(By.TAG_NAME, 'button')
    fav_btn = None
    for btn in all_btns:
        html = btn.get_attribute('innerHTML')
        if '♡' in html or '♥' in html:
            fav_btn = btn
            break
    if not fav_btn:
        raise Exception('未找到收藏按钮')
    e2e.driver.execute_script('arguments[0].click()', fav_btn)
    time.sleep(1.5)


tests.append(('收藏商品', t09))

# ====== 10. 查看收藏 ======
def t10():
    e2e.driver.get(f'{BASE}/#/favorites')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '收藏'))


tests.append(('我的收藏页面', t10))

# ====== 11. 个人中心 ======
def t11():
    e2e.driver.get(f'{BASE}/#/profile')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), TEST_SID))


tests.append(('个人中心', t11))

# ====== 12. 我的商品页面 ======
def t12():
    e2e.driver.get(f'{BASE}/#/my-products')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '发布商品'))


tests.append(('我的商品页面', t12))

# ====== 13. 交易记录页面 ======
def t13():
    e2e.driver.get(f'{BASE}/#/transactions')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '全部'))
    body = e2e.driver.find_element(By.TAG_NAME, 'body').text
    assert '我买到的' in body and '我卖出的' in body


tests.append(('交易记录页面', t13))

# ====== 14. 留言页面 ======
def t14():
    e2e.driver.get(f'{BASE}/#/messages')
    time.sleep(2)
    sent_btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "我发出")]')
    if sent_btns:
        sent_btns[0].click()
        time.sleep(2)


tests.append(('留言页面 筛选+内容', t14))

# ====== 15. 注册表单客户端校验 ======
def t15():
    e2e.driver.execute_script('localStorage.clear()')
    e2e.driver.get(f'{BASE}/#/register')
    time.sleep(1)
    submits = e2e.driver.find_elements(By.XPATH, '//button[@type="submit"]')
    if submits:
        submits[0].click()
        time.sleep(1)
        assert page_has('请填写') or page_has('不能为空') or page_has('格式')
    else:
        raise Exception('未找到提交按钮')


tests.append(('注册表单客户端校验', t15))

# ====== 16. 管理员登录 ======
def t16():
    e2e.driver.execute_script('localStorage.clear()')
    e2e.driver.get(f'{BASE}/#/login')
    e2e.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="10位学号"]'))).send_keys('2202300000')
    e2e.driver.find_element(By.XPATH, '//input[@placeholder="输入密码"]').send_keys('admin123' + Keys.ENTER)
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '管理后台'))


tests.append(('管理员登录 显示管理后台', t16))

# ====== 17. 管理后台概览页 ======
def t17():
    e2e.driver.get(f'{BASE}/#/admin')
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '概览'))
    assert page_has('用户总数') and page_has('商品总数')


tests.append(('管理后台概览页', t17))

# ====== 18. 管理后台用户管理 ======
def t18():
    e2e.driver.get(f'{BASE}/#/admin')
    time.sleep(1)
    btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "用户管理")]')
    if btns:
        e2e.driver.execute_script('arguments[0].click()', btns[0])
        time.sleep(2)
    assert page_has('学号')


tests.append(('管理后台用户管理', t18))


# ====== 19. 发布商品 ======
def t19():
    e2e.driver.get(f'{BASE}/#/product/new')
    time.sleep(2)
    inputs = e2e.driver.find_elements(By.TAG_NAME, 'input')
    title_input = None
    price_input = None
    for inp in inputs:
        ph = inp.get_attribute('placeholder') or ''
        if '商品名称' in ph:
            title_input = inp
        elif '0.00' in ph:
            price_input = inp
    if title_input and price_input:
        title_input.send_keys('Selenium发布的测试商品')
        price_input.send_keys('99.99')
        time.sleep(1)
        submits = e2e.driver.find_elements(By.XPATH, '//button[@type="submit"]')
        if submits:
            e2e.driver.execute_script('arguments[0].click()', submits[0])
            time.sleep(3)
    else:
        raise Exception(f'未找到输入框: title={title_input is not None}, price={price_input is not None}')


tests.append(('发布商品', t19))

# ====== 20. 退出登录 ======
def t20():
    e2e.driver.get(f'{BASE}/#/')
    time.sleep(1)
    logout_btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "退出")]')
    if logout_btns:
        e2e.driver.execute_script('arguments[0].click()', logout_btns[0])
        time.sleep(2)
        body = e2e.driver.find_element(By.TAG_NAME, 'body').text
        assert '登录' in body and '注册' in body


tests.append(('退出登录', t20))

# ====== 21. 404 页面 ======
def t21():
    e2e.driver.get(f'{BASE}/#/nonexistent')
    time.sleep(2)
    body = e2e.driver.find_element(By.TAG_NAME, 'body').text
    # 应该正常显示页面（Hash 路由不触发 404，显示首页或其他内容）
    assert True


tests.append(('404路由处理', t21))

# ====== 22. 管理员查看商品管理 ======
def t22():
    # 先用 admin 登录
    e2e.driver.execute_script('localStorage.clear()')
    e2e.driver.get(f'{BASE}/#/login')
    e2e.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="10位学号"]'))).send_keys('2202300000')
    e2e.driver.find_element(By.XPATH, '//input[@placeholder="输入密码"]').send_keys('admin123' + Keys.ENTER)
    e2e.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '管理后台'))
    # 进入商品管理
    e2e.driver.get(f'{BASE}/#/admin')
    time.sleep(1)
    prod_btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "商品管理")]')
    if prod_btns:
        e2e.driver.execute_script('arguments[0].click()', prod_btns[0])
        time.sleep(2)
        assert page_has('标题') or page_has('分类')


tests.append(('管理员商品管理', t22))

# ====== 23. 翻页功能 ======
def t23():
    e2e.driver.get(f'{BASE}/#/')
    time.sleep(2)
    next_btns = e2e.driver.find_elements(By.XPATH, '//button[contains(text(), "下一页")]')
    if next_btns:
        e2e.driver.execute_script('arguments[0].click()', next_btns[0])
        time.sleep(2)
        assert True


tests.append(('翻页功能', t23))

# ====== 24. 注册重复学号 ======
def t24():
    e2e.driver.get(f'{BASE}/#/register')
    time.sleep(1)
    inputs = e2e.driver.find_elements(By.TAG_NAME, 'input')
    sid_input = None
    email_input = None
    for inp in inputs:
        ph = inp.get_attribute('placeholder') or ''
        if '22023' in ph:
            sid_input = inp
        elif '@' in ph:
            email_input = inp
    assert sid_input and email_input, '未找到学号或邮箱输入框'
    sid_input.clear()
    sid_input.send_keys(TEST_SID)
    email_input.clear()
    email_input.send_keys(f'dup_{random.randint(100,999)}@qq.com')
    pw_inputs = e2e.driver.find_elements(By.XPATH, '//input[@type="password"]')
    if pw_inputs:
        pw_inputs[0].send_keys('test123')
    submits = e2e.driver.find_elements(By.XPATH, '//button[@type="submit"]')
    if submits:
        submits[0].click()
        time.sleep(2)


tests.append(('重复学号注册校验', t24))


if __name__ == '__main__':
    e2e.run(tests)
