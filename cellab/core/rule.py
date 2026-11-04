from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Rule:
    """
    Represents a cellular automaton state transition rule.
    Directly corresponds to the L3 Deliverable 1 sketch:
      current_state: state the cell must currently have
      next_state: state the cell transitions into if condition is met
      target_neighbor_state: state of neighbors being counted (None if transition doesn't depend on neighbors)
      min_count: minimum matching neighbors required (inclusive)
      max_count: maximum matching neighbors allowed (inclusive)
    """
    current_state: int
    next_state: int
    target_neighbor_state: Optional[int] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    description: Optional[str] = None

    def matches(self, cell_state: int, neighbor_counts: Dict[int, int]) -> bool:
        """
        Evaluates whether this rule applies to a cell with `cell_state`
        and a mapping of `neighbor_state -> count`.
        """
        # Rule only applies if the cell's current state matches
        if cell_state != self.current_state:
            return False

        # If rule does not depend on neighbors (unconditional transition, e.g. FIRING -> DYING)
        if self.target_neighbor_state is None:
            return True

        # Check neighbor threshold
        count = neighbor_counts.get(self.target_neighbor_state, 0)
        min_c = self.min_count if self.min_count is not None else 0
        max_c = self.max_count if self.max_count is not None else 8

        return min_c <= count <= max_c

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "next_state": self.next_state,
            "target_neighbor_state": self.target_neighbor_state,
            "min_count": self.min_count,
            "max_count": self.max_count,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Rule:
        return cls(
            current_state=data["current_state"],
            next_state=data["next_state"],
            target_neighbor_state=data.get("target_neighbor_state"),
            min_count=data.get("min_count"),
            max_count=data.get("max_count"),
            description=data.get("description"),
        )
