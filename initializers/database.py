import sqlite3

import config


def initialize_tasks_table():
    conn = sqlite3.connect(config.get_app_config().database_path)
    cur = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Task(
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            `name` varchar(255) NOT NULL,
            `status` varchar(255) NOT NULL default 'stopped',
            `enabled` varchar(1) NOT NULL default 'y'
        )'''
    cur.execute(query)
    conn.commit()
    cur.close()


def initialize_database():
    initialize_tasks_table()
