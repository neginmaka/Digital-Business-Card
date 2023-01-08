import unittest

from selenium import webdriver
from tests.e2e_selenium.page_models.home import HomePage


def setup():
    browser = webdriver.Chrome()
    return browser


class TestHomePage(unittest.TestCase):
    def test_basic_elements_present(self):
        browser = setup()
        home_page = HomePage(browser)
        home_page.load()

        assert home_page.is_navbar_present() is True
        assert home_page.is_search_field_present() is True
        assert home_page.get_title() in 'Digital Business Card'

        browser.quit()


if __name__ == '__main__':
    unittest.main()
