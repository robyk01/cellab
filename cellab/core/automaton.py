from __future__ import annotations
from typing import List, Dict, Any, Optional
from .rule import Rule
from .grid import Grid, BoundaryMode, NeighborhoodType


class CellularAutomaton:
    """
    Core engine for CelLab, following the L3 Deliverable 1 sketch:
      - Holds grid dimensions, number of states, transition rules, active grid, and history.
      - Applies rules to transform generation t -> generation t + 1.
    """
    def __init__(
        self,
        width: int,
        height: int,
        num_states: int,
        rules: Optional[List[Rule]] = None,
        initial_grid: Optional[Grid] = None,
        boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
        neighborhood: NeighborhoodType = NeighborhoodType.MOORE,
        name: str = "Automaton",
        experiment_params: Optional[Dict[str, Any]] = None,
    ):
        self.width = width
        self.height = height
        self.num_states = num_states
        self.rules: List[Rule] = rules or []
        self.boundary_mode = BoundaryMode(boundary_mode)
        self.neighborhood = NeighborhoodType(neighborhood)
        self.name = name
        self.experiment_params: Dict[str, Any] = experiment_params or {}

        if initial_grid is not None:
            self.grid = initial_grid.clone()
        else:
            self.grid = Grid(
                height=self.height,
                width=self.width,
                boundary_mode=self.boundary_mode,
            )

        for rule in self.rules:
            self._check_state(rule.current_state, "Rule current_state")
            self._check_state(rule.next_state, "Rule next_state")
            if rule.target_neighbor_state is not None:
                self._check_state(rule.target_neighbor_state, "Rule target_neighbor_state")
        self._check_matrix(self.grid.cells)

        # History stores all simulated states (history[0] is initial state)
        self.history: List[Grid] = []
        self.initial_state: Grid = self.grid.clone()

    def _check_state(self, state: int, what: str = "State") -> None:
        """Raises ValueError if `state` is not one of 0 .. num_states - 1."""
        if not 0 <= state < self.num_states:
            raise ValueError(
                f"{what} {state} is invalid: must be between 0 and {self.num_states - 1}"
            )

    def _check_matrix(self, matrix: List[List[int]]) -> None:
        for r, row in enumerate(matrix):
            for c, state in enumerate(row):
                self._check_state(state, f"Cell ({r}, {c}) state")

    def clone(self) -> CellularAutomaton:
        """Returns an independent copy (grid, history, rules and parameters)."""
        copy = CellularAutomaton(
            width=self.width,
            height=self.height,
            num_states=self.num_states,
            rules=list(self.rules),
            initial_grid=self.grid,
            boundary_mode=self.boundary_mode,
            neighborhood=self.neighborhood,
            name=self.name,
            experiment_params=dict(self.experiment_params),
        )
        copy.initial_state = self.initial_state.clone()
        copy.history = [g.clone() for g in self.history]
        return copy

    def set_grid(self, matrix: List[List[int]]) -> None:
        """Sets the current grid state from a 2D matrix and resets initial state."""
        self._check_matrix(matrix)
        self.grid = Grid(
            height=self.height,
            width=self.width,
            initial_matrix=matrix,
            boundary_mode=self.boundary_mode,
        )
        self.initial_state = self.grid.clone()
        self.history = []

    def set_cell(self, r: int, c: int, state: int) -> None:
        """Sets a single cell state."""
        self._check_state(state)
        self.grid.set(r, c, state)

    def eval_cell(self, r: int, c: int) -> int:
        """
        Evaluates the next state for the cell at (r, c).
        Directly implements `eval_cell` from the Deliverable 1 sketch:
          - Gets current state and neighbor counts.
          - Checks rules in order.
          - Returns rule.next_state on first match, or preserves current state.
        """
        cell_state = self.grid.get(r, c)
        neighbor_counts = self.grid.get_neighbor_counts(r, c, self.neighborhood)

        for rule in self.rules:
            if rule.matches(cell_state, neighbor_counts):
                return rule.next_state

        # Default fallback: state remains unchanged
        return cell_state

    def step(self) -> Grid:
        """
        Advances the world by one generation.
        Directly implements `step` from the Deliverable 1 sketch:
          - Appends current grid to history.
          - Computes new_grid via eval_cell on every coordinate.
          - Replaces current grid.
        """
        # Save snapshot into history
        self.history.append(self.grid.clone())

        # Construct new generation
        new_cells = [
            [self.eval_cell(r, c) for c in range(self.width)]
            for r in range(self.height)
        ]

        self.grid = Grid(
            height=self.height,
            width=self.width,
            initial_matrix=new_cells,
            boundary_mode=self.boundary_mode,
        )

        return self.grid

    def run(self, steps: int) -> List[Grid]:
        """Runs the simulation for a given number of steps and returns the history."""
        for _ in range(steps):
            self.step()
        return self.history

    def get_generation(self, index: int) -> Grid:
        """
        Retrieves a generation from history.
        Index 0 is initial state, len(history) is the current state.
        """
        if index < 0 or index > len(self.history):
            raise IndexError(f"Generation index {index} out of bounds (0 to {len(self.history)})")
        if index == len(self.history):
            return self.grid
        return self.history[index]

    def reset(self) -> None:
        """Restores the automaton to its initial state."""
        self.grid = self.initial_state.clone()
        self.history = []

    @property
    def current_step(self) -> int:
        return len(self.history)
