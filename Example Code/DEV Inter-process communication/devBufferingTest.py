"""
DEVELOPMENT TESTING
MAY BE INCOMPLETE / NON FUNCTIONAL

Testing continous audio playback with multiproccessing
"""


import context
context.get()

from multiprocessing import Manager, Queue
import magSonify
from datetime import datetime ,timedelta
from magSonify import THEMISdata
from magSonify.Buffering import BaseProcess

dataClass = THEMISdata
start = datetime(2007,9,20)
intervalHours = 12
events = ((
    start+timedelta(hours=(i)*intervalHours),
    start+timedelta(hours=(i+1)*intervalHours)
    ) for i in range(30))
events = list(events)

if __name__ == "__main__":
    manager = Manager()
    queues = (manager.Queue(maxsize=5) for i in range(3))
    queues = list(queues)
    processes = {}
    for task, taskArgs in {
        "importer": (events,), 
        "processing": (), 
        "sonification": (1,"waveletStretch",(12,0.5,12)), 
        "playback": (44100//2,)
    }.items():
        processes[task] = BaseProcess(
            task=task,
            taskArgs=taskArgs,
            queues=queues
        )
        processes[task].start()
    for task, p in processes.items():
        p.join()
        print(p,"joined")