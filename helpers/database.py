import sqlite3

import config


def get_connection_cursor(return_named=False):
    conn = sqlite3.connect(config.get_app_config().database_path)
    if return_named:
        conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur


def get_task_id_by_name(task_name):
    conn, curs = get_connection_cursor()
    query = "SELECT id from Task WHERE name=?"
    curs.execute(query, (task_name,))
    result = curs.fetchone()
    if not result:
        return None
    task_id, = result
    curs.close()

    return task_id
