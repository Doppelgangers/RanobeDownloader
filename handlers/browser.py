from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ec


class Browser:
    options = None

    def __init__(self):
        self.options = self.create_browser_options(background_mode=True, hide_images=True, skip_wait_load_page=True)

    @staticmethod
    def create_browser_options(background_mode: bool, hide_images: bool, skip_wait_load_page: bool) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()

        options.add_argument("--disable-blink-features=AutomationControlled")

        if hide_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

        if background_mode:
            options.headless = True

        if skip_wait_load_page:
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "none"

        return options

    def set_options(self, options: webdriver.ChromeOptions):
        self.options = options

    def get_page_akniga(self, url: str):
        try:
            driver = webdriver.Chrome(options=self.options)

            driver.get(url)

            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'audio[src]'))
            )

            html_code = driver.page_source

            driver.close()
            driver.quit()
            return html_code

        except selenium_exceptions.TimeoutException:
            raise selenium_exceptions.TimeoutException(f"Не удалось получить доступ к сайту.")

        except selenium_exceptions.SessionNotCreatedException as e:
            if 'This version of ChromeDriver' in (error := e.args[0]):
                raise Exception(f'{error}, "Обновите ChromeDriver"')

        except selenium_exceptions.WebDriverException as e:
            if (error := e.args[0]) == 'unknown error: cannot find Chrome binary':
                raise selenium_exceptions.WebDriverException(f"{error}\nGoogle Chrome не найдён в пути по умолчанию\nУстановите google chrome.")

        except Exception as e:
            raise Exception("Произошла ошибка\n\n", e.args[0])
