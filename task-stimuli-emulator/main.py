import sys, importlib
from src.shared import parser 
from src.shared.didyoumean import suggest_session_tasks

def run(parsed):
    try:
        ses_mod = importlib.import_module('src.sessions.ses-%s'%parsed.tasks)
        tasks = ses_mod.get_tasks(parsed) if hasattr(ses_mod, 'get_tasks') else ses_mod.TASKS
    except ImportError:
        suggestion = suggest_session_tasks(parsed.tasks)
        raise(ValueError('session tasks file cannot be found for %s. Did you mean %s ?'%(parsed.tasks, suggestion)))

    from src.shared import cli
    try:
        cli.main_loop(
            tasks,
            parsed.subject,
            parsed.session,
            parsed.output,
            parsed.eyetracking,
            parsed.fmri,
            parsed.meg,
            parsed.ctl_win,
            parsed.run_on_battery,
            parsed.ptt,
            parsed.record_movie,
            parsed.skip_soundcheck,
            )
    finally:
        sys.exit(1)

if __name__=="__main__":
    parsed = parser.parse_args()
    run(parsed)
    