import json

class ConfigManager:

    @classmethod
    def get_configs(cls):
        with open('config.json', "r") as file:
            return json.load(file)

    @classmethod
    def edit_config(cls , name: str , value):
        data = ConfigManager.get_configs()
        data[name] = value
        with open('config.json', "w") as file:
            json.dump(data, file)



