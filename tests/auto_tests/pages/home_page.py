"""首页 Page Object"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from driver import BASE


class HomePage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @property
    def search_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[data-testid="search-input"]')

    @property
    def category_select(self):
        from selenium.webdriver.support.ui import Select
        return Select(self.driver.find_element(By.CSS_SELECTOR, '[data-testid="category-select"]'))

    @property
    def sort_select(self):
        from selenium.webdriver.support.ui import Select
        return Select(self.driver.find_element(By.CSS_SELECTOR, '[data-testid="sort-select"]'))

    @property
    def product_cards(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')

    def goto(self):
        self.driver.get(f'{BASE}/#/')
        return self

    def search(self, keyword: str):
        self.search_input.clear()
        self.search_input.send_keys(keyword + Keys.ENTER)
        return self

    def filter_by_category(self, category: str):
        self.category_select.select_by_visible_text(category)
        return self

    def click_product(self, index=0):
        if self.product_cards:
            self.product_cards[index].click()
        return self
