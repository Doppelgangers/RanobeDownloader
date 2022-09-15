import json


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
            self.edit_config("MP3SPLT_PATH", 'mp3splt')

        if self.configs.get("SAVE_TO") is None:
            self.edit_config("SAVE_TO", "\\".join(__file__.split("\\")[:-2]))

        if self.configs.get("TEMP") is None:
            self.edit_config("TEMP", "\\".join(__file__.split("\\")[:-2]))

    def __str__(self):
        self.configs = self.get_configs()
        return self.configs

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


if __name__ == "__main__":
    pass

