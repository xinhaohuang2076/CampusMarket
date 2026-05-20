"""Selenium Edge 快速回归测试（8 项核心流程，Page Object 版）"""
from selenium.webdriver.common.by import By
from driver import E2ETest, BASE
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from pages.product_page import ProductPage

e2e = E2ETest('快速回归 — 8 项核心流程')
tests = []


def test1():
    """首页商品列表加载"""
    home = HomePage(e2e.driver, e2e.wait).goto()
    cards = home.product_cards
    assert len(cards) > 0, '商品卡片未加载'


tests.append(('首页商品列表加载', test1))


def test2():
    """搜索"数学"返回结果"""
    import time
    home = HomePage(e2e.driver, e2e.wait)
    home.search('数学')
    time.sleep(2)
    cards = home.product_cards
    assert len(cards) > 0, '搜索结果为空'


tests.append(('搜索功能', test2))


def test3():
    """商品详情页面"""
    detail = ProductPage(e2e.driver, e2e.wait).goto(1)
    assert detail.title.is_displayed()
    assert detail.price.is_displayed()


tests.append(('商品详情页面', test3))


def test4():
    """登录页面加载"""
    login = LoginPage(e2e.driver, e2e.wait).goto()
    assert login.student_id_input.is_displayed()
    assert login.password_input.is_displayed()


tests.append(('登录页面加载', test4))


def test5():
    """登录功能正常"""
    LoginPage(e2e.driver, e2e.wait).goto().login('2202300001', '123456')
    import time; time.sleep(2)
    body = e2e.driver.find_element(By.TAG_NAME, 'body').text
    assert '发布' in body, '登录后未显示导航'


tests.append(('登录功能', test5))


def test6():
    """注册页面加载"""
    register = RegisterPage(e2e.driver, e2e.wait).goto()
    assert register.student_id_input.is_displayed()
    assert register.email_input.is_displayed()


tests.append(('注册页面加载', test6))


def test7():
    """发布商品页面"""
    e2e.driver.get(f'{BASE}/#/product/new')
    import time; time.sleep(2)
    body = e2e.driver.find_element(By.TAG_NAME, 'body').text
    assert '发布商品' in body


tests.append(('发布商品页面', test7))


def test8():
    """管理后台概览"""
    from pages.admin_page import AdminPage
    admin = AdminPage(e2e.driver, e2e.wait)
    # 先登录 admin
    LoginPage(e2e.driver, e2e.wait).goto().login('2202300000', 'admin123')
    import time; time.sleep(2)
    admin.goto()
    import time; time.sleep(2)
    assert admin.tab('overview').is_displayed()


tests.append(('管理后台概览', test8))


if __name__ == '__main__':
    e2e.run(tests)
