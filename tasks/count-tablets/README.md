# Count out exactly 25 tablets with a pusher blade

Slide exactly 25 of 60 loose tablets across a green line on a pharmacy counting tray, toward the arms,
and leave the rest where they are. Two flat pusher blades stand beside the tray; any method is allowed.

- `count_tablets.py` is the task file: scene, scoring (`success`, `score`, `distance`) and the scripted `demo()`.
- `task.json` holds the task's details.

## Requirements

The Robocurve `yam-eval` launchable (Isaac Lab-Arena, the YAM embodiment, Dream-1 and the scripted demo
runner), set up as in the task board's simulation walkthrough. The commands below are run from the root
of this repository.

## Run a trial

Dream-1:

    inspect-robots run --embodiment yam_arena --policy dream \
      -E task=tasks/count-tablets/count_tablets.py -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 \
      --instruction "Slide exactly 25 tablets across the green line toward the arms and leave the rest where they are." \
      --scorer task_score --max-steps 2400 --store-frames --log-dir ~/yam-eval/dream

Scripted demo (reaches full score):

    inspect-robots run --embodiment yam_arena --policy yam_scripted \
      -E task=tasks/count-tablets/count_tablets.py -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 \
      --instruction "Slide exactly 25 tablets across the green line toward the arms and leave the rest where they are." \
      --scorer task_score --max-steps 2400 --store-frames --log-dir ~/yam-eval/demo

The score is the one `--scorer task_score` reports at the end of the run. Videos: `inspect-robots video <log>.json`.

## Scoring

Score = max(0, 1 - |t - 25| / 25), where t is the number of tablets fully on the arm side of the green line
(the whole tablet at x < 0.26 m) and still on the tray at the last step. Tablets that leave the tray do not
count. 25 tablets scores 1.00, 24 or 26 score 0.96, 20 or 30 score 0.80, and none scores 0.00.

## Runtime and seeds

- Runtime per trial: about 8 minutes for a Dream-1 trial (462 s wall clock) and about 6.5 minutes for the scripted demo (395 s, which includes Isaac Sim's first-run warm-up of about 4 minutes).
- The scripted demo takes about 92 s of simulated time (about 1,850 steps) of the 2,400-step limit.
- No random seeds: the layout is fixed (`-E object_jitter=0`) and the target count is fixed at 25.
