import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict

from PySide6.QtCore import QRect, QVariantAnimation, QPoint, QEasingCurve, QAbstractAnimation, QObject
from PySide6.QtGui import QPaintEvent, QPainter, Qt, QResizeEvent, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import QWidget

from CustomScrollBar import CustomScrollBar
from Delegate import Delegate
from models import Style, Item


@dataclass
class Index:
    item: Item
    item_style: Style
    item_id: uuid.UUID


class Flow(Enum):
    TopToBottom = auto()
    LeftToRight = auto()


class DraggableListView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.items_by_id: Dict[uuid.UUID, Index] = dict()
        self.items_list: List[Index] = list()
        self.scroll_bar = CustomScrollBar(self)
        self.scroll_bar.valueChanged.connect(self.scroll_bar_value_changed)
        self.scroll_bar.raise_()
        self.setMouseTracking(True)
        self.animation_map: Dict[int, QVariantAnimation] = dict()
        self.reorder_animation: Optional[QVariantAnimation] = None

        self.current_combobox = None

        self.inner_drag_is_active = False
        self.reorder_is_active = False
        self.inner_drag_start_position = QPoint()
        self.dragged_item_style = None
        self.dragged_item = None
        self.current_shift_value = 0
        self.dragged_pos: float = 0
        self.dragged_item_key = None
        self.dragged_item_row = None
        self.current_drop_row = None
        self.dragged_y_offset: float = 0
        self.current_animated_items = list()

        self.animation = None

        self.colors = ["#ADD8E6", "#90EE90", "#FFFFE0", "#FFC0CB", "#BA55D3", "#87CEFA", "#FFE4E1", "#FFDAB9", "#B0C4DE", "#FFA07A"]

        for i in range(len(self.colors)):
            self.addItem(Item(self.colors[i]))

        self._row_height = 60
        self._row_width = 120

        self.setFlow(Flow.TopToBottom)

        self.delegate = Delegate(self)
        self._spacing = 10

    def spacing(self) -> float:
        return self._spacing

    def setSpacing(self, value) -> None:
        self._spacing = value
        self.update()

    def setDelegate(self, delegate: QObject) -> None:
        self.delegate = delegate
        self.update()

    def setFlow(self, flow: Flow):
        self._flow = flow
        if flow == Flow.TopToBottom:
            self.scroll_bar.setOrientation(Qt.Orientation.Vertical)
        else:
            self.scroll_bar.setOrientation(Qt.Orientation.Horizontal)
        self.update()

    def flow(self) -> Flow:
        return self._flow

    def rowHeight(self) -> int:
        return self.delegate.sizeHint().height()

    def rowWidth(self) -> int:
        return self.delegate.sizeHint().width()

    def scroll_bar_value_changed(self, value) -> None:
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        self.scroll_bar.wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.flow() == Flow.TopToBottom:
            _rect = QRect(0, 0, 8, self.rect().height())
            _rect.moveRight(self.rect().right())
            self.scroll_bar.setGeometry(_rect)
            self.scroll_bar.setRange(0, self.rowHeight() * len(self.items_by_id) - self.height())
        else:
            _rect = QRect(0, 0, self.rect().width(), 8)
            _rect.moveBottom(self.rect().bottom())
            self.scroll_bar.setGeometry(_rect)
            self.scroll_bar.setRange(0, self.rowWidth() * len(self.items_by_id) - self.width())

    def getIndexRect(self, index: int) -> QRect:
        if self.flow() == Flow.TopToBottom:
            x = self.spacing()
            y = index * self.rowHeight() + self.spacing() * index - self.scroll_bar.value()
            w = self.rowWidth()
            h = self.rowHeight() - self.spacing()
        else:
            x = index * self.rowWidth() - self.scroll_bar.value() + self.spacing() * index
            y = self.spacing()
            w = self.rowWidth()
            h = self.rowHeight() - self.spacing()
        return QRect(x, y, w, h)

    def addItem(self, item) -> None:
        item_style = Style(offset=0)
        item_id = uuid.uuid4()
        index = Index(item, item_style, item_id)
        self.items_list.append(index)
        self.items_by_id[item_id] = index
        self.update()

    def indexAt(self, pos: QPoint) -> int:
        if self.flow() == Flow.TopToBottom:
            index = (pos.y() + self.scroll_bar.value()) // self.rowHeight()
        else:
            index = (pos.x() + self.scroll_bar.value()) // self.rowWidth()
        return int(index)

    def rowCount(self) -> int:
        return len(self.items_by_id)

    def isRowValid(self, row: int) -> bool:
        return 0 <= row < self.rowCount()

    def replace_item(self, from_index: int, to_index: int) -> None:
        item_to_be_moved = self.items_by_id.pop(from_index)
        item_style_to_be_moved = self.items_style.pop(from_index)
        self.items_by_id.insert(to_index, item_to_be_moved)
        self.items_style.insert(to_index, item_style_to_be_moved)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.reorder_is_active:
            return
        index = self.indexAt(event.position())
        if not 0 <= index < len(self.items_by_id):
            return
        if event.button() == Qt.LeftButton:
            self.inner_drag_is_active = True
            self.inner_drag_start_position = event.pos()
            self.dragged_item = self.items_list[index].item
            self.dragged_item_style = self.items_list[index].item_style
            self.dragged_item_row = index
            self.current_drop_row = index
            self.current_shift_value = self.dragged_item_row

    def get_shift_value(self, cursor_pos: QPoint) -> float:
        if self.flow() == Flow.TopToBottom:
            y_diff = cursor_pos.y() - self.inner_drag_start_position.y()
            self.dragged_pos = y_diff + self.dragged_item_row * self.rowHeight() - self.scroll_bar.value()
            new_shift_value = int((y_diff + self.rowHeight() // 2) // self.rowHeight())
        else:
            x_diff = cursor_pos.position().x() - self.inner_drag_start_position.x()
            self.dragged_pos = x_diff + self.dragged_item_row * self.rowWidth() - self.scroll_bar.value()
            new_shift_value = int((x_diff + self.rowWidth() // 2) // self.rowWidth())
        return new_shift_value

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.reorder_is_active:
            return
        if self.inner_drag_is_active:
            new_shift_value = self.get_shift_value(event.position())
            new_drop_row = new_shift_value + self.dragged_item_row
            if new_drop_row < 0:
                new_drop_row = 0
            if new_drop_row >= self.rowCount():
                new_drop_row = self.rowCount()-1
            if new_drop_row != self.current_drop_row:
                previous_drop_row = self.current_drop_row
                self.current_drop_row = new_drop_row
                if self.current_drop_row < previous_drop_row:
                    if self.current_drop_row >= self.dragged_item_row:
                        animated_row = self.current_drop_row + 1
                        end_value = 0
                    else:
                        animated_row = self.current_drop_row
                        if self.flow() == Flow.TopToBottom:
                            end_value = self.rowHeight() + self.spacing()
                        else:
                            end_value = self.rowWidth() + self.spacing()
                else:
                    if self.current_drop_row <= self.dragged_item_row:
                        animated_row = self.current_drop_row - 1
                        end_value = 0
                    else:
                        animated_row = self.current_drop_row
                        if self.flow() == Flow.TopToBottom:
                            end_value = -(self.rowHeight() + self.spacing())
                        else:
                            end_value = -(self.rowWidth() + self.spacing())

                self.start_offset_animation(animated_row, end_value)

            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self.reorder_is_active:
            return
        self.inner_drag_is_active = False
        self.reorder_is_active = True
        if self.flow() == Flow.TopToBottom:
            destination = self.getIndexRect(self.current_drop_row).y()
        else:
            destination = self.getIndexRect(self.current_drop_row).x()
        self.reorder_animation = QVariantAnimation(self)
        start_value = float(self.dragged_pos)
        end_value = float(destination)
        self.start_reorder_animation(start_value, end_value)

    def start_offset_animation(self, row: int, end_value: float):
        animation = QVariantAnimation(self)
        animation.setDuration(400)
        animation.setEasingCurve(QEasingCurve.Type.OutSine)
        item_index: Index = self.items_list[row]
        item_id = item_index.item_id
        animation.setStartValue(item_index.item_style.offset)
        animation.setEndValue(end_value)

        def value_changed(new_value):
            self.items_by_id[item_id].item_style.offset = new_value
            self.update()

        animation.valueChanged.connect(value_changed)
        if row in self.animation_map:
            current_animation: QVariantAnimation = self.animation_map[row]
            if current_animation.state() == QAbstractAnimation.Running:
                current_animation.stop()
        self.animation_map[row] = animation
        self.animation = animation
        self.animation.start()

    def start_reorder_animation(self, start_value: float, end_value: float):
        self.reorder_animation.setStartValue(start_value)
        self.reorder_animation.setEndValue(end_value)
        self.reorder_animation.setDuration(400)
        self.reorder_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

        def update_value(new_value: float):
            self.dragged_pos = new_value
            self.update()

        self.reorder_animation.valueChanged.connect(update_value)

        def finished():
            item_to_be_moved = self.items_list.pop(self.dragged_item_row)
            for row in range(len(self.items_list)):
                self.items_list[row].item_style.offset = 0
            self.items_list.insert(self.current_drop_row, item_to_be_moved)

            self.reorder_is_active = False
            self.inner_drag_start_position = QPoint()
            self.dragged_item = None
            self.dragged_item_style = None
            self.dragged_item_row = None
            self.current_drop_row = None
            self.dragged_item_key = None
            self.update()

        self.reorder_animation.finished.connect(finished)
        self.reorder_animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)

        painter.save()
        i = 0
        for i in range(len(self.items_by_id)):
            item = self.items_list[i].item
            item_style = self.items_list[i].item_style
            _rect = self.getIndexRect(i)
            if self.dragged_item_row == i:
                i += 1
                continue
            painter.save()
            if self.flow() == Flow.TopToBottom:
                painter.translate(QPoint(0, item_style.offset))
            else:
                painter.translate(QPoint(item_style.offset, 0))
            self.delegate.paint(painter, _rect, item_style, item)
            painter.restore()
            i += 1
        painter.restore()

        if self.inner_drag_is_active or self.reorder_is_active:
            if self.flow() == Flow.TopToBottom:
                _rect = QRect(self.spacing(), self.dragged_pos,
                              self.rowWidth(), self.rowHeight() - self.spacing())
            else:
                _rect = QRect(self.dragged_pos, self.spacing(),
                              self.rowWidth(), self.rowHeight() - self.spacing())
            self.delegate.paint(painter, _rect, self.dragged_item_style, self.dragged_item)

        painter.end()
