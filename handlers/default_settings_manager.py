import os

from .config_manager import ConfigManager


class DefaultSettingsManager:
    conf_mng = ConfigManager()

    @classmethod
    def set_default_settings(cls):
        if os.path.exists(temp := cls.conf_mng.configs["TEMP"]):
            pass

        elif cls.conf_mng.configs["TEMP"] == "local":
            if not os.path.exists(path_local_temp := os.path.join(os.getcwd(), "TEMP")):
                os.makedirs(path_local_temp)

        elif os.path.exists(f"{os.sep}".join(temp.split(os.sep)[:-1])):
            os.makedirs(temp)

        else:
            raise FileNotFoundError("Path TEMP error")
