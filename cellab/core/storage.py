from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Union
from .rule import Rule
from .grid import Grid, BoundaryMode, NeighborhoodType
from .automaton import CellularAutomaton


class StorageManager:
    """
    Handles state storage and recovery for Deliverable 2.
    Allows persisting the entire simulation state (world, rules, experiment parameters,
    and history) to JSON and reloading it completely.
    """

    @staticmethod
    def to_dict(automaton: CellularAutomaton, include_history: bool = True) -> Dict[str, Any]:
        """Serializes an automaton to a Python dictionary."""
        data: Dict[str, Any] = {
            "version": "1.0",
            "name": automaton.name,
            "width": automaton.width,
            "height": automaton.height,
            "num_states": automaton.num_states,
            "boundary_mode": automaton.boundary_mode.value,
            "neighborhood": automaton.neighborhood.value,
            "experiment_params": automaton.experiment_params,
            "current_state": automaton.grid.to_matrix(),
            "initial_state": automaton.initial_state.to_matrix(),
            "rules": [rule.to_dict() for rule in automaton.rules],
        }

        if include_history:
            data["history"] = [grid.to_matrix() for grid in automaton.history]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CellularAutomaton:
        """Reconstructs an automaton from a dictionary."""
        rules = [Rule.from_dict(r) for r in data.get("rules", [])]
        boundary_mode = BoundaryMode(data.get("boundary_mode", "toroidal"))
        neighborhood = NeighborhoodType(data.get("neighborhood", "moore"))

        grid = Grid(
            height=data["height"],
            width=data["width"],
            initial_matrix=data["current_state"],
            boundary_mode=boundary_mode,
        )

        automaton = CellularAutomaton(
            width=data["width"],
            height=data["height"],
            num_states=data["num_states"],
            rules=rules,
            initial_grid=grid,
            boundary_mode=boundary_mode,
            neighborhood=neighborhood,
            name=data.get("name", "Restored Automaton"),
            experiment_params=data.get("experiment_params", {}),
        )

        if "initial_state" in data:
            automaton.initial_state = Grid(
                height=data["height"],
                width=data["width"],
                initial_matrix=data["initial_state"],
                boundary_mode=boundary_mode,
            )

        if "history" in data:
            automaton.history = [
                Grid(
                    height=data["height"],
                    width=data["width"],
                    initial_matrix=hist_matrix,
                    boundary_mode=boundary_mode,
                )
                for hist_matrix in data["history"]
            ]

        return automaton

    @classmethod
    def save(cls, automaton: CellularAutomaton, filepath: Union[str, Path], include_history: bool = True) -> None:
        """Saves automaton to a JSON file on disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = cls.to_dict(automaton, include_history=include_history)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> CellularAutomaton:
        """Loads and recovers automaton from a JSON file on disk."""
        path = Path(filepath)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
