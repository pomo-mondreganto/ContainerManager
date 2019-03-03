from threading import Thread

import handler_functions


class EventHandler(Thread):
    def __init__(self, events_obj, *args, **kwargs):
        super(EventHandler, self).__init__(*args, **kwargs)
        self.events = events_obj

    def run(self):
        for event in self.events:
            print(event)
            if event['Type'] == 'container':
                if event['status'] == 'die':
                    handler_functions.handle_container_die(event['id'])
                elif event['status'] == 'start':
                    handler_functions.handle_container_start(event['id'])
            else:
                pass
