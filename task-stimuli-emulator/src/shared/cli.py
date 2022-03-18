def main_loop(tasks):
    for i, task in enumerate(tasks):
        print("Task #", i)
        task.run()
        print("End of task #", i)