from __future__ import annotations
import random
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QPlainTextEdit, QPushButton, QScrollArea, QSlider, QVBoxLayout, QWidget,
)
from PySide6.QtGui import QGuiApplication

from cellab.core.automaton import CellularAutomaton
from cellab.core.presets import create_brians_brain, create_game_of_life, create_seeds
from cellab.core.storage import StorageManager
from cellab import nlp
from .grid_view import GridView

GRID_SIZE = 40
MAX_HISTORY = 200  # keep memory bounded while the simulation runs for a long time
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class GameInfo:
    factory: Callable[..., CellularAutomaton]
    state_names: List[str]
    colors: Dict[int, str]
    random_density: float  # share of cells set to state 1 by "Random"


GAMES: Dict[str, GameInfo] = {
    "Conway's Game of Life": GameInfo(
        create_game_of_life, ["Dead", "Alive"], {0: "#1b1c23", 1: "#7cd992"}, 0.30
    ),
    "Brian's Brain": GameInfo(
        create_brians_brain, ["Off", "Firing", "Dying"], {0: "#1b1c23", 1: "#f2f3f7", 2: "#4f8cff"}, 0.12
    ),
    "Seeds": GameInfo(
        create_seeds, ["Dead", "Alive"], {0: "#1b1c23", 1: "#f4a259"}, 0.05
    ),
}


def _short_name(test: unittest.TestCase) -> str:
    return test.id().rsplit(".", 1)[-1].removeprefix("test_")


class _RecordingResult(unittest.TestResult):
    """Collects one short line per test, e.g. '✔ seeds_automaton'."""

    def __init__(self):
        super().__init__()
        self.lines: List[str] = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.lines.append(f"✔ {_short_name(test)}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.lines.append(f"✘ {_short_name(test)}  (failed)")

    def addError(self, test, err):
        super().addError(test, err)
        self.lines.append(f"✘ {_short_name(test)}  (error)")


def section_label(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("section")
    return label


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CelLab")
        # Open at a comfortable size that still fits small / high-scaling screens
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(min(1180, int(screen.width() * 0.9)), min(800, int(screen.height() * 0.9)))

        self.ca: CellularAutomaton
        self.game: GameInfo
        self.generation = 0
        self.paint_state = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)

        self._build_ui()
        self.load_game(self.game_combo.currentText())

    # ---- layout ---------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget(objectName="central")
        root = QHBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)
        self.setCentralWidget(central)

        # Left: grid card
        grid_card = QFrame(objectName="gridCard")
        grid_layout = QVBoxLayout(grid_card)
        grid_layout.setContentsMargins(14, 14, 14, 12)
        self.grid_view = GridView()
        self.grid_view.cell_pressed.connect(self.on_cell_pressed)
        self.grid_view.cell_dragged.connect(self.on_cell_dragged)
        self.status_label = QLabel(objectName="status")
        grid_layout.addWidget(self.grid_view, 1)
        grid_layout.addWidget(self.status_label)
        root.addWidget(grid_card, 1)

        # Right: control panel. It scrolls when the window is too short to show everything.
        panel = QFrame(objectName="panel")
        panel.setFixedWidth(350)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(1, 1, 1, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)
        content = QWidget(objectName="panelContent")
        side = QVBoxLayout(content)
        side.setContentsMargins(17, 17, 17, 17)
        side.setSpacing(8)
        scroll.setWidget(content)
        panel_layout.addWidget(scroll)
        root.addWidget(panel)

        title = QLabel("CelLab", objectName="title")
        subtitle = QLabel("Cellular automata simulator", objectName="subtitle")
        side.addWidget(title)
        side.addWidget(subtitle)
        side.addSpacing(10)

        # Game selection
        side.addWidget(section_label("Game"))
        self.game_combo = QComboBox()
        self.game_combo.addItems(GAMES.keys())
        self.game_combo.currentTextChanged.connect(self.load_game)
        side.addWidget(self.game_combo)
        self.legend = QLabel(objectName="message")
        self.legend.setTextFormat(Qt.TextFormat.RichText)
        side.addWidget(self.legend)
        side.addSpacing(8)

        # Simulation controls
        side.addWidget(section_label("Simulation"))
        controls = QGridLayout()
        controls.setSpacing(8)
        self.play_button = QPushButton("▶  Play", objectName="primary")
        self.play_button.clicked.connect(self.toggle_play)
        step_button = QPushButton("Step")
        step_button.clicked.connect(self.step)
        random_button = QPushButton("Random")
        random_button.clicked.connect(self.randomize)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear)
        controls.addWidget(self.play_button, 0, 0, 1, 3)
        controls.addWidget(step_button, 1, 0)
        controls.addWidget(random_button, 1, 1)
        controls.addWidget(clear_button, 1, 2)
        side.addLayout(controls)

        # Save / load (uses cellab.core.storage)
        storage_row = QHBoxLayout()
        storage_row.setSpacing(8)
        save_button = QPushButton("💾  Save")
        save_button.clicked.connect(self.save_dialog)
        load_button = QPushButton("📂  Load")
        load_button.clicked.connect(self.load_dialog)
        storage_row.addWidget(save_button)
        storage_row.addWidget(load_button)
        side.addLayout(storage_row)
        self.storage_message = QLabel(objectName="message")
        self.storage_message.setWordWrap(True)
        self.storage_message.hide()
        side.addWidget(self.storage_message)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed", objectName="message"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 30)  # steps per second
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self._update_speed)
        speed_row.addWidget(self.speed_slider, 1)
        side.addLayout(speed_row)
        side.addSpacing(8)

        # Tests
        side.addWidget(section_label("Tests"))
        tests_button = QPushButton("Run tests")
        tests_button.clicked.connect(self.run_tests)
        side.addWidget(tests_button)
        self.test_summary = QLabel("Not run yet", objectName="message")
        side.addWidget(self.test_summary)
        self.test_output = QPlainTextEdit(objectName="testOutput")
        self.test_output.setReadOnly(True)
        self.test_output.setPlaceholderText("Test results appear here")
        self.test_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.test_output.setFixedHeight(120)
        side.addWidget(self.test_output)
        side.addSpacing(10)

        # Natural language rules (for the L13 NLP deliverable)
        side.addWidget(section_label("Rules in natural language"))
        self.nl_input = QPlainTextEdit()
        self.nl_input.setPlaceholderText(
            "e.g. A dead cell with exactly 3 live neighbors becomes alive."
        )
        self.nl_input.setFixedHeight(80)
        side.addWidget(self.nl_input)
        convert_button = QPushButton("Convert to rules")
        convert_button.clicked.connect(self.convert_rules)
        side.addWidget(convert_button)
        self.nl_message = QLabel(objectName="message")
        self.nl_message.setWordWrap(True)
        side.addWidget(self.nl_message)
        side.addStretch(1)  # extra height goes below the controls, not into them

        self._update_speed()

    # ---- simulation -----------------------------------------------------

    def load_game(self, name: str) -> None:
        self.stop()
        self.game = GAMES[name]
        self.ca = self.game.factory(width=GRID_SIZE, height=GRID_SIZE)
        self._update_legend()
        self.nl_message.clear()
        self.randomize()

    def _update_legend(self) -> None:
        self.legend.setText("   ".join(
            f'<span style="color:{self.game.colors[s] if s else "#5a5c68"}">■</span> {n}'
            for s, n in enumerate(self.game.state_names)
        ))

    def randomize(self) -> None:
        density = self.game.random_density
        matrix = [
            [1 if random.random() < density else 0 for _ in range(self.ca.width)]
            for _ in range(self.ca.height)
        ]
        self.ca.set_grid(matrix)
        self.generation = 0
        self.refresh()

    def clear(self) -> None:
        self.ca.set_grid([[0] * self.ca.width for _ in range(self.ca.height)])
        self.generation = 0
        self.refresh()

    def step(self) -> None:
        self.ca.step()
        del self.ca.history[:-MAX_HISTORY]
        self.generation += 1
        self.refresh()

    def toggle_play(self) -> None:
        if self.timer.isActive():
            self.stop()
        else:
            self.timer.start()
            self.play_button.setText("❚❚  Pause")

    def stop(self) -> None:
        self.timer.stop()
        if hasattr(self, "play_button"):
            self.play_button.setText("▶  Play")

    def _update_speed(self) -> None:
        self.timer.setInterval(int(1000 / self.speed_slider.value()))

    def refresh(self) -> None:
        self.grid_view.set_grid(self.ca.grid, self.game.colors)
        counts = "   ·   ".join(
            f"{name}: {self.ca.grid.count_cells_of_type(state)}"
            for state, name in enumerate(self.game.state_names)
        )
        self.status_label.setText(f"Generation {self.generation}   ·   {counts}")

    # ---- save / load ----------------------------------------------------

    def save_dialog(self) -> None:
        self.stop()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save simulation", str(PROJECT_ROOT / "simulation.json"), "Simulation (*.json)"
        )
        if path:
            self.save_to(path)

    def load_dialog(self) -> None:
        self.stop()
        path, _ = QFileDialog.getOpenFileName(
            self, "Load simulation", str(PROJECT_ROOT), "Simulation (*.json)"
        )
        if path:
            self.load_from(path)

    def save_to(self, path: str) -> None:
        # The window trims history while running, so the generation number is saved
        # separately and history is left out (it would make files very large).
        self.ca.experiment_params["generation"] = self.generation
        try:
            StorageManager.save(self.ca, path, include_history=False)
        except OSError as error:
            self._show_storage_message(f"Could not save: {error}", error=True)
            return
        self._show_storage_message(f"Saved to {Path(path).name}")

    def load_from(self, path: str) -> None:
        try:
            ca = StorageManager.load(path)
        except Exception as error:  # bad JSON, missing fields, invalid states, ...
            self._show_storage_message(f"Could not load {Path(path).name}: {error}", error=True)
            return

        self.ca = ca
        self.generation = ca.experiment_params.get("generation", ca.current_step)
        if ca.name in GAMES:
            self.game = GAMES[ca.name]
            self.game_combo.blockSignals(True)  # don't reset the loaded grid
            self.game_combo.setCurrentText(ca.name)
            self.game_combo.blockSignals(False)
        else:
            self.game = self._generic_game(ca.num_states)
        self._update_legend()
        self.refresh()
        self._show_storage_message(
            f"Loaded {Path(path).name}: {ca.name}, {ca.width}×{ca.height}, generation {self.generation}"
        )

    def _generic_game(self, num_states: int) -> GameInfo:
        """Display settings for a saved automaton that isn't one of the presets."""
        palette = ["#1b1c23", "#7cd992", "#4f8cff", "#f4a259", "#f2f3f7", "#c77dff", "#ff6b6b"]
        return GameInfo(
            factory=self.game.factory,
            state_names=[f"State {s}" for s in range(num_states)],
            colors={s: palette[s % len(palette)] for s in range(num_states)},
            random_density=0.2,
        )

    def _show_storage_message(self, text: str, error: bool = False) -> None:
        color = "#ff6b6b" if error else "#a9abb6"
        self.storage_message.setText(f'<span style="color:{color}">{text}</span>')
        self.storage_message.show()

    # ---- painting cells -------------------------------------------------

    def on_cell_pressed(self, r: int, c: int) -> None:
        # Click cycles the cell to its next state; dragging paints that same state
        self.paint_state = (self.ca.grid.get(r, c) + 1) % self.ca.num_states
        self.ca.set_cell(r, c, self.paint_state)
        self.refresh()

    def on_cell_dragged(self, r: int, c: int) -> None:
        self.ca.set_cell(r, c, self.paint_state)
        self.refresh()

    # ---- tests ----------------------------------------------------------

    def run_tests(self) -> None:
        suite = unittest.TestLoader().discover(
            start_dir=str(PROJECT_ROOT / "tests"), top_level_dir=str(PROJECT_ROOT)
        )
        result = _RecordingResult()
        suite.run(result)

        failed = len(result.failures) + len(result.errors)
        if failed == 0:
            self.test_summary.setText(f'<span style="color:#7cd992">✔ All {result.testsRun} tests passed</span>')
        else:
            self.test_summary.setText(
                f'<span style="color:#ff6b6b">✘ {failed} of {result.testsRun} tests failed</span>'
            )
        lines = list(result.lines)
        for test, trace in result.failures + result.errors:
            lines.append(f"\n--- {_short_name(test)} ---\n{trace}")
        self.test_output.setPlainText("\n".join(lines))

    # ---- natural language ----------------------------------------------

    def convert_rules(self) -> None:
        text = self.nl_input.toPlainText().strip()
        if not text:
            self.nl_message.setText("Type a rule first.")
            return
        try:
            rules = nlp.parse_rules(text, self.ca.num_states)
        except NotImplementedError:
            self.nl_message.setText(
                "The NLP parser isn't built yet (planned for L13). Your text is kept."
            )
            return

        try:
            # Rebuilding the automaton checks that the new rules use valid states
            self.ca = CellularAutomaton(
                width=self.ca.width,
                height=self.ca.height,
                num_states=self.ca.num_states,
                rules=rules,
                initial_grid=self.ca.grid,
                boundary_mode=self.ca.boundary_mode,
                neighborhood=self.ca.neighborhood,
                name="Custom rules",
            )
        except ValueError as error:
            self.nl_message.setText(f"Invalid rules: {error}")
            return
        self.nl_message.setText(f"Loaded {len(rules)} rule(s) from your text.")
        self.refresh()
