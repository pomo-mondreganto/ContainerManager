import sqlite3

import docker
import requests

import authentication
import commands
import config
import helpers
import secure_config


def initialize_tasks_table():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cur = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Task(
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            `name` varchar(255) NOT NULL
        )'''
    cur.execute(query)
    conn.commit()
    cur.close()


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
    cur.close()


def initialize_users_table():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cur = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS User(
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `login` varchar(255) NOT NULL,
                `salt` varchar(16) NOT NULL,
                `password_hash` varchar(255) NOT NULL
            )'''
    cur.execute(query)
    conn.commit()
    cur.close()


def initialize_default_admin():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cur = conn.cursor()

    query = "SELECT id from User WHERE login=?"
    cur.execute(query, (secure_config.ADMIN_LOGIN,))
    if cur.fetchone():
        cur.close()
        return

    password_hash, salt = authentication.get_password_hash(secure_config.ADMIN_PASSWORD)

    query = '''INSERT INTO User (`login`, `password_hash`, `salt`) VALUES (?, ?, ?)'''
    cur.execute(query, (secure_config.ADMIN_LOGIN, password_hash, salt))
    conn.commit()
    cur.close()


def initialize_database():
    initialize_tasks_table()
    initialize_services_table()
    initialize_users_table()
    initialize_default_admin()


def create_docker_network():
    client = docker.from_env()
    try:
        networks = client.networks.list(names=[config.DOCKER_NETWORK_NAME])
        if networks:
            return
        client.networks.create(name=config.DOCKER_NETWORK_NAME)
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')


def update_all_tasks():
    conn, cur = helpers.get_connection_cursor(return_named=True)
    query = "SELECT * FROM Task"
    cur.execute(query)
    tasks = cur.fetchall()
    for task in tasks:
        query = "SELECT * FROM Service WHERE task_id=?"
        cur.execute(query, (task['id'],))
        services = cur.fetchall()
        for service in services:
            try:
                status = commands.get_service_status(service)
            except requests.exceptions.ConnectionError:
                print(f'Could not update status for task {task["name"]}')
                return
            query = "UPDATE Service SET `user_status`=? WHERE id=?"
            cur.execute(query, (status, service['id']))
            conn.commit()
    cur.close()


def run_all():
    initialize_database()
    create_docker_network()
    update_all_tasks()
