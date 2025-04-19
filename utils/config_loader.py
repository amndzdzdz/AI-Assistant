import yaml

class ConfigLoader:

    def __init__(self, config_path: str) -> None:
        with open(config_path) as file:
            self._config = yaml.safe_load(file)

    def get(self, key: str):
        config = self._config
        for config_key in config:
            try:
                return config[config_key][key]
            except:
                raise KeyError(f"The config does not contain the key '{key}'")