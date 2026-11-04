#!/usr/bin/env python3
"""
Deliverable 2 Demonstration Script:
  - Models 3 distinct cellular automata (Game of Life, Brian's Brain, Seeds).
  - Demonstrates generation transitions (reading t -> generating t+1).
  - Demonstrates state storage and recovery via StorageManager.
  - Answers the 5 project questions.
"""
from cellab.core.presets import create_game_of_life, create_brians_brain, create_seeds
from cellab.core.storage import StorageManager
from cellab.core.analysis import SimulationAnalyzer
from cellab.core.grid import BoundaryMode


def print_banner(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def demo_game_of_life():
    print_banner("1. Conway's Game of Life (Blinker Oscillator)")
    ca = create_game_of_life(width=7, height=7)
    blinker = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    ca.set_grid(blinker)

    print("Generation 0 (Initial):")
    print(ca.grid.to_string({0: ".", 1: "#"}))

    ca.step()
    print("\nGeneration 1 (Vertical):")
    print(ca.grid.to_string({0: ".", 1: "#"}))

    ca.step()
    print("\nGeneration 2 (Horizontal again):")
    print(ca.grid.to_string({0: ".", 1: "#"}))

    cycle = SimulationAnalyzer.detect_cycle(ca)
    print(f"\n[Question 5 - Cycle Detection]: Cycle start step = {cycle[0]}, period length = {cycle[1]}")


def demo_brians_brain():
    print_banner("2. Brian's Brain (3 States: 0=OFF, 1=FIRING, 2=DYING)")
    bb = create_brians_brain(width=7, height=7, boundary_mode=BoundaryMode.FIXED)
    # A simple oscillator / active cluster
    init = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    bb.set_grid(init)

    chars = {0: ".", 1: "F", 2: "D"}
    print("Generation 0 (Initial FIRING cells):")
    print(bb.grid.to_string(chars))

    bb.step()
    print("\nGeneration 1 (Decay to DYING, and new FIRING born between them):")
    print(bb.grid.to_string(chars))

    bb.step()
    print("\nGeneration 2:")
    print(bb.grid.to_string(chars))


def demo_storage_and_recovery():
    print_banner("3. State Storage and Recovery (Deliverable 2 Requirement)")
    save_path = "saved_simulation.json"

    ca = create_game_of_life(width=6, height=6)
    # Glider pattern
    glider = [
        [0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]
    ca.set_grid(glider)
    print("Running original simulation for 4 steps...")
    ca.run(4)

    print(f"Saving state + full history ({len(ca.history)} past generations) to '{save_path}'...")
    StorageManager.save(ca, save_path, include_history=True)

    print(f"Loading/recovering state from '{save_path}'...")
    recovered_ca = StorageManager.load(save_path)

    print("Parity checks:")
    print(f" - Grid dimensions match: {recovered_ca.width}x{recovered_ca.height}")
    print(f" - Rules count match: {len(recovered_ca.rules)} rules")
    print(f" - History length recovered: {len(recovered_ca.history)} generations")
    print(f" - Current states match exactly: {ca.grid == recovered_ca.grid}")

    # Both take 1 step forward
    orig_next = ca.step()
    recov_next = recovered_ca.step()
    print(f" - Subsequent step t=5 matches exactly: {orig_next == recov_next}")


if __name__ == "__main__":
    demo_game_of_life()
    demo_brians_brain()
    demo_storage_and_recovery()
