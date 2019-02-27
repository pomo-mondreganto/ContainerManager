from cmd import Cmd

import commands
import formatters


class Prompt(Cmd):
    @staticmethod
    def do_exit(_input):
        """Exit prompt"""
        print('Exiting...')
        return True

    @staticmethod
    def do_add_task(inp):
        """Add new task to task pool"""
        task_name = inp.split()[0].strip()
        kwargs = dict()
        if 'verbose' in inp:
            kwargs['verbose'] = True
        commands.add_task(task_name=task_name, **kwargs)

    @staticmethod
    def do_start_task(inp):
        """Start task, provide task_name and 'verbose' optionally"""
        task_name = inp.split()[0].strip()
        kwargs = dict()
        if 'verbose' in inp:
            kwargs['verbose'] = True
        commands.start_task(task_name=task_name)

    @staticmethod
    def do_list_tasks(inp):
        """List existing tasks"""
        result = commands.get_all_tasks()
        for task, services in result:
            print(formatters.get_task_info(task, services))

    @staticmethod
    def do_delete_task(inp):
        """Delete task by task_name"""
        task_name = inp.split()[0].strip()
        commands.remove_task(task_name=task_name)

    @staticmethod
    def do_rebuild_task(inp):
        """Rebuild task by task_name, provide 'verbose' optionally"""
        task_name = inp.split()[0].strip()
        kwargs = dict()
        if 'verbose' in inp:
            kwargs['verbose'] = True
        commands.rebuild_task(task_name=task_name, **kwargs)

    @staticmethod
    def do_stop_task(inp):
        """Stop task by name"""
        task_name = inp.split()[0].strip()
        commands.stop_task(task_name=task_name)

    @staticmethod
    def do_list_containers(inp):
        """List all containers"""
        if inp.strip() == 'running':
            containers = commands.get_running_containers()
        else:
            containers = commands.get_all_containers()

        result = '\n'.join(formatters.get_container_info(container) for container in containers)
        print(result)

    @staticmethod
    def do_prune_containers(_inp):
        """Remove all stopped containers"""
        commands.prune_containers()

    @staticmethod
    def do_get_network(_inp):
        """Get network information"""
        result = formatters.get_network_info(commands.get_network())
        print(result)
