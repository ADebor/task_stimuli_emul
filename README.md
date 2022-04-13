# task_stimuli_emul

PsychoPy-based emulator of the [`task_stimuli`](https://github.com/courtois-neuromod/task_stimuli) framework from the [Courtois NeuroMod Project](https://github.com/courtois-neuromod).

# Usage

Run `python main.py --subject 00 --task robots --session 0 --output test_ds` for a basic test demo.

# Global structure

TODO

# Guidelines for creating a new task

## Session

Before actually implementing the task, one has to create a session script that basically instanciates the different `Task` objects (as defined in `task_base.py`) implementing the tasks to perform in the current session.

This session script is imported in `main.py`, where the `Task` objects of the current session are retreived. In the session file, one has two options for passing the tasks to the `main` script: 

- implementing a python generator that yields the `Task` objects (see `ses-mario.py`) **reason to do that ???**

or 

- storing the `Task` objects in a list called `TASKS` (see `ses-friends-sx.py`). 

The `Task` objects are then passed to the `main_loop` implemented in `cli.py`, which
- sets up logging facilities (logging level, directories and files to write in),
- creates, start and sets up the eye-tracker client if needed,
- add `Pause` tasks before and after each task if the MRI scanner is used,
- sets up PsychoPy windows (experiment and (if wanted) control windows), 
- loops over the `Task` objects (*i.e.* sets them up, run them, restart them if needed, record movie if needed).

## Task 

Once the session file is ready, one can start implementing the actual task(s) to be performed.

A task must be a class inheriting from the `Task` class implemented in `task_base.py`. A few methods *can* be overwritten/created:
- `_setup(self, *args, **kwargs)`: used to set up what one wants, *e.g.* the visual stimulation parameters (incl. its dimension). This method is called in the `setup(self, ...)` method of the `Task` class, which initializes various variables (paths, flags, progress bar, ...).
- `_instructions(self, exp_win, ctl_win, *args, **kwargs)`: used to display instructions on the experiment window at the beginning of the task. This method, if it exists, can draw a visual  stimulation on both windows, and it is iterated over in the `instructions(self, exp_win, ctl_win)` method of the `Task` class, which flips all windows (according to the OpenGL framework). A basic example writes
```python
def _instructions(self, exp_win, ctl_win):
  screen_text = visual.TextStim(
    exp_win, 
    text="my instruction",
    alignText="center",
    color="black",
  )
  
  for frameN in range(config.FRAME_RATE * config.INSTRUCTION_DURATION):
    screen_text.draw(exp_win)
    if ctl_win:
      screen_text.draw(ctl_win)
    yield ()
```
Please note that such a method must be a python generator/iterator. Note also that one can define a `DEFAULT_INSTRUCTION` variable in the task class, that will be displayed if no instruction is passed when the task is instanciated (`instruction` parameters of the `Task` class `__init__` routine). 
- `_run(self, exp_win, ctl_win, *args, **kwargs)`: implements the actual task loop (*i.e.* everyting one wants to run during the task) as a generator, yielding `True` if the windows need to be flipped. One can also implement a timeout mechanism to exit the task, using one of the different timers provided by PsychoPy.
- `_save(self)`: this method *must* be overwritten, and should return `False` if events do not need to be saved. It also allows to override events saving if transformation are needed.
