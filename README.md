# task_stimuli_emul

PsychoPy-based emulator of the [`task_stimuli`](https://github.com/courtois-neuromod/task_stimuli) framework from the [Courtois NeuroMod Project](https://github.com/courtois-neuromod).

# Usage

Run `python main.py --subject 00 --task robots --session 0 --output test_ds` for a basic test demo.

# Guidelines for creating a new task

## Session

Before actually implementing the task, one has to create a session script that basically instanciates the different `Task` objects (as defined in `task_base.py`) implementing the tasks to perform in the current session.

This session script is imported in `main.py`, where the `Task` objects of the current session are retreived. In the session file, one has two options for passing the tasks to the `main` script: 

- implementing a python generator that yields the `Task` objects (see **example needed**) **reason to do that ???**

or 

- storing the `Task` objects in a list called `TASKS` (see **example needed**). 

The `Task` objects are then passed to the `main_loop` implemented in `cli.py`, which
- sets up logging facilities (logging level, directories and files to write in),
- creates, start and sets up the eye-tracker client if needed,
- add `Pause` tasks before and after each task if the MRI scanner is used,
- sets up PsychoPy windows (experiment and (if wanted) control windows), 
- loops over the `Task` objects (*i.e.* sets them up, run them, restart them if needed, record movie if needed).

## Task 

Once the session file is ready, one can start implementing the actual task(s) to be performed. #todo: inheritance, methods to overwrite (mendatory or not), things to *yield*, etc.
