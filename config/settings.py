import os
import yaml
import logging

class Settings:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback default configuration if file is missing
            self._config = {
                'data': {'data_dir': './data', 'cache_expiry_days': 1},
                'logging': {'level': 'INFO'},
                'strategies': {}
            }
            logging.warning(f"Config file not found at {config_path}. Using defaults.")

    def get(self, path, default=None):
        """
        Get a configuration value using dot notation.
        e.g. settings.get('strategies.momentum.window_short', 20)
        """
        keys = path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

settings = Settings()
