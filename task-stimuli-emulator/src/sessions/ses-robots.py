
#from ..tasks.cozmo_test_task import Task
from ..tasks.cozmo_first_task import Task

import logging

from cozmo_api.controller import Controller

def get_tasks(parsed):
    if parsed.test:
        mode = "test"
    else:
        mode = "default"

    with Controller.make(
            mode=mode,
            enable_procedural_face=False,
            log_level=logging.INFO,
            protocol_log_level=logging.INFO,
            robot_log_level=logging.INFO,
        ) as ctrlr:
            for _ in range(3):
                yield Task(controler=ctrlr)


