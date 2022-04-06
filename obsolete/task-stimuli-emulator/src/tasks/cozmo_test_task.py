import os
import sys
import time

import pygame

from .cozmo_base import BaseTask
from .cozmo_test_task_utils import screen_init, screen_update

COZMO_FPS = 15.0

dirname = os.path.dirname(__file__)

class Task(BaseTask):
    def __init__(self, controler):
        super().__init__(
            controler=controler,
            img_path=os.path.abspath(os.path.join(dirname, '..', 'data', 'images', 'cneuromod_bw.png')),
            sound_path=os.path.abspath(os.path.join(dirname, '..', 'data', 'audio', 'hello.wav')),
            capture_path=os.path.abspath(os.path.join(dirname, '..', 'data', 'captures', 'picture.png')),
        )
        pygame.init()
        self._screen, self._font = screen_init()
        self.actions_list = []
        self._allowed_kb_keys = {
            "forward": pygame.K_UP,
            "backward": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "head_up": pygame.K_a,
            "head_down": pygame.K_z,
            "lift_up": pygame.K_u,
            "lift_down": pygame.K_d,
            "picture": pygame.K_p,
            "display": pygame.K_SPACE,
            "sound": pygame.K_s,
        }

        self._actions2key_dict = {
            "forward": "drive",
            "backward": "drive",
            "left": "drive",
            "right": "drive",
            "head_up": "head",
            "head_down": "head",
            "lift_up": "lift",
            "lift_down": "lift",
            "picture": "picture",
            "display": "display",
            "sound": "sound",
        }

        self.clock_old = time.time()
        self.clock = time.time()

        self.cnter = 0

    def _update_value(self, key, value):
        if type(self.actions[key]) is bool:
            self.actions[key] = True
        elif type(self.actions[key]) is list:
            self.actions[key].append(value)
        """ elif type(self.actions[key]) is str:
            self.actions[key] = value """

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
                pygame.quit()
                #sys.exit()
                return

            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.actions_list = []
                kb_keys = pygame.key.get_pressed()
                for allowed_kb_key in self._allowed_kb_keys.values():
                    if kb_keys[allowed_kb_key]:  # if key has been pressed
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
        # custom function
        self.clock_new = time.time()
        if self.clock_new - self.clock > 1 / COZMO_FPS:
            self.clock = self.clock_new
            self.info = self.controler.infos
            self.obs = self.controler.last_frame
            if self.controler._mode is not "test":
                self.update_screen()

    def run(self):
        super().run()
