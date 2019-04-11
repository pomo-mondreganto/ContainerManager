from helpers.database import get_connection_cursor


def update_task_status(task_name, new_status):
    conn, cursor = get_connection_cursor()
    query = "UPDATE `Task` SET status=? WHERE name=?"
    cursor.execute(query, (new_status, task_name))
