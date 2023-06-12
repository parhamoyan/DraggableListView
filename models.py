from dataclasses import dataclass

from PySide6.QtGui import QColor


@dataclass
class Style:
    offset: float = 0


@dataclass
class Item:
    color: QColor
