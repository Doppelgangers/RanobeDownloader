import os

from handlers.config_manager import ConfigManager


class DefaultSettingsManager:
    conf_mng = ConfigManager()

    @classmethod
    def set_default_settings(cls):
        if os.path.exists(temp := cls.conf_mng.configs["TEMP"]):
            pass
        elif os.path.exists(f"{os.sep}".join(temp.split(os.sep)[:-1])):
            os.makedirs(temp)
        else:
            raise FileNotFoundError("Path TEMP error")
