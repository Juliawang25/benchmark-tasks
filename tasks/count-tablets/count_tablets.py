"""On the station table, in front of the arms: a pharmacy counting tray (203 mm wide, 140 mm deep) with 60
small loose tablets laid out on a grid, 13 columns by 5 rows. A green line is taped across the tray, 30 mm in
from the edge nearest the arms. Goal: slide exactly 25 tablets across the line toward the arms (fully on the
arm side of it) and leave the rest where they are. Tablets that leave the tray do not count.
Score = max(0, 1 - |t - 25| / 25), where t is the number of tablets fully across the line.
Two small flat pusher blades stand beside the tray, one near each arm. Any method is allowed."""

import numpy as np

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN
from yam_arena.demo import Waypoint
from yam_arena.task_file import TABLE_TOP, Box

SCENE = "station"
TOP = TABLE_TOP[SCENE]

N = 25
N_TABLETS = 60

# World frame: x forward from the arms, y left, metres.
TRAY_X0, TRAY_X1 = 0.23, 0.37
TRAY_W = 0.203
LINE_X = 0.26                   # count line; "far side" = x < LINE_X (toward the arms)
FLOOR_T, WALL_T, WALL_H = 0.004, 0.004, 0.012
TABLET = (0.008, 0.008, 0.003)

CX, CY = (TRAY_X0 + TRAY_X1) / 2, 0.0
DEPTH = TRAY_X1 - TRAY_X0

COLS = 13
YS = [-0.09 + 0.015 * i for i in range(COLS)]          # -0.09 ... +0.09
ROW_X = [0.276, 0.298, 0.320, 0.342, 0.364]
LAST_ROW_COLS = range(2, 10)                           # row 4 holds 8 tablets
LAND = [0.2355, 0.2465]                                # landing x for front row / second row                               # landing x for front row / second row

# Pusher blades: flat face toward the arms. Size is x thickness, y width, z height.
BLADE = (0.006, 0.014, 0.040)
BLADE_POS = {"right": (0.24, -0.17), "left": (0.24, 0.17)}
CLEAR = 0.002                                          # gap between blade face and tablet before pushing


def _grid():
    cells = []
    for r, x in enumerate(ROW_X):
        for c, y in enumerate(YS):
            if r == 4 and c not in LAST_ROW_COLS:
                continue
            cells.append((r, c, x, y))
    return cells


GRID = _grid()
assert len(GRID) == N_TABLETS


def _make_tablets():
    z = TOP + FLOOR_T + TABLET[2] / 2 + 0.0005
    return [
        Box(f"tablet_{i:02d}", pos=(x, y, z), size=TABLET, mass=0.001, color=(0.95, 0.95, 0.92))
        for i, (_, _, x, y) in enumerate(GRID)
    ]


WALL = (0.45, 0.47, 0.50)
TRAY = [
    Box("tray_floor", pos=(CX, CY, TOP + FLOOR_T / 2), size=(DEPTH, TRAY_W, FLOOR_T), color=(0.55, 0.57, 0.60)),
    Box("tray_front", pos=(TRAY_X0 - WALL_T / 2, CY, TOP + WALL_H / 2),
        size=(WALL_T, TRAY_W + 2 * WALL_T, WALL_H), color=WALL),
    Box("tray_back", pos=(TRAY_X1 + WALL_T / 2, CY, TOP + WALL_H / 2),
        size=(WALL_T, TRAY_W + 2 * WALL_T, WALL_H), color=WALL),
    Box("tray_left", pos=(CX, TRAY_W / 2 + WALL_T / 2, TOP + WALL_H / 2),
        size=(DEPTH, WALL_T, WALL_H), color=WALL),
    Box("tray_right", pos=(CX, -TRAY_W / 2 - WALL_T / 2, TOP + WALL_H / 2),
        size=(DEPTH, WALL_T, WALL_H), color=WALL),
    Box("count_line", pos=(LINE_X, CY, TOP + FLOOR_T - 0.0001), size=(0.003,TRAY_W, 0.0004),
        color=(0.30, 0.65, 0.30)),
]
BLADES = [
    Box(f"blade_{arm}", pos=(bx, by, TOP + BLADE[2] / 2), size=BLADE, mass=0.03, color=(0.90, 0.62, 0.20))
    for arm, (bx, by) in BLADE_POS.items()
]
OBJECTS = TRAY + _make_tablets() + BLADES


def _count(objects):
    """Tablets still on the tray and fully across the count line."""
    t = 0
    for i in range(N_TABLETS):
        s = objects[f"tablet_{i:02d}"]
        on_tray = (
            TRAY_X0 - 0.002 < s.pos[0] < TRAY_X1
            and abs(s.pos[1]) < TRAY_W / 2
            and s.pos[2] < TOP + FLOOR_T + 0.02
        )
        if on_tray and s.high[0] < LINE_X:
            t += 1
    return t


def success(objects):
    return _count(objects) == N and all(objects[f"tablet_{i:02d}"].resting() for i in range(N_TABLETS))


def distance(objects):
    return float(abs(_count(objects) - N))


def score(objects):
    return max(0.0, 1.0 - abs(_count(objects) - N) / N)


# ---- scripted demo: each arm grips its blade, pushes tablets one at a time; arms take turns ----
GRIP_UP = 0.030                                        # TCP height above the blade's bottom edge when gripped
GRASP_Z = TOP + GRIP_UP                                # blade standing on the table
TRAVEL_Z = TOP + 0.14
HOVER_Z = TOP + FLOOR_T + 0.015 + GRIP_UP              # blade bottom 15 mm above the tray floor
PUSH_Z = TOP + FLOOR_T - 0.0005 + GRIP_UP              # blade bottom at the floor
PARK = {"right": (0.20, -0.20, TRAVEL_Z), "left": (0.20, 0.20, TRAVEL_Z)}


def _slot(x_t, y, land):
    xb = x_t + TABLET[0] / 2 + CLEAR + BLADE[0] / 2    # blade centre just behind the tablet
    xe = land + TABLET[0] / 2 + BLADE[0] / 2           # blade centre with the tablet at its landing spot
    return [
        Waypoint(0.6, (xb, y, HOVER_Z), FINGER_CLOSED, "to hover"),
        Waypoint(0.4, (xb, y, PUSH_Z), FINGER_CLOSED, "descend"),
        Waypoint(1.4, (xe, y, PUSH_Z), FINGER_CLOSED, "push"),
        Waypoint(0.6, (xe, y, HOVER_Z), FINGER_CLOSED, "lift"),
    ]


def _pick(arm):
    bx, by = BLADE_POS[arm]
    return [
        Waypoint(1.5, (bx, by, TRAVEL_Z), FINGER_OPEN, "above blade"),
        Waypoint(1.2, (bx, by, GRASP_Z), FINGER_OPEN, "descend to blade"),
        Waypoint(0.8, (bx, by, GRASP_Z), FINGER_CLOSED, "grip blade"),
        Waypoint(1.2, (bx, by, TRAVEL_Z), FINGER_CLOSED, "lift blade"),
    ]


def _work(arm, cols):
    jobs = [(ROW_X[0], YS[c], LAND[0]) for c in cols]
    jobs += [(ROW_X[1], YS[c], LAND[1]) for c in cols if c != COLS - 1]
    first_xb = jobs[0][0] + TABLET[0] / 2 + CLEAR + BLADE[0] / 2
    wps = _pick(arm) + [Waypoint(1.2, (first_xb, jobs[0][1], TRAVEL_Z), FINGER_CLOSED, "over tray")]
    for job in jobs:
        wps += _slot(*job)
    last_x = jobs[-1][2] + TABLET[0] / 2 + BLADE[0] / 2
    wps += [Waypoint(0.8, (last_x, jobs[-1][1], TRAVEL_Z), FINGER_CLOSED, "raise"),
            Waypoint(1.5, PARK[arm], FINGER_CLOSED, "park")]
    return wps


def demo():
    right = _work("right", range(0, 7))                # y -0.09 ... 0.00, goes first
    left = _work("left", range(7, 13))                 # y +0.015 ... +0.09, starts after the right arm parks
    t_right = sum(w.duration for w in right)
    return {
        "right": right,
        "left": [Waypoint(1.5, PARK["left"], FINGER_OPEN, "park first"),
                 Waypoint(max(0.1, t_right - 1.0), PARK["left"], FINGER_OPEN, "wait")] + left,
    }
