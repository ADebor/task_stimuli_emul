import logging, logging.handlers
import sys

def main_loop(tasks):
    #logging.basicConfig(level=logging.DEBUG, filename='std.log', filemode='w', format="%(asctime)s.%(msecs)03d %(name)-20s %(levelname)-8s %(message)s")
    
    for i, task in enumerate(tasks):
        print("Task #{}, press '5' to start or 'q' to quit.\n".format(i))
        while True:
            res = input()
            if res == "5":
                break
            elif res == 'q':
                print("Session exited at task #{}.\n".format(i))
                return
            else:
                print("Wrong key pressed: please press '5' or 'q'.\n")
        task.run()
