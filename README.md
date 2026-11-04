# CelLab - Cellular Automata Simulation & Analysis System

An extensible cellular automata simulation framework built for the Artificial Intelligence laboratory project (**Project CelLab**).

Based on the architectural sketch from **L3 Deliverable 1**, this repository implements **L6 Deliverable 2** (automata modeling, state transitions, experiment parameters, state storage & recovery, and simulation analytics) while preparing the foundation for future deliverables (L11 ML experiment and L13 NLP parser).

---

## Key Features (Deliverable 2)

- **Rule Model**: Flexible transition rules with support for neighbor count ranges (`min_count <= count <= max_count`), specific neighbor states, and unconditional state decays (e.g. Brian's Brain `FIRING -> DYING`).
- **2D World (Grid)**: Matrix state supporting configurable boundary conditions (**Toroidal** wrap-around and **Fixed** boundary) and neighborhoods (**Moore** 8-neighbor and **Von Neumann** 4-neighbor).
- **State Storage & Recovery**: Complete serialization and deserialization of world configurations, transition rules, experiment parameters, and full generation histories to and from JSON.
- **Preconfigured Automata**:
  1. **Conway's Game of Life** ($B3/S23$ - classic 2-state oscillator & still-life benchmark).
  2. **Brian's Brain** (3-state: OFF, FIRING, DYING - decay & birth).
  3. **Seeds** ($B2/S$ - pure birth chaos model).
- **Analysis Engine**: Built-in support to answer the 5 core project questions:
  1. *What is the state after $N$ iterations?*
  2. *When does the system reach a stable state?*
  3. *Does a particular configuration ever occur?*
  4. *How many cells of type $X$ exist after $N$ iterations?*
  5. *Does the simulation enter a cycle (periodic orbit)?*

---



## Repository Structure

```
cellab/
├── cellab/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── rule.py         # Rule dataclass and matching logic
│   │   ├── grid.py         # 2D Grid, boundary modes, neighbor counting
│   │   ├── automaton.py    # Main CellularAutomaton class & step engine
│   │   ├── storage.py      # JSON State storage and recovery (Deliverable 2)
│   │   ├── presets.py      # Game of Life, Brian's Brain, Seeds
│   │   └── analysis.py     # Solvers for the 5 project questions
│   ├── gui/                # PySide6 desktop interface (front end only)
│   │   ├── __init__.py     # main() starts the app
│   │   ├── main_window.py  # Window layout and controls
│   │   ├── grid_view.py    # Widget that draws the grid
│   │   └── style.py        # Dark theme
│   └── nlp.py              # Natural language -> rules (placeholder for L13)
├── tests/
│   ├── __init__.py
│   └── test_automata.py    # Comprehensive unit tests for Deliverable 2
├── demo_deliverable2.py    # Live terminal demonstration script
├── run_gui.py              # Starts the desktop interface
├── requirements.txt        # PySide6 (only needed for the interface)
├── README.md               # Project documentation & team guide
└── .gitignore
```

---

## Desktop Interface

Install PySide6 once, then start the window:

```bash
pip install -r requirements.txt
python run_gui.py
```

- **Left:** the grid. Click a cell to change its state, or drag to paint.
- **Right:** pick the game, then Play / Step / Random / Clear and adjust the speed. **Run tests** runs the test suite and shows the results.
- **Save / Load:** stores the current grid, rules and generation number in a JSON file (via `StorageManager`) and loads it back. Files made by `demo_deliverable2.py` can be loaded too.
- **Rules in natural language:** a text box for the L13 NLP update. It calls `parse_rules` in `cellab/nlp.py`, which is a placeholder for now.

---

## Testing & Verification

Run the full test suite with Python's built-in `unittest` (no external dependencies required):

```bash
python3 -m unittest discover tests
```

Run the live Deliverable 2 demonstration:

```bash
python3 demo_deliverable2.py
```

---

## State Storage Example

```python
from cellab.core.presets import create_game_of_life
from cellab.core.storage import StorageManager

# 1. Initialize and run
ca = create_game_of_life(width=10, height=10)
ca.run(10)

# 2. Save full state and history
StorageManager.save(ca, "simulation_checkpoint.json")

# 3. Recover state anytime
recovered_ca = StorageManager.load("simulation_checkpoint.json")
recovered_ca.step()  # continues seamlessly from generation 10
```
