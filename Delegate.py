from PySide6.QtCore import QSize, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, Qt, QFontMetrics, QFont, QPen, QPixmap, QPainterPath
from PySide6.QtWidgets import QWidget

from Icon import Icon
from models import Item


class Delegate:
    def __init__(self, parent: QWidget) -> None:
        self._parent: QWidget = parent

    def paint(self, painter: QPainter, option_rect, item_style, item: Item) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(item.color))
        painter.drawRect(option_rect)

