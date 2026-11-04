"""PySide6 front end for CelLab. Kept separate from `cellab.core`, which has no GUI dependencies."""
import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication
    from .main_window import MainWindow
    from .style import STYLE_SHEET

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    window.show()
    return app.exec()
