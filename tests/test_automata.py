import unittest
import tempfile
import os
from pathlib import Path

from cellab.core.rule import Rule
from cellab.core.grid import Grid, BoundaryMode, NeighborhoodType
from cellab.core.automaton import CellularAutomaton
from cellab.core.storage import StorageManager
from cellab.core.presets import create_game_of_life, create_brians_brain, create_seeds
from cellab.core.analysis import SimulationAnalyzer


class TestCelLabDeliverable2(unittest.TestCase):
    """
    Test suite fulfilling Deliverable 2 requirements:
      1. World state & rules evaluation (transition t -> t+1)
      2. Testing across 3 different automata (Game of Life, Brian's Brain, Seeds)
      3. State storage and recovery (JSON serialization & reload)
      4. Answering core questions (stability, cycle detection, cell counts)
    """

    def test_game_of_life_blinker_oscillator(self):
        """
        Tests Game of Life with a Blinker (period 2 oscillator).
        Initial (horizontal):
          . . . . .
          . . . . .
          . 1 1 1 .
          . . . . .
          . . . . .
        Generation 1 (vertical):
          . . . . .
          . . 1 . .
          . . 1 . .
          . . 1 . .
          . . . . .
        Generation 2 (horizontal again):
        """
        gol = create_game_of_life(width=5, height=5)
        blinker = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        gol.set_grid(blinker)

        # Step 1: should become vertical
        g1 = gol.step()
        expected_g1 = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        self.assertEqual(g1.to_matrix(), expected_g1)

        # Step 2: should oscillate back to horizontal
        g2 = gol.step()
        self.assertEqual(g2.to_matrix(), blinker)

        # Test cycle detection on Blinker
        cycle_info = SimulationAnalyzer.detect_cycle(gol)
        self.assertIsNotNone(cycle_info)
        start_step, cycle_len = cycle_info
        self.assertEqual(cycle_len, 2)

    def test_game_of_life_block_still_life(self):
        """
        Tests Game of Life with a 2x2 Block (Still Life).
        Must remain unchanged every generation.
        """
        gol = create_game_of_life(width=4, height=4)
        block = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ]
        gol.set_grid(block)

        # Step forward
        g1 = gol.step()
        self.assertEqual(g1.to_matrix(), block)

        # Check stability question
        stable_step = SimulationAnalyzer.reaches_stable_state(gol, max_steps=10)
        self.assertIsNotNone(stable_step)

    def test_brians_brain_transitions(self):
        """
        Tests Brian's Brain:
          - OFF (0) with 2 FIRING (1) neighbors -> FIRING (1)
          - FIRING (1) -> DYING (2) unconditionally
          - DYING (2) -> OFF (0) unconditionally
        """
        bb = create_brians_brain(width=3, height=3, boundary_mode=BoundaryMode.FIXED)
        # Place two FIRING cells around center (1, 1)
        initial = [
            [1, 0, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]
        bb.set_grid(initial)

        # Step 1:
        # (0, 0) FIRING -> DYING (2)
        # (0, 2) FIRING -> DYING (2)
        # (0, 1) had 2 firing neighbors -> becomes FIRING (1)
        # (1, 1) had 2 firing neighbors -> becomes FIRING (1)
        g1 = bb.step()
        self.assertEqual(g1.get(0, 0), 2)  # FIRING -> DYING
        self.assertEqual(g1.get(0, 2), 2)  # FIRING -> DYING
        self.assertEqual(g1.get(0, 1), 1)  # OFF -> FIRING (2 firing neighbors)
        self.assertEqual(g1.get(1, 1), 1)  # OFF -> FIRING (2 firing neighbors)

        # Step 2:
        # Dying cells (0, 0) and (0, 2) become OFF (0)
        # Firing cells (0, 1) and (1, 1) become DYING (2)
        g2 = bb.step()
        self.assertEqual(g2.get(0, 0), 0)  # DYING -> OFF
        self.assertEqual(g2.get(0, 2), 0)  # DYING -> OFF
        self.assertEqual(g2.get(0, 1), 2)  # FIRING -> DYING
        self.assertEqual(g2.get(1, 1), 2)  # FIRING -> DYING

    def test_seeds_automaton(self):
        """
        Tests Seeds (B2/S):
          - Dead (0) + 2 live neighbors -> Alive (1)
          - All Alive (1) cells die in next step -> Dead (0)
        """
        seeds = create_seeds(width=3, height=3, boundary_mode=BoundaryMode.FIXED)
        initial = [
            [1, 0, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]
        seeds.set_grid(initial)

        # Step 1: Both original alive cells die; cells with 2 neighbors are born
        g1 = seeds.step()
        self.assertEqual(g1.get(0, 0), 0)  # Alive dies
        self.assertEqual(g1.get(0, 2), 0)  # Alive dies
        self.assertEqual(g1.get(0, 1), 1)  # Dead with 2 neighbors born
        self.assertEqual(g1.get(1, 1), 1)  # Dead with 2 neighbors born

    def test_state_storage_and_recovery(self):
        """
        Tests Deliverable 2 State Storage and Recovery:
          - Run simulation for 3 steps
          - Save state, history, rules, and parameters to a JSON file
          - Recover automaton from the file
          - Ensure complete parity and ability to continue simulation
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_sim.json"

            original_ca = create_game_of_life(width=5, height=5)
            blinker = [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ]
            original_ca.set_grid(blinker)
            original_ca.run(3)

            # Save state
            StorageManager.save(original_ca, filepath, include_history=True)
            self.assertTrue(filepath.exists())

            # Load / recover state
            recovered_ca = StorageManager.load(filepath)

            # Check properties
            self.assertEqual(recovered_ca.width, original_ca.width)
            self.assertEqual(recovered_ca.height, original_ca.height)
            self.assertEqual(recovered_ca.num_states, original_ca.num_states)
            self.assertEqual(len(recovered_ca.rules), len(original_ca.rules))
            self.assertEqual(recovered_ca.grid.to_matrix(), original_ca.grid.to_matrix())
            self.assertEqual(len(recovered_ca.history), 3)

            # Both should produce the exact same next step
            step_orig = original_ca.step().to_matrix()
            step_recov = recovered_ca.step().to_matrix()
            self.assertEqual(step_orig, step_recov)

    def test_simulation_questions(self):
        """
        Tests the questions engine:
          - State after N steps
          - Counting cells of type X
          - Subgrid pattern detection
        """
        gol = create_game_of_life(width=5, height=5)
        blinker = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        gol.set_grid(blinker)

        # Question 4: Count cells of type 1 at step 4
        live_count = SimulationAnalyzer.count_cells_of_type(gol, cell_type=1, n=4)
        self.assertEqual(live_count, 3)

        # Question 3: Does pattern occur?
        pattern = [
            [1],
            [1],
            [1],
        ]
        found_at = SimulationAnalyzer.pattern_occurs(gol, pattern, max_steps=5)
        self.assertIsNotNone(found_at)


if __name__ == "__main__":
    unittest.main()
