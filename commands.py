import json
import os

import docker
import requests
import yaml

import config
import formatters
import helpers


def get_all_containers():
    client = docker.from_env()
    try:
        containers = client.containers.list(all=True)
        return containers
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')


def get_running_containers():
    client = docker.from_env()
    try:
        containers = client.containers.list(filters=dict(status='running'))
        return containers
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')


def get_network():
    client = docker.from_env()
    try:
        networks = client.networks.list(names=[config.DOCKER_NETWORK_NAME])
        return networks[0]
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')
    except IndexError:
        print('Network does not exist')


def create_image_from_service(client, service, service_name, task_dir, task_name, task_id, verbose):
    create_kwargs = dict()

    build_dir = os.path.join(task_dir, service['build'])

    create_kwargs['path'] = build_dir
    create_kwargs['tag'] = f'{task_name}_{service_name}'
    create_kwargs['rm'] = True

    print(f'Creating image with args: {create_kwargs}')

    image, output = client.images.build(**create_kwargs)
    print(f"Created image: {formatters.get_image_info(image)}")
    if verbose:
        print('Verbose turned on, build output printing:')
        for line in output:
            print(line)

    conn, cur = helpers.get_connection_cursor()

    query = ("INSERT INTO Service ("
             "`name`, `user_status`, `image_id`,"
             "`cpu_limit`, `mem_limit`, `task_id`,"
             "`capacities`, `ports`"
             ") "
             "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
    cpu_limit = service.get('cpus', '')
    mem_limit = service.get('mem_limit', '')

    capacities = json.dumps(service.get('cap_add', []))

    unparsed_ports = service.get('ports', [])
    parsed_ports = {each.split(':')[0]: each.split(':')[1] for each in unparsed_ports}
    ports = json.dumps(parsed_ports)

    cur.execute(query, (
        service_name,
        'stopped',
        image.id,
        cpu_limit,
        mem_limit,
        task_id,
        capacities,
        ports,
    ))
    conn.commit()
    cur.close()


def add_task(task_name, verbose=False):
    client = docker.from_env()

    conn, cur = helpers.get_connection_cursor()

    query = "SELECT * from Task WHERE name=?"
    cur.execute(query, (task_name,))
    task = cur.fetchone()
    if task:
        print('Task with that name already exists')
        return

    query = "INSERT INTO Task (`name`) VALUES (?)"
    cur.execute(query, (task_name,))
    conn.commit()
    cur.close()
    task_id = cur.lastrowid

    task_dir = os.path.join(config.TASKS_PATH, task_name)
    try:
        docker_compose = yaml.load(open(os.path.join(task_dir, 'docker-compose.yml')))
    except FileNotFoundError:
        print(f'Could not open docker-compose.yml in task directory: {task_dir}')
        return
    services = docker_compose['services']

    error = False
    for name, service in services.items():
        print(f'Creating image for service {name}')
        try:
            create_image_from_service(
                client=client,
                service=service,
                service_name=name,
                task_dir=task_dir,
                task_name=task_name,
                task_id=task_id,
                verbose=verbose,
            )
        except KeyError as e:
            print(f'Invalid dockerfile: {e}')
            error = True
            break
        except requests.exceptions.ConnectionError:
            print('Could not connect to docker daemon')
            error = True
            break

    if error:
        cur = conn.cursor()
        query = "DELETE FROM Service WHERE task_id=?"
        cur.execute(query, (task_id,))
        query = "DELETE FROM Task WHERE id=?"
        cur.execute(query, (task_id,))
        conn.commit()
        cur.close()
        print('Could not create task due to errors, cleaned up')
        return

    print(f'Task {task_id}:{task_name} created successfully!')


def create_container_from_image(service):
    if service['user_status'] != 'stopped':
        print(f'Can start only stopped containers, current status for {service["name"]}: {service["user_status"]}')
        return

    client = docker.from_env()
    image_id = service['image_id']
    try:
        image = client.images.get(image_id)
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')
        return
    except docker.errors.ImageNotFound:
        print(f'No such image: {image_id} during creation of container {service["name"]}')
        return

    print(service)
    run_kwargs = dict()
    run_kwargs['ports'] = json.loads(service['ports'])
    run_kwargs['cpu_period'] = config.CPU_PERIOD
    run_kwargs['cpu_quota'] = int(float(service['cpu_limit']) * config.CPU_PERIOD)
    run_kwargs['mem_limit'] = service['mem_limit']
    run_kwargs['cap_add'] = json.loads(service['capacities'])
    run_kwargs['name'] = service['name']
    run_kwargs['network'] = config.DOCKER_NETWORK_NAME
    run_kwargs['remove'] = True
    run_kwargs['detach'] = True

    container = client.containers.run(image=image, **run_kwargs)

    conn, cur = helpers.get_connection_cursor()
    query = "UPDATE Service SET `container_id`=?, `user_status`=? WHERE image_id=?"
    cur.execute(query, (container.id, 'running', image_id))
    cur.close()
    conn.commit()


def start_task(task_name):
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT id from task WHERE name=?"
    cur.execute(query, (task_name,))
    task = cur.fetchone()
    if not task:
        print(f'No such task {task_name}')
        return

    query = "SELECT * FROM Service WHERE task_id=?"
    cur.execute(query, (task['id'],))
    services = cur.fetchall()
    cur.close()

    for service in services:
        print(f'Starting container {service[1]}')
        create_container_from_image(service=dict(service))

    print('All containers started successfully!')


def get_all_tasks():
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT * from Task"
    cur.execute(query)
    tasks = cur.fetchall()

    results = []

    for task in tasks:
        query = "SELECT * from Service WHERE task_id=?"
        cur.execute(query, (task['id'],))
        task_services = cur.fetchall()
        results.append((dict(task), list(dict(service) for service in task_services)))

    cur.close()
    return results


def stop_service(service):
    client = docker.from_env()
    container_id = service['container_id']
    try:
        container = client.containers.get(container_id)
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')
        return
    except docker.errors.NotFound:
        print(f'No such container: {container_id} during stopping of service {service["name"]}')
        return

    container.stop()

    conn, cur = helpers.get_connection_cursor()

    query = "UPDATE Service SET `user_status`=? WHERE id=?"
    cur.execute(query, ('stopped', service['id']))
    conn.commit()
    cur.close()

    print(f'Successfully stopped container for service {service["name"]}')


def stop_task(task_name):
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT id from task WHERE name=?"
    cur.execute(query, (task_name,))
    task = cur.fetchone()
    if not task:
        print(f'No such task {task_name}')
        return

    query = "SELECT * FROM Service WHERE task_id=?"
    cur.execute(query, (task['id'],))
    services = cur.fetchall()
    cur.close()

    for service in services:
        print(f'Stopping service {service["name"]}')
        stop_service(service)

    print('All services stopped successfully!')

    print('Task stopped')


def remove_task(task_name):
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT id from task WHERE name=?"
    cur.execute(query, (task_name,))
    task = cur.fetchone()
    if not task:
        print(f'No such task {task_name}')
        return

    stop_task(task_name)

    query = "DELETE from Service WHERE task_id=?"
    cur.execute(query, (task['id'],))
    query = "DELETE from Task WHERE id=?"
    cur.execute(query, (task['id'],))

    cur.close()
    conn.commit()

    print('Task deleted')


def rebuild_task(task_name, verbose=False):
    remove_task(task_name)
    add_task(task_name, verbose=verbose)


def prune_containers():
    client = docker.from_env()
    try:
        client.containers.prune()
    except requests.exceptions.ConnectionError:
        print('Could not connect to docker daemon')
