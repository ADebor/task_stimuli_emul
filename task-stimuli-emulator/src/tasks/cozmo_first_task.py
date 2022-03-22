import os
import sys
import time

import pygame
import numpy as np

from .cozmo_base import BaseTask
from .cozmo_test_task_utils import screen_init, screen_update

from func_timeout import func_timeout, FunctionTimedOut

COZMO_FPS = 15.0
TARGET = (350.0, 350.0)  #custom target pose
TARGET_THRESH = 25 #mm

dirname = os.path.dirname(__file__)


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)   

class Task(BaseTask):
    def __init__(self, controller, timeout=5*60):
        super().__init__(
            controller=controller,
        ) 
        pygame.init()
        self.timeout = timeout
        self._screen, self._font = screen_init()
        self.actions_list = []
        self._allowed_kb_keys = {
            "forward": pygame.K_UP,
            "backward": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "head_up": pygame.K_a,
            "head_down": pygame.K_z,
        }

        self._actions2key_dict = {
            "forward": "drive",
            "backward": "drive",
            "left": "drive",
            "right": "drive",
            "head_up": "head",
            "head_down": "head",
        }

        self.clock_old = time.time()
        self.clock = time.time()

        self.cnter = 0

    def _update_value(self, key, value):
        if type(self.actions[key]) is bool:
            self.actions[key] = True
        elif type(self.actions[key]) is list:
            self.actions[key].append(value)

    def _update_dict(self):
        for a in self.actions_list:
            key = self._actions2key_dict[a]
            self._update_value(key, a)

        self.cnter += 1
        if not self.actions["drive"]:
            self.cnter = 0.0
        self.actions["acc_rate"] = self.cnter * 0.01

    def get_actions(self):
        self.reset_dict()
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.done = True
                #pygame.quit()
                return

            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.actions_list = []
                kb_keys = pygame.key.get_pressed()
                for allowed_kb_key in self._allowed_kb_keys.values():
                    if kb_keys[allowed_kb_key]:  
                        self.actions_list.append(
                            list(self._allowed_kb_keys.keys())[
                                list(self._allowed_kb_keys.values()).index(
                                    allowed_kb_key
                                )
                            ]
                        )

        self._update_dict()

    def update_screen(self):
        screen_update(self.obs, self.info, self._screen, self._font)

    def loop_fun(self):
        self.clock_new = time.time()
        if self.clock_new - self.clock > 1 / COZMO_FPS:
            self.clock = self.clock_new
            self.info = self.controller.infos
            self.obs = self.controller.last_frame
            if self.controller._mode is not "test":
                self.update_screen()
        
        curr_pos = (self.info["pose_x"], self.info["pose_y"],)
        if dist(curr_pos, TARGET) < TARGET_THRESH:
            self.done = True
            print("Well done ! You solved the task in less than {} seconds.\n".format(self.timeout)) 

    def stop(self):
        super().stop()
        pygame.quit()

    def run(self):
        try:
            _ = func_timeout(self.timeout, super().run)
        except FunctionTimedOut:
            print("You could not complete the task within {} seconds. Task failed.\n".format(self.timeout))
