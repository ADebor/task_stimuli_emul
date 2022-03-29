import time
from typing import Optional
import copy

from psychopy import visual
#, core, logging, event
from .task_base import Task

from ..shared import config

from cozmo_api.controller import Controller

# ----------------------------------------------------------------- #
#                       Cozmo Abstract Task                         #
# ----------------------------------------------------------------- #

class CozmoBaseTask(Task):
    """Base task class, implementing the basic run loop and some facilities."""

    DEFAULT_INSTRUCTION = """You will perform a task with Cozmo."""

    def __init__(
        self,
        controller: Controller = None,
        img_path: Optional[str] = None, # TODO: these paths could be moved to child class when needed
        sound_path: Optional[str] = None,
        capture_path: Optional[str] = None,
        *args,
        **kwargs,
    ):
        """CozmoTask class constructor.

        Args:
            controller (cozmo_api.controller.Controller): Controller object for interacting with Cozmo.
            img_path (Optional[str], optional): path of the image to display on Cozmo's screen. Defaults to None.
            sound_path (Optional[str], optional): path of the sound to play in Cozmo's speaker. Defaults to None.
            capture_path (Optional[str], optional): path for picture saving. Defaults to None.
        """
        super().__init__(**kwargs)
        self.controller = controller
        self.obs = None
        #self.rew = None
        self.done = False
        self.info = None
        self.actions = {
            "display": False,
            "sound": False,
            "picture": False,
            "head": [],
            "lift": [],
            "drive": [],
            "acc_rate": 0.0,
        }
        self.actions_old = {
            "display": False,
            "sound": False,
            "picture": False,
            "head": [],
            "lift": [],
            "drive": [],
            "acc_rate": 0.0,
        }
        self.img_path = img_path
        self.sound_path = sound_path
        self.capture_path = capture_path

    def _setup(self, exp_win):
        super()._setup(exp_win) #useless (pass function)
        self.controller.reset()
        while self.controller.last_frame is None:   #wait for frame to be captured (busy waiting ok ? no time constraint in setup ?)
            pass
        self._first_frame = self.controller.last_frame

        min_ratio = min(
            exp_win.size[0] / self._first_frame.size[0],
            exp_win.size[1] / self._first_frame.size[1],
        )
        width = int(min_ratio * self._first_frame.size[0])
        height = int(min_ratio * self._first_frame.size[1])

        self.game_vis_stim = visual.ImageStim(
            exp_win,
            size=(width, height),
            units="pixels",
            interpolate=False,
            flipVert=True,
            autoLog=False,
        )

    def get_actions(self, *args, **kwargs):
        """Must update the actions instance dictionary of the task class.

        Raises:
            NotImplementedError: error raised if method not overwritten in child class.
        """
        raise NotImplementedError("Must override get_actions")

    def actions_is_new(self):
        """Checks if the updated actions instance dictionary is different from the previous actions dictionary sent for controlling Cozmo.

        Returns:
            bool: True if the updated actions instance dictionary is different from the previous actions dictionary sent for controlling Cozmo. False otherwise.
        """
        return self.actions != self.actions_old

    def loop_fun(self, *args, **kwargs):
        """Custom method to be overridden if needed."""
        pass

    def _reset(self):   #TODO: should be moved to child class that needs these paths
        """Initializes/Resets display, sound and image capture handles."""
        self.controller.reset(
            img_path=self.img_path,
            sound_path=self.sound_path,
            capture_path=self.capture_path,
        )

    def _step(self):
        """Sends actions dictionary to the Controller."""
        self.controller.step(self.actions_old)

    def reset_dict(self):
        """Resets the action dictionary with default values."""
        self.actions["display"] = False
        self.actions["sound"] = False
        self.actions["picture"] = False
        self.actions["head"] = []
        self.actions["lift"] = []
        self.actions["drive"] = []
        self.actions["acc_rate"] = 0.0

    def _stop_cozmo(self):
        self.controller.stop()

    def run_cozmo(self, *args, **kwargs):
        """Main task loop."""
        _done = False
        yield True  #may be useless

        self._reset()
        #time.sleep(2)
        while not _done:
            time.sleep(0.01)
            _done = self.get_actions(*args, **kwargs)
            if _done:
                break
            elif self.actions_is_new():
                self.actions_old = copy.deepcopy(self.actions)
                self._step()
            flip = self.loop_fun(*args, **kwargs)   #TODO: the "yield" thing does not fit with the original pygame-based task organization (in task_stimuli_emulator)
            yield flip  # True if new frame, False otherwise

        self._stop_cozmo()


# ----------------------------------------------------------------- #
#                   Cozmo First Task (PsychoPy)                     #
# ----------------------------------------------------------------- #

# KEY_SET = ["x", "a", "b", "y", "u", "d", "l", "r", "p", "s", "space",]
KEY_SET = ["x", "_", "b", "_", "u", "d", "l", "r", "_", "_", "_",]
import pyglet

KEY_ACTION_DICT = {
    KEY_SET[4] : "forward",
    KEY_SET[5] : "backward",
    KEY_SET[6] : "left",
    KEY_SET[7] : "right" ,
    KEY_SET[0] : "head_up",
    KEY_SET[2] : "head_down"
    }

ACTION_ACTU_DICT = {
    "forward": "drive",
    "backward": "drive",
    "left": "drive",
    "right": "drive",
    "head_up": "head",
    "head_down": "head",
    }

_keyPressBuffer = []
_keyReleaseBuffer = []

def _onPygletKeyPress(symbol, modifier):
    if modifier:
        event._onPygletKey(symbol, modifier)
    global _keyPressBuffer
    keyTime = core.getTime()
    key = pyglet.window.key.symbol_string(symbol).lower().lstrip("_").lstrip("NUM_")
    _keyPressBuffer.append((key, keyTime))


def _onPygletKeyRelease(symbol, modifier):
    global _keyReleaseBuffer
    keyTime = core.getTime()
    key = pyglet.window.key.symbol_string(symbol).lower().lstrip("_").lstrip("NUM_")
    _keyReleaseBuffer.append((key, keyTime))


class CozmoFirstTaskPsychoPy(CozmoBaseTask):

    DEFAULT_INSTRUCTION = "Let's explore the maze !"

    def __init__(self, max_duration=5 * 60, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.max_duration=max_duration
        self.actions_list = []
        self.frame_timer = core.Clock()
        self.cnter = 0

    def _instructions(self, exp_win, ctl_win):
        screen_text = visual.TextStim(
            exp_win,
            text=self.instruction,
            alignText="center",
            color="black",
            wrapWidth=1.2,
        )
        exp_win.setColor(self.bg_color, "rgb")
        if ctl_win:
            ctl_win.setColor(self.bg_color, "rgb")

        for frameN in range(config.FRAME_RATE * config.INSTRUCTION_DURATION):
            screen_text.draw(exp_win)
            if ctl_win:
                screen_text.draw(ctl_win)
            yield ()

    def _setup(self, exp_win):
        super()._setup(exp_win)
        self.txt_stim = visual.TextStim(
            exp_win,
            text="Get in there, Cozmo !",
            font="Palatino Linotype",
            height=42,
            units="pixels",
            alignText="center",
            color=self.txt_color,
        )
        self._progress_bar_refresh_rate = 1

    def _set_key_handler(self, exp_win):
        exp_win.winHandle.on_key_press = _onPygletKeyPress
        exp_win.winHandle.on_key_release = _onPygletKeyRelease
        self.pressed_keys = set()

    def _unset_key_handler(self, exp_win):
        # deactivate custom keys handling
        exp_win.winHandle.on_key_press = event._onPygletKey

    def _handle_controller_presses(self, exp_win):  # k[0] : actual key, k[1] : time stamp
        exp_win.winHandle.dispatch_events()
        global _keyPressBuffer, _keyReleaseBuffer

        for k in _keyReleaseBuffer:
            self.pressed_keys.discard(k[0])
            logging.data(f"Keyrelease: {k[0]}", t=k[1])
        _keyReleaseBuffer.clear()
        for k in _keyPressBuffer:
            self.pressed_keys.add(k[0])
        self._new_key_pressed = _keyPressBuffer[:]  # copy
        _keyPressBuffer.clear()
        return self.pressed_keys

    def _run(self, exp_win, *args, **kwargs):
        self._set_key_handler(exp_win)
        while True:
            yield from self.run_cozmo(exp_win)
            if (
                self.max_duration and self.task_timer.getTime() > self.max_duration
            ):  # stop if we are above the planned duration
                break

    def _stop(self, exp_win, ctl_win):
        exp_win.setColor((0, 0, 0), "rgb")
        for _ in range(2):
            yield True

    def _save(self):
        pass
        return False

    def _update_value(self, actu, value):
        if type(self.actions[actu]) is bool:
            self.actions[actu] = True
        elif type(self.actions[actu]) is list:
            self.actions[actu].append(value)

    def _progressive_mov(self):
        self.cnter += 1
        if not self.actions["drive"]:
            self.cnter = 0.0
        self.actions["acc_rate"] = self.cnter * 0.01

    def _update_dict(self):
        for action in self.actions_list:
            actu = ACTION_ACTU_DICT[action]
            self._update_value(actu, action)
        self._progressive_mov()

    def _clear_key_buffers(self):
        global _keyPressBuffer, _keyReleaseBuffer
        self.pressed_keys.clear()
        _keyReleaseBuffer.clear()
        _keyPressBuffer.clear()

    def _reset(self):
        super()._reset()
        self.frame_timer.reset()

    def _render_graphics(self, exp_win):
        self.game_vis_stim.image = self.obs / 255.0
        self.game_vis_stim.draw(exp_win)

    def loop_fun(self, exp_win):
        if self.frame_timer.getTime() >= 1 / COZMO_FPS:
            self.frame_timer.reset()
            self.info = self.controller.infos
            self.obs = self.controller.last_frame
            if self.controller._mode != "test":
                self._render_graphics(exp_win)
                return True
        return False

    def get_actions(self, exp_win):
        keys = self._handle_controller_presses(exp_win)
        self.reset_dict()
        self.actions_list.clear()
        for key in keys:
            self.actions_list.append(KEY_ACTION_DICT[key])
        self._update_dict()
        return False

    def run_cozmo(self, exp_win):
        # flush all keys to avoid unwanted actions
        self._clear_key_buffers()
        super().run_cozmo(exp_win)

# ----------------------------------------------------------------- #
#                     Cozmo First Task (PyGame)                     #
# ----------------------------------------------------------------- #

""" import os
import time

import pygame
import numpy as np

from .cozmo_test_task_utils import screen_init, screen_update

# from func_timeout import func_timeout, FunctionTimedOut

COZMO_FPS = 15.0
TARGET = (350.0, 350.0)  # custom target pose
TARGET_THRESH = 25  # mm

dirname = os.path.dirname(__file__)


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class CozmoFirstTaskPyGame(CozmoBaseTask):
    def __init__(self, controller, timeout=5 * 60):
        super().__init__(
            controller=controller,
            max_duration=timeout,
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
                # pygame.quit()
                return True

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
        return False

    def update_screen(self):
        screen_update(self.obs, self.info, self._screen, self._font)

    def loop_fun(self):
        # TO CHANGE because pose not accurate enough
        self.clock_new = time.time()
        if self.clock_new - self.clock > 1 / COZMO_FPS:
            self.clock = self.clock_new
            self.info = self.controller.infos
            self.obs = self.controller.last_frame
            if self.controller._mode != "test":
                self.update_screen()

        curr_pos = (
            self.info["pose_x"],
            self.info["pose_y"],
        )
        if dist(curr_pos, TARGET) < TARGET_THRESH:
            self.done = True
            print("Well done ! You solved the task") # in less than {} seconds.\n".format(self.timeout))

    def _stop_cozmo(self):
        super()._stop_cozmo()
        pygame.quit()

    def run_cozmo(self):
        pass
        try:
            _ = func_timeout(self.timeout, super()._run_cozmo)
        except FunctionTimedOut:
            print("You could not complete the task within {} seconds. Task failed.\n".format(self.timeout))
        # TO CHANGE OR TO LET AS IN PARENT CLASS but no func_timeout
 """