import os

import yaml


class CeleryConfig:
    def __init__(self, broker_url, backend_url):
        self.broker_url = broker_url
        self.backend_url = backend_url

    @classmethod
    def from_yaml(cls, base_dir, yaml_path):
        full_path = os.path.join(base_dir, yaml_path)

        with open(full_path, 'r') as config_file:
            loaded = yaml.load(config_file)
            return cls(**loaded)
