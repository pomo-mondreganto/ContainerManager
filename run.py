import docker

import events_handler
import initializers
import prompt

initializers.run_all()

main_client = docker.from_env()
events = main_client.events(decode=True)

docker_events_handler = events_handler.EventHandler(events_obj=events)
docker_events_handler.start()

p = prompt.Prompt()

try:
    p.cmdloop()
except KeyboardInterrupt:
    events.close()
