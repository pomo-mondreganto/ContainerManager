import commands
import helpers


def handle_container_die(container_id):
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT `task_id` FROM Service WHERE container_id=?"
    cur.execute(query, (container_id,))
    task = cur.fetchone()
    if not task:
        return
    query = "UPDATE Service SET `user_status`=? WHERE container_id=?"
    cur.execute(query, ('stopped', container_id))
    conn.commit()
    cur.close()
    commands.stop_task(task['name'])
