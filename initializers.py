import sqlite3
import docker
import requests
import config


def initialize_tasks_table():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cur = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Task(
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            `name` varchar(255) NOT NULL
        )'''
    cur.execute(query)
    conn.commit()


def initialize_services_table():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cur = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Service(
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            `name` varchar(255) NOT NULL,
            `container_id` varchar(255) NOT NULL default '',
            `user_status` varchar(16) NOT NULL default 'stopped',
            `image_id` varchar(255) NOT NULL default '',
            `cpu_limit` varchar(10) NOT NULL default '',
            `mem_limit` varchar(10) NOT NULL default '',
            `capacities` varchar(255) NOT NULL default '',
            `ports` varchar(500) NOT NULL default '',
            `task_id` INTEGER NOT NULL
        )'''
    cur.execute(query)
    conn.commit()


def initialize_database():
    initialize_tasks_table()
    initialize_services_table()


def create_docker_network():
    client = docker.from_env()
    try:
        networks = client.networks.list(names=[config.DOCKER_NETWORK_NAME])
        if networks:
            return
        client.networks.create(name=config.DOCKER_NETWORK_NAME)
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')


def run_all():
    initialize_database()
    create_docker_network()
