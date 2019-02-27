import sqlite3

import config


def get_connection_cursor(return_named=False):
    conn = sqlite3.connect(config.DATABASE_PATH)
    if return_named:
        conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur
