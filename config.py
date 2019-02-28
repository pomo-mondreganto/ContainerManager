import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'db.sqlite3')
TASKS_PATH = os.path.join(BASE_DIR, 'test_tasks')
DOCKER_NETWORK_NAME = 'ctf_tasks_network'
CPU_PERIOD = 100000
LOGIN_REGEX = '[a-z_A-Z0-9]{5,15}'
