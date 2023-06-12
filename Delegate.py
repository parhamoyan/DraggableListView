from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QBrush, Qt
from PySide6.QtWidgets import QWidget

from models import Item


class Delegate:
    def __init__(self, parent: QWidget) -> None:
        self._parent: QWidget = parent

    def parent(self) -> QWidget:
        return self._parent

    def sizeHint(self) -> QSize:
        return QSize(self.parent().width(), 120)

    def paint(self, painter: QPainter, option_rect, item_style, item: Item) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(item.color))
        painter.drawRect(option_rect)

