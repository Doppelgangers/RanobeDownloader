import os

from .webdriver_manager import WebDriverManager
from .config_manager import ConfigManager
from .default_settings_manager import DefaultSettingsManager


class Checking_dependencies:

    @classmethod
    def test(cls):
        config_manger = ConfigManager()
        DefaultSettingsManager.set_default_settings()
        """ Проверка наличии  mp3splt.exe по пути конфигураци"""
        if (not cls.path_mp3splt(config_manger.configs["MP3SPLT_PATH"])) and config_manger.configs["MP3SPLT_PATH"] != "local":
            raise FileNotFoundError
        if not os.path.exists(config_manger.configs["SAVE_TO"]) and config_manger.configs["SAVE_TO"] != "local":
            raise FileNotFoundError
        if not os.path.exists(config_manger.configs["TEMP"]) and config_manger.configs["TEMP"] != "local":
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
