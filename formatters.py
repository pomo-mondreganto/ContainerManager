def get_container_info(container):
    return (
        f"id: {container.short_id}; "
        f"name: {container.name}; "
        f"image: {container.image}; "
        f"status: {container.status}"
    )


def get_network_info(network):
    return (
        f"id: {network.short_id}; "
        f"name: {network.name}; "
        f"containers: {network.containers}"
    )


def get_image_info(image):
    return (
        f"id: {image.short_id}; "
        f"tags: {image.tags} "
        f"labels: {image.labels}"
    )


def get_service_info(service):
    if not isinstance(service, dict):
        service = dict(service)
    return ' '.join(f'{key}:{value}' for key, value in service.items())


def get_task_info(task, services):
    result = f"Task {task['id']}:{task['name']}, status: {task['user_status']}"
    services = '\n\t'.join(get_service_info(service) for service in services)
    return '\n\t'.join([result, services])
