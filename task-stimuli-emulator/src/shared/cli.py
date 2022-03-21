def main_loop(tasks):
    for i, task in enumerate(tasks):
        x = input("Task #{}, press 5 to start.\n".format(i))
        if(x):
            task.run()
            print("End of task #{}\n".format(i))