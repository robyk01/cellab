"""
Preset automata. The rules are NOT written here: each game is a JSON file in
`cellab/rules/`. To add a new game, add a new JSON file there with the same format.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from .rule import Rule
from .grid import BoundaryMode, NeighborhoodType
from .automaton import CellularAutomaton

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"


@dataclass
class Preset:
    """One game, as read from its JSON rule file."""
    key: str                   # file name without ".json", e.g. "game_of_life"
    name: str                  # display name, e.g. "Conway's Game of Life"
    num_states: int
    state_names: List[str]
    neighborhood: NeighborhoodType
    rule_notation: Optional[str]
    rules: List[Rule]


def load_preset(source: Union[str, Path]) -> Preset:
    """
    Reads a rule file. `source` is either a preset key ("game_of_life")
    or a path to any .json rule file.
    """
    path = Path(source)
    if path.suffix != ".json":
        path = RULES_DIR / f"{source}.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for field in ("name", "num_states", "rules"):
        if field not in data:
            raise ValueError(f"{path.name}: missing required field '{field}'")

    num_states = data["num_states"]
    state_names = data.get("state_names") or [f"State {s}" for s in range(num_states)]
    if len(state_names) != num_states:
        raise ValueError(
            f"{path.name}: 'state_names' has {len(state_names)} names but 'num_states' is {num_states}"
        )

    return Preset(
        key=path.stem,
        name=data["name"],
        num_states=num_states,
        state_names=state_names,
        neighborhood=NeighborhoodType(data.get("neighborhood", "moore")),
        rule_notation=data.get("rule_notation"),
        rules=[Rule.from_dict(r) for r in data["rules"]],
    )


def list_presets() -> List[Preset]:
    """All games found in the rules folder, sorted by file name."""
    return [load_preset(path) for path in sorted(RULES_DIR.glob("*.json"))]


def create_automaton(
    preset: Union[str, Path, Preset],
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """Builds an automaton from a preset key, a rule file path, or a loaded Preset."""
    if not isinstance(preset, Preset):
        preset = load_preset(preset)

    ca = CellularAutomaton(
        width=width,
        height=height,
        num_states=preset.num_states,
        rules=list(preset.rules),
        boundary_mode=boundary_mode,
        neighborhood=preset.neighborhood,
        name=preset.name,
        experiment_params={"rule_notation": preset.rule_notation} if preset.rule_notation else {},
    )
    if initial_matrix is not None:
        ca.set_grid(initial_matrix)
    return ca


# Shortcuts for the three built-in games (rules in cellab/rules/*.json)

def create_game_of_life(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """Conway's Game of Life (B3/S23), from rules/game_of_life.json."""
    return create_automaton("game_of_life", width, height, initial_matrix, boundary_mode)


def create_brians_brain(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """Brian's Brain (OFF / FIRING / DYING), from rules/brians_brain.json."""
    return create_automaton("brians_brain", width, height, initial_matrix, boundary_mode)


def create_seeds(
    width: int = 20,
    height: int = 20,
    initial_matrix: Optional[List[List[int]]] = None,
    boundary_mode: BoundaryMode = BoundaryMode.TOROIDAL,
) -> CellularAutomaton:
    """Seeds (B2/S), from rules/seeds.json."""
    return create_automaton("seeds", width, height, initial_matrix, boundary_mode)
