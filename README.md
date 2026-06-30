*This project has been created as part of the 42 curriculum by ejulien.*

# fly-in

## Description

**fly-in** is a drone routing simulator. Given a map describing a network of
zones (nodes) connected by links (edges), a fleet of drones must travel from a
**start hub** to an **end hub** as efficiently as possible.

The goal is twofold:

1. **Find the cheapest route** through the network, taking into account the
   different costs and constraints attached to each zone (normal, restricted,
   blocked, priority).
2. **Simulate the movement of the whole fleet** turn by turn while respecting
   capacity constraints (how many drones a zone can hold, how many drones a link
   can carry simultaneously), then **visualise** the result in a graphical
   interface.

The project is written in Python and uses **pygame** for the visual
representation.

## Features

- Robust map file parser with detailed, line-numbered error messages.
- Pathfinding with **Dijkstra's algorithm** weighted by zone cost.
- Turn-by-turn fleet simulation honouring per-zone (`max_drones`) and per-link
  (`max_link_capacity`) capacities, plus a 2-turn traversal cost for
  `restricted` zones.
- Interactive **pygame** visualisation with keyboard navigation through turns,
  clickable zones showing detailed info, and an on-screen turn counter.
- A small built-in menu to pick from the bundled `easy` / `medium` / `hard`
  maps.

## Instructions

### Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) — handles the virtual environment and
  dependencies (including `pygame`) automatically.

The project ships with a `Makefile` that wraps everything, so there is nothing
to install by hand. A `drone.png` image and the `maps/` directory must be
present at the root of the repository (where the program is launched from).

### Execution

From the repository root, simply run:

```bash
make run
```

`uv` automatically creates the virtual environment, installs the dependencies
(`pygame`, ...) and launches the program. You will then be prompted to choose a
map from the list; once selected, the program parses the map, computes the best
path, simulates the fleet, and opens the graphical window.

### Other Makefile targets

| Command        | Description                                            |
|----------------|--------------------------------------------------------|
| `make run`     | Install dependencies (via `uv`) and run the program    |
| `make install` | Sync the dependencies only (`uv sync`)                 |
| `make debug`   | Run under `pdb`                                         |
| `make lint`    | Run `flake8` and `mypy` on the source                  |
| `make clean`   | Remove caches and the virtual environment              |

### Controls

| Key            | Action                          |
|----------------|---------------------------------|
| `→`            | Next turn                       |
| `←`            | Previous turn                   |
| `↑`            | Jump to the last turn           |
| `↓`            | Jump back to the first turn     |
| Mouse click    | Select a zone to display its info / clear button |
| `Esc`          | Quit                            |

## Map format

Each map is a plain text file:

```
nb_drones: 5

start_hub: start 0 0 [color=green max_drones=4]
hub: fast_junction 1 0 [zone=priority color=blue max_drones=2]
hub: blocked_zone 2 2 [zone=blocked]
end_hub: goal 4 0 [color=green max_drones=4]

connection: start-fast_junction
connection: fast_junction-goal [max_link_capacity=2]
```

- `nb_drones:` must be the first meaningful line.
- Zones are declared with `start_hub:` / `end_hub:` / `hub:` followed by
  `name x y` and optional `[key=value ...]` metadata
  (`zone`, `color`, `max_drones`).
- Connections use the `zone1-zone2` syntax with an optional
  `[max_link_capacity=N]`.
- Lines starting with `#` are comments.

## Algorithm choices and implementation strategy

### Pathfinding — Dijkstra

The natural first idea was a brute-force DFS enumerating every path and keeping
the cheapest one, but the number of paths grows exponentially and would not
scale to the larger maps. Since a "BFS that accounts for costs" is exactly
Dijkstra, the project uses **Dijkstra's algorithm** directly.

Implementation notes (`src/Pathfinder.py`):

- A binary heap (`heapq`) acts as the priority queue, always expanding the
  cheapest known node first. A monotonically increasing `counter` is pushed
  alongside the cost so tuples never need to compare `Zone` objects when costs
  are equal.
- The cost of entering a zone is given by `Zone.get_cost()`
  (`src/models.py`): `restricted` zones cost more, `blocked` zones are
  `inf` (and are also skipped explicitly so they never pollute the queue).
- The search stops as soon as the **end hub** is popped: by Dijkstra's
  invariant, its optimal cost is already known at that point.
- `get_actual_path()` rebuilds the route by walking the parent map backwards
  from the end hub to the start hub.

### Fleet simulation

The simulator (`src/Simulation.py`) advances all drones turn by turn along the
computed path:

- Each drone tracks the last zone it reached and a `remaining` counter used to
  model the **2-turn traversal of `restricted` zones** (one turn in flight on
  the connection, one turn to land).
- At the start of every turn, the current occupancy of each zone and each link
  is recomputed so that `max_drones` and `max_link_capacity` are enforced; a
  drone that cannot legally move simply stays put.
- The **start and end hubs are treated as having unlimited capacity**. Without
  this, the first drone arriving at a capacity-1 end hub would block all others
  forever — a classic deadlock that caused the simulation to loop infinitely.
- The output is a list of turns, each turn being a list of strings of the form
  `D<id>-<zone>` (landed) or `D<id>-<from>-<to>` (in transit over a connection).

## Visual representation

The pygame interface (`src/GUI.py`) turns the abstract graph and the simulation
trace into something the user can explore:

- **Graph layout** — zone coordinates are scaled to fit the window, and zones
  are drawn as coloured circles (the colour comes from the map metadata, default
  `black`), with their connections drawn as lines.
- **Drone overlay** — at each turn, drones are rendered on the zones they occupy
  (and at the midpoint of a connection when a drone is mid-flight toward a
  restricted zone), making the fleet's progress immediately readable.
- **Turn navigation** — the arrow keys let the user step forward/backward,
  jump to the first/last turn, and a counter shows `current/total` turns, so the
  whole simulation can be inspected at the user's own pace.
- **Zone inspection** — clicking a zone displays its details (name, coordinates,
  colour, type, max drones) at the bottom of the screen, helping the user
  understand *why* the chosen path behaves the way it does.

Together these features make the routing decisions and capacity constraints
tangible instead of hidden behind raw text output.

## Resources

- [pygame documentation](https://www.pygame.org/docs/) — surfaces, events,
  drawing, fonts.
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)

### Use of AI

AI (Claude) was used as a pair-programming assistant for:

- **Algorithm guidance** — discussing why a weighted BFS is equivalent to
  Dijkstra, how to terminate the search at the end hub, and how to handle
  `blocked` zones.
- **Typing & tooling** — diagnosing mypy errors (module resolution, missing
  annotations, `Optional` handling) and adding a `TypedDict` for zone info.
- **GUI explanations** — how to render images, build a clickable button, and
  draw the info bubble in pygame.

All AI suggestions were reviewed, adapted, and integrated by the author; the
design decisions and final implementation remain the author's own.
