import helpers


def handle_container_die(container_id):
    conn, cur = helpers.get_connection_cursor()

    query = "UPDATE Service SET `user_status`=? WHERE container_id=?"
    cur.execute(query, ('stopped', container_id))
    conn.commit()
    cur.close()


def handle_container_start(container_id):
    conn, cur = helpers.get_connection_cursor()

    query = "UPDATE Service SET `user_status`=? WHERE container_id=?"
    cur.execute(query, ('running', container_id))
    conn.commit()
    cur.close()
