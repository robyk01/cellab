from __future__ import annotations
from typing import Dict, Optional, Tuple

from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QMouseEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

from cellab.core.grid import Grid


class GridView(QWidget):
    """
    Draws a Grid as colored squares, scaled to fit the widget.
    Clicking a cell emits `cell_pressed`; dragging over more cells emits `cell_dragged`.
    """

    cell_pressed = Signal(int, int)  # row, col
    cell_dragged = Signal(int, int)  # row, col

    BACKGROUND = QColor("#1f2029")  # same as the card around the grid
    LINE_COLOR = QColor(255, 255, 255, 18)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._grid: Optional[Grid] = None
        self._colors: Dict[int, QColor] = {}
        self._last_cell: Optional[Tuple[int, int]] = None
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_grid(self, grid: Grid, colors: Dict[int, str]) -> None:
        self._grid = grid
        self._colors = {state: QColor(color) for state, color in colors.items()}
        self.update()

    # ---- geometry -------------------------------------------------------

    def _layout(self) -> Tuple[float, float, float]:
        """Returns (cell_size, x_offset, y_offset) so the grid is square and centered."""
        g = self._grid
        cell = min(self.width() / g.width, self.height() / g.height)
        x0 = (self.width() - cell * g.width) / 2
        y0 = (self.height() - cell * g.height) / 2
        return cell, x0, y0

    def _cell_at(self, pos: QPointF) -> Optional[Tuple[int, int]]:
        if self._grid is None:
            return None
        cell, x0, y0 = self._layout()
        c = int((pos.x() - x0) // cell)
        r = int((pos.y() - y0) // cell)
        if 0 <= r < self._grid.height and 0 <= c < self._grid.width:
            return r, c
        return None

    # ---- drawing --------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.BACKGROUND)
        if self._grid is None:
            return

        g = self._grid
        cell, x0, y0 = self._layout()
        painter.fillRect(QRectF(x0, y0, cell * g.width, cell * g.height), self._colors.get(0, self.BACKGROUND))

        # Draw non-zero cells with a small gap so they read as tiles
        gap = 1.0 if cell >= 6 else 0.0
        for r, row in enumerate(g.cells):
            for c, state in enumerate(row):
                if state:
                    painter.fillRect(
                        QRectF(x0 + c * cell + gap / 2, y0 + r * cell + gap / 2, cell - gap, cell - gap),
                        self._colors.get(state, QColor("#ff00ff")),
                    )

        if cell >= 6:
            painter.setPen(QPen(self.LINE_COLOR, 1))
            for c in range(g.width + 1):
                x = x0 + c * cell
                painter.drawLine(QPointF(x, y0), QPointF(x, y0 + cell * g.height))
            for r in range(g.height + 1):
                y = y0 + r * cell
                painter.drawLine(QPointF(x0, y), QPointF(x0 + cell * g.width, y))

    # ---- mouse ----------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        hit = self._cell_at(event.position())
        self._last_cell = hit
        if hit:
            self.cell_pressed.emit(*hit)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not event.buttons() & Qt.MouseButton.LeftButton:
            return
        hit = self._cell_at(event.position())
        if hit and hit != self._last_cell:
            self._last_cell = hit
            self.cell_dragged.emit(*hit)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._last_cell = None
