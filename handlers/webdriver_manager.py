import os
import time
import zipfile

import requests


class WebDriverManager:

    @classmethod
    def del_last_webdriver(cls):
        if os.path.exists(os.path.join(os.getcwd(), "chromedriver.exe")):
            os.remove('chromedriver.exe')
            time.sleep(0.3)
        if os.path.exists(os.path.join(os.getcwd(), "chromedriver.exe")):
            return False
        else:
            return True

    @classmethod
    def find_vers_your_google_chrome(cls):

        if os.path.exists(chrome_info_file := os.path.expandvars(r"%localappdata%/Google/Chrome/User Data/Last Version")):
            with open(chrome_info_file, 'r') as f:
                vers_chrome = f.readline()
        else:
            print("""
            Не удалось определить версию вашего браузера google chrome. 
            Если у все нет google chrome то его необходимо установить. 

            Введите версию ваешго google chrome вручную.
            Пример: 105.0.5195.54

            """)
            vers_chrome = input("Ваша версия: ").strip()
            if "." not in vers_chrome:
                print(f"Версия {vers_chrome} указанна не корректно")
                return False
        vers_chrome = vers_chrome.split('.')[:-1]
        vers_chrome = '.'.join(vers_chrome)
        return vers_chrome

    @classmethod
    def get_version_webdriver(cls, version_google):
        version_webdriver = requests.get(f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_google}', stream=True, timeout=3)
        if (error_code := version_webdriver.status_code) != 200:
            print(
                f"Error: {error_code}\nТакой версии браузера не найдено\nВведите версию корректно или скачайте webdriver под ваш GoogleChrome самостоятельно(поместить в {os.getcwd()} ).")
            return None
        return version_webdriver.text

    @classmethod
    def download_webdriver(cls, version_webdriver):
        file = requests.get(f"https://chromedriver.storage.googleapis.com/{version_webdriver}/chromedriver_win32.zip", stream=True, timeout=3)

        if (error_code := file.status_code) != 200:
            print(
                f"Error: {error_code}\nВерсии chromedriver {version_webdriver} не найдено\nПопробуйте загрузить webdriver под ваш GoogleChrome самостоятельно(поместить в {os.getcwd()} ).")
            return None

        # ===Загрузка=архива=с=драйвером============================================================================
        with open('chromedriver.zip', "wb") as f:
            for chank in file.iter_content(chunk_size=1024 * 1024):
                if chank:
                    f.write(chank)
        # ===Распаковка=архива=с=драйвером============================================================================
        with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
            zip_ref.extractall()

        os.remove('chromedriver.zip')
        print(f"Downloaded chromedriver: v{version_webdriver}")
        return True

    @classmethod
    def download_chrome_driver(cls):
        cls.del_last_webdriver()
        version_google = cls.find_vers_your_google_chrome()
        version_webdriver = cls.get_version_webdriver(version_google)
        cls.download_webdriver(version_webdriver)
        return True
