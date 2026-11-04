from __future__ import annotations
from typing import Optional, Tuple, List, Dict
from .automaton import CellularAutomaton
from .grid import Grid


class SimulationAnalyzer:
    """
    Answers the 5 core project questions defined in CelLab requirements:
      1. What is the state after N iterations?
      2. When does the system reach a stable state?
      3. Does a particular configuration ever occur?
      4. How many cells of type X exist after N iterations?
      5. Does the simulation enter a cycle?
    """

    @staticmethod
    def state_after_n(automaton: CellularAutomaton, n: int) -> Grid:
        """Question 1: What is the state after N iterations?"""
        if n < automaton.current_step:
            return automaton.get_generation(n)

        needed_steps = n - automaton.current_step
        automaton.run(needed_steps)
        return automaton.grid

    @staticmethod
    def reaches_stable_state(
        automaton: CellularAutomaton,
        max_steps: int = 500,
    ) -> Optional[int]:
        """
        Question 2: When does the system reach a stable state?
        Returns the step index t where state(t) == state(t + 1), or None if not reached within max_steps.
        """
        for step_idx in range(automaton.current_step, max_steps):
            prev_grid = automaton.grid.clone()
            automaton.step()
            if automaton.grid == prev_grid:
                return step_idx + 1  # Reached stability at this step
        return None

    @staticmethod
    def pattern_occurs(
        automaton: CellularAutomaton,
        pattern: List[List[int]],
        max_steps: int = 200,
    ) -> Optional[int]:
        """
        Question 3: Does a particular subgrid configuration / pattern ever occur?
        Returns the first generation index where the pattern is found, or None.
        """
        pat_h = len(pattern)
        if pat_h == 0:
            return 0
        pat_w = len(pattern[0])

        def matches(grid: Grid) -> bool:
            # Check every top-left origin (r, c)
            for r in range(grid.height):
                for c in range(grid.width):
                    match = True
                    for pr in range(pat_h):
                        for pc in range(pat_w):
                            expected = pattern[pr][pc]
                            if expected is not None and grid.get(r + pr, c + pc) != expected:
                                match = False
                                break
                        if not match:
                            break
                    if match:
                        return True
            return False

        # Check existing history first
        for idx, hist_grid in enumerate(automaton.history):
            if matches(hist_grid):
                return idx
        if matches(automaton.grid):
            return automaton.current_step

        # Step forward up to max_steps
        for _ in range(automaton.current_step, max_steps):
            automaton.step()
            if matches(automaton.grid):
                return automaton.current_step

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
        Returns (cycle_start_step, cycle_length) if a cycle is found, else None.
        """
        # Map: Grid hash/state -> first seen step
        seen_states: Dict[Tuple[Tuple[int, ...], ...], int] = {}

        # Record history already simulated
        for idx, hist_grid in enumerate(automaton.history):
            state_key = hist_grid.to_tuples()
            if state_key in seen_states:
                start_step = seen_states[state_key]
                return (start_step, idx - start_step)
            seen_states[state_key] = idx

        # Record current grid
        curr_key = automaton.grid.to_tuples()
        if curr_key in seen_states:
            start_step = seen_states[curr_key]
            return (start_step, automaton.current_step - start_step)
        seen_states[curr_key] = automaton.current_step

        # Step until cycle or max_steps
        for _ in range(automaton.current_step, max_steps):
            automaton.step()
            state_key = automaton.grid.to_tuples()
            if state_key in seen_states:
                start_step = seen_states[state_key]
                cycle_len = automaton.current_step - start_step
                return (start_step, cycle_len)
            seen_states[state_key] = automaton.current_step

        return None
