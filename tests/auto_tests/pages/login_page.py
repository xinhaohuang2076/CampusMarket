"""登录页面 Page Object"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from driver import BASE


class LoginPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @property
    def student_id_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-student-id"]')

    @property
    def password_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-password"]')

    @property
    def submit_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-submit"]')

    def goto(self):
        self.driver.get(f'{BASE}/#/login')
        return self

    def login(self, student_id: str, password: str):
        self.student_id_input.send_keys(student_id)
        self.password_input.send_keys(password + Keys.ENTER)
        return self
