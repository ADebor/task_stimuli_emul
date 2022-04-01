# Don't display 'Hello from the Pygame Community!'
from os import environ
try:
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
except:
    pass

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
        log_level=logging.INFO,
        protocol_log_level=logging.INFO,
        robot_log_level=logging.INFO,
    ) as ctrlr:
        for run in range(1, 5):
            print("run {}".format(run))
            yield robot.CozmoFirstTaskPsychoPy(
                controller=ctrlr,
                max_duration=2 * 60,
                name=f"cozmo_run-{run}",
                instruction="Explore the maze and find the target !",
            )
