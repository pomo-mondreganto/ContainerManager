import logging
import os

import config
from celery_manager import tasks
from helpers import database

logger = logging.getLogger(__name__)


def add_task(task_name):
    task_id = database.get_task_id_by_name(task_name)
    if task_id:
        print('Task already exists')
        return

    task_dir = os.path.join(config.get_app_config().tasks_dir, task_name)
    if not os.path.isdir(task_dir):
        print('Invalid task_name, directory doesn\'t exist')
        return

    conn, curs = database.get_connection_cursor()
    query = "INSERT INTO Task (name) VALUES (?)"
    curs.execute(query, (task_name,))
    conn.commit()
    curs.close()

    print("Done")


def run_build_task(task_name):
    task_id = database.get_task_id_by_name(task_name)
    if not task_id:
        print('Invalid task name')

    tasks.build_task.delay(task_name)


def run_start_task(task_name):
    task_id = database.get_task_id_by_name(task_name)
    if not task_id:
        print('Invalid task name')

    tasks.start_task.delay(task_name)


def run_stop_task(task_name):
    task_id = database.get_task_id_by_name(task_name)
    if not task_id:
        print('Invalid task name')

    tasks.stop_task.delay(task_name)


def run_restart_task(task_name, with_build=False):
    task_id = database.get_task_id_by_name(task_name)
    if not task_id:
        print('Invalid task name')

    if with_build:
        tasks.restart_rebuild_task.delay(task_name)
    else:
        tasks.restart_task.delay(task_name)


def run_auto_add_tasks():
    tasks_dir = config.get_app_config().tasks_dir
    files = os.listdir(tasks_dir)
    for file in files:
        file_path = os.path.join(tasks_dir, file)
        if not os.path.isdir(file_path):
            continue

        task_id = database.get_task_id_by_name(file)
        if task_id:
            continue

        print(f'Adding task {file}')
        add_task(file)


def disable_task(task_name):
    conn, curs = database.get_connection_cursor()
    query = "UPDATE Task SET enabled='n' WHERE name=?"

    curs.execute(query, (task_name,))
    conn.commit()
    curs.close()
    run_stop_task(task_name)


def enable_task(task_name):
    conn, curs = database.get_connection_cursor()
    query = "UPDATE Task SET enabled='y' WHERE name=?"

    curs.execute(query, (task_name,))
    conn.commit()
    curs.close()
    run_start_task(task_name)


def start_all_tasks():
    conn, curs = database.get_connection_cursor()
    query = "SELECT id from Task WHERE enabled='y'"

    curs.execute(query)
    enabled_tasks = curs.fetchall()
    curs.close()
    for task_name, in enabled_tasks:
        add_task(task_name)


def stop_all_tasks():
    conn, curs = database.get_connection_cursor()
    query = "SELECT name from Task WHERE enabled='y'"

    curs.execute(query)
    enabled_tasks = curs.fetchall()
    curs.close()
    for task_name, in enabled_tasks:
        tasks.stop_task.delay(task_name)


def restart_all_tasks(with_build=False):
    conn, curs = database.get_connection_cursor()
    query = "SELECT name from Task WHERE enabled='y'"

    curs.execute(query)
    enabled_tasks = curs.fetchall()
    curs.close()
    for task_name, in enabled_tasks:
        if with_build:
            tasks.restart_rebuild_task.delay(task_name)
        else:
            tasks.restart_task.delay(task_name)


def reset_tasks():
    stop_all_tasks()
    conn, curs = database.get_connection_cursor()
    # noinspection SqlWithoutWhere
    query = "DELETE FROM Task"
    curs.execute(query)
    conn.commit()
    curs.close()
    run_auto_add_tasks()
    start_all_tasks()
