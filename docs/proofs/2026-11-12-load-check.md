# Does a recording stay the same under load?

The approved to-do clip, recorded live from the same voice, 12 Nov 2026 22:59. The Mac's load when it started: 43 (other apps running); at the end: 49.

## Result

- Recorded alone, a second time (the noise): **NOT the same**
- While another video is being drawn: **NOT the same**
- While another voice is being timed: **NOT the same**
- Two recordings at once: **NOT the same**
- Three recordings at once: **NOT the same**

## alone-2

| | Alone | alone-2 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.1 | no |
| Frame gap while moving, typical (ms) | 50.0 | 83.3 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 517 | no |
| Frame gaps over 50 ms while moving | 43 | 57 | **yes** |
| Repeated frames in the video while moving | 234 | 213 | no |
| Page response after an action, typical (ms) | 63 | 53 | no |
| Page response after an action, slowest (ms) | 6971 | 6963 | no |
| Cursor travel time, average (ms) | 419 | 409 | no |
| Scheduler lateness, worst (ms) | 765 | 753 | no |
| Action vs its word, average (ms) | 53 | 35 | no |
| Action vs its word, worst (ms) | 489 | 220 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2699 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving**

## with-render

This take did not finish.

## with-timing

| | Alone | with-timing | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.6 | no |
| Frame gap while moving, typical (ms) | 50.0 | 66.7 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 500 | no |
| Frame gaps over 50 ms while moving | 43 | 47 | **yes** |
| Repeated frames in the video while moving | 234 | 204 | no |
| Page response after an action, typical (ms) | 63 | 38 | no |
| Page response after an action, slowest (ms) | 6971 | 6964 | no |
| Cursor travel time, average (ms) | 419 | 407 | no |
| Scheduler lateness, worst (ms) | 765 | 731 | no |
| Action vs its word, average (ms) | 53 | 28 | no |
| Action vs its word, worst (ms) | 489 | 73 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2671 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving**

## two-1

| | Alone | two-1 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.6 | no |
| Frame gap while moving, typical (ms) | 50.0 | 66.7 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 500 | no |
| Frame gaps over 50 ms while moving | 43 | 55 | **yes** |
| Repeated frames in the video while moving | 234 | 268 | **yes** |
| Page response after an action, typical (ms) | 63 | 55 | no |
| Page response after an action, slowest (ms) | 6971 | 6959 | no |
| Cursor travel time, average (ms) | 419 | 408 | no |
| Scheduler lateness, worst (ms) | 765 | 732 | no |
| Action vs its word, average (ms) | 53 | 22 | no |
| Action vs its word, worst (ms) | 489 | 50 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2669 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving, Repeated frames in the video while moving**

## two-2

| | Alone | two-2 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.4 | no |
| Frame gap while moving, typical (ms) | 50.0 | 66.7 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 500 | no |
| Frame gaps over 50 ms while moving | 43 | 50 | **yes** |
| Repeated frames in the video while moving | 234 | 223 | no |
| Page response after an action, typical (ms) | 63 | 72 | no |
| Page response after an action, slowest (ms) | 6971 | 6923 | no |
| Cursor travel time, average (ms) | 419 | 418 | no |
| Scheduler lateness, worst (ms) | 765 | 733 | no |
| Action vs its word, average (ms) | 53 | 38 | no |
| Action vs its word, worst (ms) | 489 | 216 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2673 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving**

## three-1

| | Alone | three-1 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.3 | no |
| Frame gap while moving, typical (ms) | 50.0 | 66.7 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 500 | no |
| Frame gaps over 50 ms while moving | 43 | 54 | **yes** |
| Repeated frames in the video while moving | 234 | 249 | **yes** |
| Page response after an action, typical (ms) | 63 | 122 | **yes** |
| Page response after an action, slowest (ms) | 6971 | 6972 | no |
| Cursor travel time, average (ms) | 419 | 411 | no |
| Scheduler lateness, worst (ms) | 765 | 733 | no |
| Action vs its word, average (ms) | 53 | 41 | no |
| Action vs its word, worst (ms) | 489 | 335 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2672 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving, Repeated frames in the video while moving, Page response after an action, typical (ms)**

## three-2

| | Alone | three-2 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 4.3 | no |
| Frame gap while moving, typical (ms) | 50.0 | 66.7 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 500 | no |
| Frame gaps over 50 ms while moving | 43 | 55 | **yes** |
| Repeated frames in the video while moving | 234 | 265 | **yes** |
| Page response after an action, typical (ms) | 63 | 122 | **yes** |
| Page response after an action, slowest (ms) | 6971 | 6971 | no |
| Cursor travel time, average (ms) | 419 | 411 | no |
| Scheduler lateness, worst (ms) | 765 | 732 | no |
| Action vs its word, average (ms) | 53 | 37 | no |
| Action vs its word, worst (ms) | 489 | 301 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2672 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving, Repeated frames in the video while moving, Page response after an action, typical (ms)**

## three-3

| | Alone | three-3 | B worse? |
|---|---|---|---|
| Page frames per second while moving | 5.0 | 3.9 | no |
| Frame gap while moving, typical (ms) | 50.0 | 83.3 | **yes** |
| Frame gap while moving, 95th pct (ms) | 500.0 | 500.0 | no |
| Longest frame gap while moving (ms) | 500 | 533 | no |
| Frame gaps over 50 ms while moving | 43 | 57 | **yes** |
| Repeated frames in the video while moving | 234 | 246 | **yes** |
| Page response after an action, typical (ms) | 63 | 33 | no |
| Page response after an action, slowest (ms) | 6971 | 6969 | no |
| Cursor travel time, average (ms) | 419 | 406 | no |
| Scheduler lateness, worst (ms) | 765 | 733 | no |
| Action vs its word, average (ms) | 53 | 27 | no |
| Action vs its word, worst (ms) | 489 | 90 | no |
| Cursor shapes along every move | 17 steps | identical | no |
| Passes needed / join checks | 1 / pass | 1 / pass | no |
| Browser frames / video | [2880, 1620] / 2675 at 60 fps | [2880, 1620] / 2692 at 60 fps | |

**B is worse: Frame gap while moving, typical (ms), Frame gaps over 50 ms while moving, Repeated frames in the video while moving**

