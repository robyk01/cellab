# CelLab - Cellular Automata Simulation & Analysis System

An extensible cellular automata simulation framework built for the Artificial Intelligence laboratory project (**Project CelLab**).

Based on the architectural sketch from **L3 Deliverable 1**, this repository implements **L6 Deliverable 2** (automata modeling, state transitions, experiment parameters, state storage & recovery, and simulation analytics) while preparing the foundation for future deliverables (L11 ML experiment and L13 NLP parser).

---

## 🚀 Key Features (Deliverable 2)

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

## 👥 Team Collaboration Tracks

To ensure efficient teamwork without merge conflicts or blocking dependencies, the project is structured into **two independent tracks**:

```
                  ┌──────────────────────────────────────────────┐
                  │                 CelLab Core                  │
                  │   (Rule, Grid, CellularAutomaton, Storage)   │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼                                               ▼
      ┌─────────────────────┐                         ┌─────────────────────┐
      │       TRACK 1       │                         │       TRACK 2       │
      │ Simulation Engine & │                         │ NLP Parser & GUI    │
      │    AI Analytics     │                         │    Visualization    │
      └──────────┬──────────┘                         └──────────┬──────────┘
                 │                                               │
                 ├─ Advanced Automata Rules                      ├─ Graphical Interface
                 ├─ Optimization & Question Solvers              ├─ Natural Language Parser
                 └─ L11: Dataset & NN/RL Experiment              └─ Interactive Visualizer
```

### **Track 1: Core Engine, Automata Models & AI Analytics (Deliverable 3 focus)**
* **Responsible for**:
  1. **Automata Rule Variations**: Implementing additional complex automata (e.g., Cyclic Automaton, Forest Fire, Rule 30 1D embedded).
  2. **Advanced Question Solvers**: Optimizing cycle detection (Floyd's cycle-finding / hashing) and 2D pattern matching.
  3. **L11 Deliverable 3 (NN / RL Experiment)**:
     - Generate large datasets of generation sequences across different rule sets.
     - Train a Neural Network (CNN / MLP) to predict:
       - Next generation ($t \to t+1$), or
       - Long-term behavior (stability vs. periodicity vs. extinction).

### **Track 2: GUI, Natural Language Parser & Integration (Deliverable 4 focus)**
* **Responsible for**:
  1. **Graphical Interface (GUI)**:
     - Interactive grid canvas (PyQt, Tkinter, Pygame, or Web/Streamlit).
     - Controls: Play, Pause, Step Forward, Reset, Speed Slider.
     - Interactive cell drawing / pattern placement.
     - Question & Answer display panel (dropdown to choose question, parameters input, output display).
  2. **L13 Deliverable 4 (NLP Rule Parser)**:
     - Parse natural language descriptions (e.g., *"A dead cell with 3 live neighbors becomes alive"*) into `Rule` and `CellularAutomaton` configurations.
     - System validation of user descriptions.
  3. **Documentation & Agent Logs**:
     - Maintain records of conversational assistant interactions as required by course policy.

---

## 📁 Repository Structure

```
cellab/
├── cellab/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── rule.py         # Rule dataclass and matching logic
│       ├── grid.py         # 2D Grid, boundary modes, neighbor counting
│       ├── automaton.py    # Main CellularAutomaton class & step engine
│       ├── storage.py      # JSON State storage and recovery (Deliverable 2)
│       ├── presets.py      # Game of Life, Brian's Brain, Seeds
│       └── analysis.py     # Solvers for the 5 project questions
├── tests/
│   ├── __init__.py
│   └── test_automata.py    # Comprehensive unit tests for Deliverable 2
├── demo_deliverable2.py    # Live terminal demonstration script
├── README.md               # Project documentation & team guide
└── .gitignore
```

---

## 🧪 Testing & Verification

Run the full test suite with Python's built-in `unittest` (no external dependencies required):

```bash
python3 -m unittest discover tests
```

Run the live Deliverable 2 demonstration:

```bash
python3 demo_deliverable2.py
```

---

## 💾 State Storage Example

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
