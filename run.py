import docker
import requests

import events_handler
import initializers
import prompt

if __name__ == '__main__':
    try:
        initializers.run_all()
    except docker.errors.APIError:
        print('Unable to initialize manager, docker is not running')
        exit(1)

    main_client = docker.from_env()
    try:
        events = main_client.events(decode=True)
    except requests.exceptions.ConnectionError:
        print('Unable to connect to docker')
        exit(1)
    finally:
        events = None

    docker_events_handler = events_handler.EventHandler(events_obj=events)
    docker_events_handler.start()

    p = prompt.Prompt()

    try:
        p.cmdloop()
    except KeyboardInterrupt:
        pass
        events.close()
