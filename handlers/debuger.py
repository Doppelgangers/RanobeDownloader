import os

from handlers.webdriver_manager import WebDriverManager
from handlers.config_manager import ConfigManager
from handlers.default_settings_manager import DefaultSettingsManager


class Checking_dependencies:

    @classmethod
    def test(cls):
        config_manger = ConfigManager()
        DefaultSettingsManager.set_default_settings()
        """ Проверка наличии  mp3splt.exe по пути конфигураци"""
        if not cls.path_mp3splt(config_manger.configs["MP3SPLT_PATH"]):
            raise FileNotFoundError
        if not os.path.exists(config_manger.configs["SAVE_TO"]):
            raise FileNotFoundError
        if not os.path.exists(config_manger.configs["TEMP"]):
            raise FileNotFoundError
        if not os.path.exists('chromedriver.exe'):
            if not WebDriverManager.download_chrome_driver():
                raise Exception("Webdriwer was not installed")

    @classmethod
    def path_mp3splt(cls, folder_path: str) -> bool:
        if os.path.exists(os.path.join(folder_path, 'mp3splt.exe')):
            return True
        else:
            return False
