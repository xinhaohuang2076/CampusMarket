"""商品详情页 Page Object"""
from selenium.webdriver.common.by import By
from driver import BASE


class ProductPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @property
    def title(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="product-title"]')

    @property
    def price(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')

    @property
    def favorite_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="favorite-btn"]')

    @property
    def message_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="message-input"]')

    @property
    def send_message_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="send-msg-btn"]')

    @property
    def want_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="want-btn"]')

    def goto(self, product_id: int):
        self.driver.get(f'{BASE}/#/product/{product_id}')
        return self

    def send_message(self, text: str):
        self.message_input.send_keys(text)
        self.send_message_button.click()
        return self

    def toggle_favorite(self):
        self.favorite_button.click()
        return self
