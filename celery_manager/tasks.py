import os
import subprocess

from celery import shared_task
from celery.utils.log import get_task_logger

import config
from commands import task_status
from helpers import shell_commands

logger = get_task_logger(__name__)


@shared_task
def build_task(task_name):
    task_dir = os.path.join(config.BASE_DIR, config.get_app_config().tasks_dir, task_name)

    if not os.path.isdir(task_dir):
        logger.warning(f'Invalid task {task_name}')
        return False

    command = ["docker-compose", "build"]

    try:
        shell_commands.run_command_gracefully(
            command,
            timeout=60 * 10,
            terminate_timeout=10,
            cwd=task_dir,
        )
    except subprocess.TimeoutExpired:
        logger.warning(f'Timeout expired while building task ({task_name})')
        task_status.update_task_status(task_name, 'build timeout')
        return False
    except subprocess.CalledProcessError as e:
        logger.warning(f'Task ({task_name}) failed to build, retcode: {e.returncode}')
        task_status.update_task_status(task_name, 'build failed')
        return False
    else:
        return True


@shared_task
def start_task(task_name):
    task_dir = os.path.join(config.BASE_DIR, config.get_app_config().tasks_dir, task_name)

    if not os.path.isdir(task_dir):
        logger.warning(f'Invalid task {task_name}')
        return False

    task_dir = os.path.join(config.BASE_DIR, config.get_app_config().tasks_dir, task_name)

    command = ["docker-compose", "up"]

    try:
        shell_commands.run_command_gracefully(
            command,
            timeout=180,
            terminate_timeout=10,
            cwd=task_dir,
            check=True,
        )
    except subprocess.TimeoutExpired:
        logger.warning(f'Timeout expired while starting task ({task_name})')
        task_status.update_task_status(task_name, 'start timeout')
        return False
    except subprocess.CalledProcessError as e:
        logger.warning(f'Task ({task_name}) failed to start, retcode: {e.returncode}')
        task_status.update_task_status(task_name, 'start failed')
        return False
    else:
        task_status.update_task_status(task_name, 'running')
        return True


@shared_task
def stop_task(task_name):
    task_dir = os.path.join(config.BASE_DIR, config.get_app_config().tasks_dir, task_name)

    if not os.path.isdir(task_dir):
        logger.warning(f'Invalid task {task_name}')
        return False

    task_dir = os.path.join(config.BASE_DIR, config.get_app_config().tasks_dir, task_name)

    command = ["docker-compose", "down"]

    try:
        shell_commands.run_command_gracefully(
            command,
            timeout=180,
            terminate_timeout=10,
            cwd=task_dir,
        )
    except subprocess.TimeoutExpired:
        logger.warning(f'Timeout expired while stopping task ({task_name})')
        task_status.update_task_status(task_name, 'stop timeout')
        return False
    except subprocess.CalledProcessError as e:
        logger.warning(f'Task ({task_name}) failed to stop, retcode: {e.returncode}')
        task_status.update_task_status(task_name, 'stop failed')
        return False
    else:
        task_status.update_task_status(task_name, 'stopped')
        return True


@shared_task
def restart_task(task_id):
    if stop_task(task_id):
        start_task(task_id)


@shared_task
def restart_rebuild_task(task_id):
    r1 = build_task(task_id)
    if r1:
        r2 = stop_task(task_id)
        if r2:
            start_task(task_id)
