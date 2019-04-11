from cmd import Cmd

from commands import task_control


class Prompt(Cmd):
    prompt = '(container_manager) '
    intro = 'Welcome to container manager!'

    @staticmethod
    def do_exit(_input):
        """Exit prompt"""
        print('Exiting...')
        return True

    @staticmethod
    def do_add_task(input):
        task_name = input.split()[0]
        task_control.add_task(task_name)

    @staticmethod
    def do_build_task(input):
        task_name = input.split()[0]
        task_control.run_build_task(task_name)

    @staticmethod
    def do_start_task(input):
        task_name = input.split()[0]
        task_control.run_start_task(task_name)

    @staticmethod
    def do_stop_task(input):
        task_name = input.split()[0]
        task_control.run_stop_task(task_name)

    @staticmethod
    def do_restart_task(input):
        task_name = input.split()[0]
        task_control.run_restart_task(task_name)

    @staticmethod
    def do_restart_task_with_build(input):
        task_name = input.split()[0]
        task_control.run_restart_task(task_name)

    @staticmethod
    def do_add_all_tasks(_input):
        task_control.run_auto_add_tasks()

    @staticmethod
    def do_stop_all_tasks(_input):
        task_control.stop_all_tasks()

    @staticmethod
    def do_start_all_tasks(_input):
        task_control.start_all_tasks()

    @staticmethod
    def do_restart_all_tasks(_input):
        task_control.restart_all_tasks()

    @staticmethod
    def do_restart_all_tasks_with_build(_input):
        task_control.restart_all_tasks()

    @staticmethod
    def do_disable_task(input):
        task_name = input.split()[0]
        task_control.disable_task(task_name)

    @staticmethod
    def do_enable_task(input):
        task_name = input.split()[0]
        task_control.enable_task(task_name)

    @staticmethod
    def do_reset_tasks(_input):
        task_control.reset_tasks()
