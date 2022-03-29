import os, datetime, traceback, time
import logging, logging.handlers
from psychopy import core, visual, logging, event
import itertools

TIMEOUT = 5
DELAY_BETWEEN_TASK = 5

globalClock = core.MonotonicClock(0)
logging.setDefaultClock(globalClock)

from . import config
from ..tasks import task_base, video

def listen_shortcuts():
    if any([k[1] & event.MOD_CTRL for k in event._keyBuffer]):
        allKeys = event.getKeys(["n", "c", "q"], modifiers=True)
        ctrl_pressed = any([k[1]["ctrl"] for k in allKeys])
        all_keys_only = [k[0] for k in allKeys]
        if len(allKeys) and ctrl_pressed:
            return all_keys_only[0]
    return False

def run_task_loop(loop, eyetracker=None, gaze_drawer=None, record_movie=False):
    for frameN, _ in enumerate(loop):
        if gaze_drawer:
            gaze = eyetracker.get_gaze()
            if not gaze is None:
                gaze_drawer.draw_gazepoint(gaze)
        if record_movie and frameN % 6 == 0:
            record_movie.getMovieFrame(buffer="back")
        # check for global event keys
        shortcut_evt = listen_shortcuts()
        if shortcut_evt:
            return 

def run_task(
    task, exp_win, ctl_win=None, eyetracker=None, gaze_drawer=None, record_movie=False
):
    print("Next task: %s" % str(task))

    # show instruction
    shortcut_evt = run_task_loop(
        task.instructions(exp_win, ctl_win),
        eyetracker,
        gaze_drawer,
        record_movie=exp_win if record_movie else False,
    )

    if task.use_fmri and not shortcut_evt:
        pass

    logging.info("GO")
    if eyetracker and not shortcut_evt and task.use_eyetracking:
        pass

    # send start trigger/marker to MEG + Biopac (or anything else on parallel port)
    if task.use_meg and not shortcut_evt:
        pass

    if not shortcut_evt:
        shortcut_evt = run_task_loop(
            task.run(exp_win, ctl_win),
            eyetracker,
            gaze_drawer,
            record_movie=exp_win if record_movie else False,
        )

    # send stop trigger/marker to MEG + Biopac (or anything else on parallel port)
    if task.use_meg and not shortcut_evt:
        pass

    if eyetracker:
        eyetracker.stop_recording()

    run_task_loop(
        task.stop(exp_win, ctl_win),
        eyetracker,
        gaze_drawer,
        record_movie=exp_win if record_movie else False,
    )

    # now that time is less sensitive: save files
    task.save()

    return shortcut_evt

def main_loop(
    all_tasks,
    subject,
    session,
    output_ds,
    enable_eyetracker=False,
    use_fmri=False,
    use_meg=False,
    show_ctl_win=False,
    allow_run_on_battery=False,
    enable_ptt=False,
    record_movie=False,
    skip_soundcheck=False,
):
    
    bids_sub_ses = ("sub-%s" % subject, "ses-%s" % session)
    log_path = os.path.abspath(os.path.join(output_ds, "sourcedata", *bids_sub_ses))
    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)
    log_name_prefix = "sub-%s_ses-%s_%s" % (
        subject,
        session,
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
    )
    logfile_path = os.path.join(log_path, log_name_prefix + ".log")
    log_file = logging.LogFile(logfile_path, level=logging.INFO, filemode="w")

    exp_win = visual.Window(**config.EXP_WINDOW, monitor=config.EXP_MONITOR)
    exp_win.mouseVisible = False
    
    if show_ctl_win:
        ctl_win = visual.Window(**config.CTL_WINDOW)
        ctl_win.name = "Stimuli"
    else:
        ctl_win = None

    eyetracker_client = None
    gaze_drawer = None
    if enable_eyetracker:
        pass

    if use_fmri:
        all_tasks = itertools.chain(
                [task_base.Pause(
                    """We are completing the setup and initializing the scanner.
                    We will start the tasks in a few minutes.
                    Please remain still."""
                )],
                all_tasks,
                [task_base.Pause(
                    """We are done for today.
                    The scanner might run for a few seconds to acquire reference images.
                    Please remain still.
                    We are coming to get you out of the scanner shortly."""
                )],
            )

    try:
        for task in all_tasks:

            # clear events buffer in case the user pressed a lot of buttoons
            event.clearEvents()
            # setup task files (eg. video)
            task.setup(
                exp_win,
                log_path,
                log_name_prefix,
                use_fmri=use_fmri,
                use_meg=use_meg,
            )
            print("READY")

            while True:
                exp_win.winHandle.activate()

                shortcut_evt = run_task(
                    task,
                    exp_win,
                    ctl_win,
                    eyetracker_client,
                    gaze_drawer,
                    record_movie=record_movie,    
                )

    except KeyboardInterrupt as ki:
        print(traceback.format_exc())
        logging.exp(msg="user killing the program")
        print("you killing me!")
    
    finally:
        if enable_eyetracker:
            #eyetracker_client.join(TIMEOUT)
            pass
