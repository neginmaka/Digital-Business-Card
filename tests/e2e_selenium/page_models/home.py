from selenium.webdriver.common.by import By

navbar_id = "navbarSupportedContent2"
search_field_id = "search_field"


class HomePage:
    def __init__(self, browser):
        self.browser = browser

    def load(self):
        self.browser.get('http://127.0.0.1:5000')

    def get_title(self):
        return self.browser.title

    def is_navbar_present(self):
        return self.is_element_present_by_id(navbar_id)

    def is_search_field_present(self):
        return self.is_element_present_by_id(search_field_id)

    def is_element_present_by_id(self, element_id):
        elements = self.browser.find_elements(By.ID, element_id)
        if len(elements) == 0:
            return False
        else:
            return True
