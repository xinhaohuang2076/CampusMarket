"""管理后台 Page Object"""
from selenium.webdriver.common.by import By
from driver import BASE


class AdminPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def tab(self, name):
        return self.driver.find_element(By.CSS_SELECTOR, f'[data-testid="admin-tab-{name}"]')

    def goto(self):
        self.driver.get(f'{BASE}/#/admin')
        return self

    def switch_to(self, tab: str):
        self.tab(tab).click()
        return self
