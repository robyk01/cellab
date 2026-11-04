from __future__ import annotations
from typing import List, Tuple, Dict, Optional
from enum import Enum


class BoundaryMode(str, Enum):
    TOROIDAL = "toroidal"  # Wraps around edges
    FIXED = "fixed"        # Out-of-bounds cells are treated as 0 (dead / default)


class NeighborhoodType(str, Enum):
    MOORE = "moore"              # 8 neighbors (Moore)
    VON_NEUMANN = "von_neumann"  # 4 orthogonal neighbors


class Grid:
    """
    Represents the 2D matrix world state in CelLab.
    """
    def __init__(
        self,
        height: int,
        width: int,
        initial_matrix: Optional[List[List[int]]] = None,
        default_state: int = 0,
        boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
    ):
        self.height = height
        self.width = width
        self.default_state = default_state
        self.boundary_mode = BoundaryMode(boundary_mode)

        if initial_matrix is not None:
            if len(initial_matrix) != height or any(len(row) != width for row in initial_matrix):
                raise ValueError(f"Matrix shape must match height={height}, width={width}")
            self.cells = [list(row) for row in initial_matrix]
        else:
            self.cells = [[default_state for _ in range(width)] for _ in range(height)]

    def get(self, r: int, c: int) -> int:
        """Retrieves cell state according to the configured boundary mode."""
        if self.boundary_mode == BoundaryMode.TOROIDAL:
            return self.cells[r % self.height][c % self.width]
        else:
            if 0 <= r < self.height and 0 <= c < self.width:
                return self.cells[r][c]
            return self.default_state

    def set(self, r: int, c: int, val: int) -> None:
        """Sets cell value inside bounds."""
        if 0 <= r < self.height and 0 <= c < self.width:
            self.cells[r][c] = val
        else:
            raise IndexError(f"Position ({r}, {c}) is out of bounds for grid of size {self.height}x{self.width}")

    def count_neighbors(
        self,
        r: int,
        c: int,
        target_state: int,
        neighborhood: NeighborhoodType = NeighborhoodType.MOORE,
    ) -> int:
        """Counts neighbors of a given state around (r, c)."""
        counts = self.get_neighbor_counts(r, c, neighborhood)
        return counts.get(target_state, 0)

    def get_neighbor_counts(
        self,
        r: int,
        c: int,
        neighborhood: NeighborhoodType = NeighborhoodType.MOORE,
    ) -> Dict[int, int]:
        """
        Returns a dictionary mapping state -> count of neighboring cells.
        Directly implements the neighbor_count logic from the Deliverable 1 sketch.
        """
        counts: Dict[int, int] = {}

        if neighborhood == NeighborhoodType.VON_NEUMANN:
            deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        else:
            # Moore neighborhood: 8 surrounding cells
            deltas = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]

        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            state = self.get(nr, nc)
            counts[state] = counts.get(state, 0) + 1

        return counts

    def count_cells_of_type(self, state: int) -> int:
        """Total number of cells with a specific state across the grid."""
        return sum(row.count(state) for row in self.cells)

    def clone(self) -> Grid:
        """Returns a deep copy of this Grid instance."""
        new_grid = Grid(
            height=self.height,
            width=self.width,
            default_state=self.default_state,
            boundary_mode=self.boundary_mode,
        )
        new_grid.cells = [list(row) for row in self.cells]
        return new_grid

    def to_matrix(self) -> List[List[int]]:
        return [list(row) for row in self.cells]

    def to_tuples(self) -> Tuple[Tuple[int, ...], ...]:
        return tuple(tuple(row) for row in self.cells)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Grid):
            return False
        return (
            self.height == other.height
            and self.width == other.width
            and self.cells == other.cells
        )

    def __hash__(self) -> int:
        return hash(self.to_tuples())

    def to_string(self, state_chars: Optional[Dict[int, str]] = None) -> str:
        """Renders grid as an ASCII string for visualization."""
        mapping = state_chars or {0: ".", 1: "O", 2: "X"}
        lines = []
        for row in self.cells:
            lines.append(" ".join(mapping.get(val, str(val)) for val in row))
        return "\n".join(lines)
