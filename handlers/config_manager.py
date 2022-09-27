import json
import os.path


class ConfigManager:
    configs = {}
    name_config_file = ''

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigManager, cls).__new__(cls)
        return cls.instance

    def __init__(self, name_config_file: str = "config.json"):
        self.name_config_file = name_config_file
        self.configs = self.get_configs()

        if self.configs.get("MP3SPLT_PATH") is None:
            self.edit_config("MP3SPLT_PATH", "local")

        if self.configs.get("SAVE_TO") is None:
            self.edit_config("SAVE_TO", "local")

        if self.configs.get("TEMP") is None:
            self.edit_config("TEMP",  "local")

    def get_configs(self):
        try:
            with open(self.name_config_file, "r") as file:
                self.configs = json.load(file)
                return self.configs
        except FileNotFoundError:
            with open(self.name_config_file, "w") as file:
                json.dump({}, file)
                return {}

    def edit_config(self, name: str, value: str):

        self.configs[name] = value
        with open(self.name_config_file, "w", encoding="utf-8") as file:
            json.dump(self.configs, file)
        return self.get_configs()
