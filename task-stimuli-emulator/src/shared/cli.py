def main_loop(tasks):
    for i, task in enumerate(tasks):
        while True:
            res = input("Task #{}, press '5' to start or 'q' to quit.\n".format(i))
            if res == "5":
                break
            elif res == 'q':
                print("Session exited at task #{}.\n".format(i))
                return
            else:
                print("Wrong key pressed: please press '5' or 'q'.\n")
        task.run()
