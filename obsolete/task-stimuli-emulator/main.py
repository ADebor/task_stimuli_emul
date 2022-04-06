import argparse
import importlib
from src.shared import cli 
import sys

def main():
    parser = argparse.ArgumentParser(description="Test script parser")
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()

    ses_mod = importlib.import_module('src.sessions.ses-robots')

    tasks = ses_mod.get_tasks(args)
    cli.main_loop(tasks)
    sys.exit(1)

if __name__=="__main__":
    main()
    