import os

import yaml


class AppConfig:
    def __init__(self, database_path, tasks_dir, base_dir):
        self.database_path = os.path.join(base_dir, database_path)
        self.tasks_dir = os.path.join(base_dir, tasks_dir)
        self.base_dir = base_dir

    @classmethod
    def from_yaml(cls, base_dir, yaml_path):
        full_path = os.path.join(base_dir, yaml_path)

        with open(full_path, 'r') as config_file:
            loaded = yaml.load(config_file)
            return cls(**loaded, base_dir=base_dir)
