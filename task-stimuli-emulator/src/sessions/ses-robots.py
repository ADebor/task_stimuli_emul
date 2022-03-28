from ..tasks import robot
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
            log_level=logging.DEBUG,
            protocol_log_level=logging.DEBUG,
            robot_log_level=logging.DEBUG,
        ) as ctrlr:
            for run in range(1, 5):
                yield robot.CozmoFirstTask(controller=ctrlr, name=f"cozmo_run-{run}",)
    
          
