from cozmo_api.controller import Controller
import time
from typing import Optional
import copy


class BaseTask:
    """BaseTask class, implementing the basic run loop and some facilities."""

    def __init__(
        self,
        controler: Controller = None,
        img_path: Optional[str] = None,
        sound_path: Optional[str] = None,
        capture_path: Optional[str] = None,
    ):
        """BaseTask class constructor.

        Args:
            img_path (Optional[str], optional): path of the image to display on Cozmo's screen. Defaults to None.
            sound_path (Optional[str], optional): path of the sound to play in Cozmo's speaker. Defaults to None.
            capture_path (Optional[str], optional): path for picture saving. Defaults to None.
        """
        
        self.controler = controler
        self.obs = None
        self.rew = None
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

    def get_actions(self):
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

    def loop_fun(self):
        """Custom method to overwrite if needed."""
        pass

    def _reset(self):
        """Initializes/Resets display, sound and image capture handles."""
        self.controler.reset(
            img_path=self.img_path,
            sound_path=self.sound_path,
            capture_path=self.capture_path,
        )

    def _step(self):
        """Sends actions dictionary to the Controller."""
        self.controler.step(self.actions_old)

    def reset_dict(self):
        """Resets the action dictionary with default values."""
        self.actions["display"] = False
        self.actions["sound"] = False
        self.actions["picture"] = False
        self.actions["head"] = []
        self.actions["lift"] = []
        self.actions["drive"] = []
        self.actions["acc_rate"] = 0.0

    def run(self):
        """Main task loop."""
        self._reset()
        time.sleep(2)
        while True:
            time.sleep(0.01)
            self.get_actions()
            if self.done:
                return
            elif self.actions_is_new():
                self.actions_old = copy.deepcopy(self.actions)
                self._step()

            self.loop_fun()
        return 
