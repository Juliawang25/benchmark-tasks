# Count out exactly 25 scattered tablets with a pusher blade

Slide exactly 25 of 60 loose tablets, scattered at random on a pharmacy counting tray, across a green line
toward the arms, and leave the rest on the tray on their starting side. Two small flat pusher blades stand
beside the tray; any method is allowed. Tablets that end up off the tray cost points.

- `count_tablets.py` is the task file: scene, scoring (`success`, `score`, `distance`) and the scripted `demo()`.
- `task.json` holds the task's details.

## Requirements

The Robocurve `yam-eval` launchable (Isaac Lab-Arena, the YAM embodiment, Dream-1 and the scripted demo
runner), set up as in the task board's simulation walkthrough. The commands below are run from the root
of this repository.

## Run a trial

Dream-1:

    inspect-robots run --embodiment yam_arena --policy dream \
      -E task=tasks/count-tablets-scattered/count_tablets.py -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 \
      --instruction "Slide exactly 25 tablets across the green line toward the arms. Leave the other tablets on the tray, on the side of the line they started on." \
      --scorer task_score --max-steps 2400 --store-frames --log-dir ~/yam-eval/dream

Scripted demo (reaches full score):

    inspect-robots run --embodiment yam_arena --policy yam_scripted \
      -E task=tasks/count-tablets-scattered/count_tablets.py -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 \
      --instruction "Slide exactly 25 tablets across the green line toward the arms. Leave the other tablets on the tray, on the side of the line they started on." \
      --scorer task_score --max-steps 2400 --store-frames --log-dir ~/yam-eval/demo

The score is the one `--scorer task_score` reports at the end of the run. Videos: `inspect-robots video <log>.json`.

## Scoring

Score = max(0, 1 - E / 25), where E = |t - 25| + f at the last step. t is the number of tablets on the tray
whose centre is on the arm side of the green line's centreline (x < 0.26 m), and f is the number of tablets
that are off the tray. A tablet is on the tray if its centre is within the tray's 140 x 203 mm footprint and
less than 20 mm above the floor. Tablets left on their starting side of the line are not penalized. Exactly
25 across with none off the tray scores 1.00; 24 or 26 across scores 0.96; 25 across plus 3 off the tray
scores 0.88; none across scores 0.00.

## Runtime and seeds

- Runtime per trial: about 7.5 minutes for a Dream-1 trial and about 5.3 minutes for the scripted demo, wall clock including simulator start-up (the first run on a new instance adds about 4 minutes of Isaac Sim warm-up).
- The scripted demo uses the left arm only and takes about 82 s of simulated time (about 1,650 steps) of the 2,400-step limit.
- No random seeds at run time: the scatter is generated inside the task file from a fixed seed, so every trial starts from the same layout (`-E object_jitter=0`).
