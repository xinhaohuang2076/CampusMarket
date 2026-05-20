"""注册页面 Page Object"""
from selenium.webdriver.common.by import By
from driver import BASE


class RegisterPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @property
    def student_id_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register-student-id"]')

    @property
    def email_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register-email"]')

    @property
    def password_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register-password"]')

    @property
    def nickname_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register-nickname"]')

    @property
    def submit_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register-submit"]')

    def goto(self):
        self.driver.get(f'{BASE}/#/register')
        return self

    def register(self, student_id: str, email: str, password: str, nickname: str = ''):
        self.student_id_input.send_keys(student_id)
        self.email_input.send_keys(email)
        self.password_input.send_keys(password)
        if nickname:
            self.nickname_input.send_keys(nickname)
        self.submit_button.click()
        return self
