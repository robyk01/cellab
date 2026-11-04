"""
Natural-language to rules parser (planned for the L13 NLP deliverable).

The GUI already calls `parse_rules`, so implementing this function is all
that is needed to make the "Convert to rules" button work.
"""
from __future__ import annotations
from typing import List
from .core.rule import Rule


def parse_rules(text: str, num_states: int) -> List[Rule]:
    """
    Turns a natural-language description into a list of Rules, e.g.
    "A dead cell with exactly 3 live neighbors becomes alive."
    ->  Rule(current_state=0, next_state=1, target_neighbor_state=1, min_count=3, max_count=3)
    """
    raise NotImplementedError("The NLP rule parser will be added in the L13 deliverable.")
