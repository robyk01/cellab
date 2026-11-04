from __future__ import annotations
from typing import Optional, List
from .rule import Rule
from .grid import BoundaryMode, NeighborhoodType
from .automaton import CellularAutomaton


def create_game_of_life(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """
    Factory for Conway's Game of Life:
      - 2 States: 0 (Dead), 1 (Alive)
      - B3/S23:
        * Birth: Dead cell with exactly 3 live neighbors becomes Alive.
        * Survival: Live cell with 2 or 3 live neighbors stays Alive.
        * Underpopulation/Overpopulation: Live cell with < 2 or > 3 live neighbors dies.
    """
    rules = [
        # Birth: 0 -> 1 if 3 live neighbors
        Rule(
            current_state=0,
            next_state=1,
            target_neighbor_state=1,
            min_count=3,
            max_count=3,
            description="Birth: 3 live neighbors",
        ),
        # Survival: 1 -> 1 if 2 or 3 live neighbors
        Rule(
            current_state=1,
            next_state=1,
            target_neighbor_state=1,
            min_count=2,
            max_count=3,
            description="Survival: 2 or 3 live neighbors",
        ),
        # Underpopulation: 1 -> 0 if 0 or 1 live neighbors
        Rule(
            current_state=1,
            next_state=0,
            target_neighbor_state=1,
            min_count=0,
            max_count=1,
            description="Underpopulation: < 2 live neighbors",
        ),
        # Overpopulation: 1 -> 0 if 4 to 8 live neighbors
        Rule(
            current_state=1,
            next_state=0,
            target_neighbor_state=1,
            min_count=4,
            max_count=8,
            description="Overpopulation: > 3 live neighbors",
        ),
    ]

    ca = CellularAutomaton(
        width=width,
        height=height,
        num_states=2,
        rules=rules,
        boundary_mode=boundary_mode,
        neighborhood=NeighborhoodType.MOORE,
        name="Conway's Game of Life",
        experiment_params={"rule_notation": "B3/S23"},
    )

    if initial_matrix is not None:
        ca.set_grid(initial_matrix)

    return ca


def create_brians_brain(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """
    Factory for Brian's Brain:
      - 3 States: 0 (OFF), 1 (FIRING), 2 (DYING)
      - Rules:
        * OFF cell becomes FIRING if exactly 2 neighbors are FIRING.
        * FIRING cell unconditionally becomes DYING.
        * DYING cell unconditionally becomes OFF.
    """
    rules = [
        # OFF -> FIRING if exactly 2 FIRING neighbors
        Rule(
            current_state=0,
            next_state=1,
            target_neighbor_state=1,
            min_count=2,
            max_count=2,
            description="Birth: OFF cell with 2 FIRING neighbors becomes FIRING",
        ),
        # FIRING -> DYING unconditionally
        Rule(
            current_state=1,
            next_state=2,
            target_neighbor_state=None,
            description="Decay: FIRING cell unconditionally transitions to DYING",
        ),
        # DYING -> OFF unconditionally
        Rule(
            current_state=2,
            next_state=0,
            target_neighbor_state=None,
            description="Reset: DYING cell unconditionally transitions to OFF",
        ),
    ]

    ca = CellularAutomaton(
        width=width,
        height=height,
        num_states=3,
        rules=rules,
        boundary_mode=boundary_mode,
        neighborhood=NeighborhoodType.MOORE,
        name="Brian's Brain",
        experiment_params={"rule_notation": "B2/S/3-state"},
    )

    if initial_matrix is not None:
        ca.set_grid(initial_matrix)

    return ca


def create_seeds(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """
    Factory for Seeds (B2/S):
      - 2 States: 0 (Dead), 1 (Alive)
      - Rules:
        * Birth: Dead cell becomes Alive if exactly 2 neighbors are alive.
        * All alive cells die in the next step (no survival).
    """
    rules = [
        # Birth: 0 -> 1 if exactly 2 live neighbors
        Rule(
            current_state=0,
            next_state=1,
            target_neighbor_state=1,
            min_count=2,
            max_count=2,
            description="Birth: exactly 2 live neighbors",
        ),
        # Alive cells unconditionally die
        Rule(
            current_state=1,
            next_state=0,
            target_neighbor_state=None,
            description="Death: all alive cells die",
        ),
    ]

    ca = CellularAutomaton(
        width=width,
        height=height,
        num_states=2,
        rules=rules,
        boundary_mode=boundary_mode,
        neighborhood=NeighborhoodType.MOORE,
        name="Seeds",
        experiment_params={"rule_notation": "B2/S"},
    )

    if initial_matrix is not None:
        ca.set_grid(initial_matrix)

    return ca
