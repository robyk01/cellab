from __future__ import annotations
from typing import Optional, Tuple, List, Dict
from .automaton import CellularAutomaton
from .grid import Grid, BoundaryMode


class SimulationAnalyzer:
    """
    Answers the 5 core project questions defined in CelLab requirements:
      1. What is the state after N iterations?
      2. When does the system reach a stable state?
      3. Does a particular configuration ever occur?
      4. How many cells of type X exist after N iterations?
      5. Does the simulation enter a cycle?

    The analyzer never changes the automaton passed in: when it needs to simulate
    further, it works on a copy. `max_steps` is always the maximum number of NEW
    steps to simulate beyond the automaton's current generation.
    """

    @staticmethod
    def state_after_n(automaton: CellularAutomaton, n: int) -> Grid:
        """Question 1: What is the state after N iterations (generation index n)?"""
        if n < 0:
            raise ValueError(f"Generation index must be >= 0, got {n}")
        if n <= automaton.current_step:
            return automaton.get_generation(n)

        sim = automaton.clone()
        sim.run(n - sim.current_step)
        return sim.grid

    @staticmethod
    def reaches_stable_state(
        automaton: CellularAutomaton,
        max_steps: int = 500,
    ) -> Optional[int]:
        """
        Question 2: When does the system reach a stable state?
        Returns the first generation index t where state(t) == state(t + 1),
        or None if not reached within max_steps new steps.
        """
        # Check generations already simulated
        generations = automaton.history + [automaton.grid]
        for t in range(len(generations) - 1):
            if generations[t] == generations[t + 1]:
                return t

        # Simulate further on a copy
        sim = automaton.clone()
        for _ in range(max_steps):
            prev_grid = sim.grid
            sim.step()
            if sim.grid == prev_grid:
                return sim.current_step - 1
        return None

    @staticmethod
    def pattern_occurs(
        automaton: CellularAutomaton,
        pattern: List[List[Optional[int]]],
        max_steps: int = 200,
    ) -> Optional[int]:
        """
        Question 3: Does a particular subgrid configuration / pattern ever occur?
        `None` entries in the pattern match any state.
        Returns the first generation index where the pattern is found, or None.

        With TOROIDAL boundaries the pattern may wrap around the edges.
        With FIXED boundaries it must fit completely inside the grid.
        """
        pat_h = len(pattern)
        if pat_h == 0:
            return 0
        pat_w = len(pattern[0])

        def matches(grid: Grid) -> bool:
            if grid.boundary_mode == BoundaryMode.FIXED:
                rows = range(grid.height - pat_h + 1)
                cols = range(grid.width - pat_w + 1)
            else:
                rows = range(grid.height)
                cols = range(grid.width)

            for r in rows:
                for c in cols:
                    if all(
                        pattern[pr][pc] is None or grid.get(r + pr, c + pc) == pattern[pr][pc]
                        for pr in range(pat_h)
                        for pc in range(pat_w)
                    ):
                        return True
            return False

        # Check generations already simulated
        for idx, hist_grid in enumerate(automaton.history):
            if matches(hist_grid):
                return idx
        if matches(automaton.grid):
            return automaton.current_step

        # Simulate further on a copy
        sim = automaton.clone()
        for _ in range(max_steps):
            sim.step()
            if matches(sim.grid):
                return sim.current_step

        return None

    @staticmethod
    def count_cells_of_type(automaton: CellularAutomaton, cell_type: int, n: int) -> int:
        """Question 4: How many cells of type X exist after N iterations?"""
        grid = SimulationAnalyzer.state_after_n(automaton, n)
        return grid.count_cells_of_type(cell_type)

    @staticmethod
    def detect_cycle(
        automaton: CellularAutomaton,
        max_steps: int = 500,
    ) -> Optional[Tuple[int, int]]:
        """
        Question 5: Does the simulation enter a cycle?
        Returns (cycle_start_step, cycle_length) if a cycle is found within
        max_steps new steps, else None.
        """
        # Map: grid state -> first generation index it was seen at
        seen_states: Dict[Tuple[Tuple[int, ...], ...], int] = {}

        # Check generations already simulated (history + current grid)
        generations = automaton.history + [automaton.grid]
        for idx, grid in enumerate(generations):
            state_key = grid.to_tuples()
            if state_key in seen_states:
                start_step = seen_states[state_key]
                return (start_step, idx - start_step)
            seen_states[state_key] = idx

        # Simulate further on a copy
        sim = automaton.clone()
        for _ in range(max_steps):
            sim.step()
            state_key = sim.grid.to_tuples()
            if state_key in seen_states:
                start_step = seen_states[state_key]
                return (start_step, sim.current_step - start_step)
            seen_states[state_key] = sim.current_step

        return None
