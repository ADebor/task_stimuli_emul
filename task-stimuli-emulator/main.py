import argparse
import importlib
from src.shared import cli 
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Test script parser")
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()

    ses_mod = importlib.import_module('src.sessions.ses-robots')

    tasks = ses_mod.get_tasks(args)
    cli.main_loop(tasks)
    os._exit(0) # to change
    