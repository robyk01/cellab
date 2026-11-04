"""Dark theme for the CelLab window (Qt style sheet)."""
from pathlib import Path

ACCENT = "#4f8cff"
ARROW_ICON = (Path(__file__).parent / "arrow_down.svg").as_posix()

STYLE_SHEET = f"""
QWidget {{
    color: #e6e6eb;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
}}
QWidget#central {{ background: #16171d; }}
QFrame#panel, QFrame#gridCard {{
    background: #1f2029;
    border: 1px solid #2a2c37;
    border-radius: 12px;
}}
QLabel {{ background: transparent; }}
QLabel#title {{ font-size: 17pt; font-weight: 600; }}
QLabel#subtitle {{ color: #8b8d98; }}
QLabel#section {{ color: #8b8d98; font-size: 8pt; font-weight: 600; }}
QLabel#status {{ color: #a9abb6; }}
QLabel#message {{ color: #a9abb6; }}

QPushButton {{
    background: #2b2d38;
    border: 1px solid #3a3c4a;
    border-radius: 8px;
    padding: 7px 12px;
}}
QPushButton:hover {{ background: #343745; }}
QPushButton:pressed {{ background: #252731; }}
QPushButton#primary {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
    color: white;
    font-weight: 600;
}}
QPushButton#primary:hover {{ background: #6699ff; }}
QPushButton#primary:pressed {{ background: #3f7aec; }}

QComboBox {{
    background: #2b2d38;
    border: 1px solid #3a3c4a;
    border-radius: 8px;
    padding: 6px 10px;
}}
QComboBox:hover {{ border-color: #4a4d5e; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{ image: url("{ARROW_ICON}"); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{
    background: #2b2d38;
    border: 1px solid #3a3c4a;
    selection-background-color: {ACCENT};
    outline: none;
}}

QPlainTextEdit {{
    background: #15161c;
    border: 1px solid #3a3c4a;
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {ACCENT};
}}
QPlainTextEdit:focus, QComboBox:focus {{ border-color: {ACCENT}; }}
QPlainTextEdit#testOutput {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 9pt;
}}

QScrollArea, QWidget#panelContent {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px 4px; }}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: #3a3c4a;
    border-radius: 3px;
    min-height: 28px;
    min-width: 28px;
}}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{ background: #4a4d5e; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
QAbstractScrollArea::corner {{ background: transparent; }}

QSlider::groove:horizontal {{ height: 4px; background: #3a3c4a; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: white;
    width: 14px; height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
"""
