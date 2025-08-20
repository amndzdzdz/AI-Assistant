import yaml

class ConfigLoader(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str) -> None:
        with open(config_path) as file:
            self._config = yaml.safe_load(file)

    def get_mcp_endpoint(self):
        return self._config["mcp"]["mcp_endpoint"]
    
    def get_news_endpoint(self):
        return self._config["tools"]["news_endpoint"]
    
    def get_google_scopes(self):
        return [
            self._config["google_api"]["calendar_endpoint"],
            self._config["google_api"]["gmail_endpoint"]
        ]
            
config = ConfigLoader(config_path="config/config.yaml")