import os

from config.app import AppConfig
from config.celery import CeleryConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_app_config = None


def get_app_config():
    global _app_config

    if not _app_config:
        _app_config = AppConfig.from_yaml(base_dir=BASE_DIR, yaml_path='app_config.dev.yml')

    return _app_config


_celery_config = None


def get_celery_config():
    global _celery_config

    if not _celery_config:
        _celery_config = CeleryConfig.from_yaml(base_dir=BASE_DIR, yaml_path='celery_config.dev.yml')

    return _celery_config
