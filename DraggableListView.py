import uuid
from dataclasses import dataclass
from typing import Optional, List, Dict

from PySide6.QtCore import QRect, QVariantAnimation, QPoint, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPaintEvent, QPainter, Qt, QResizeEvent, QWheelEvent, QMouseEvent, QColor
from PySide6.QtWidgets import QWidget

from CustomScrollBar import CustomScrollBar
from Delegate import Delegate
from models import Style, Item


@dataclass
class Index:
    item: Item
    item_style: Style
    item_id: uuid.UUID


class DraggableListView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.items_by_id: Dict[uuid.UUID, Index] = dict()
        self.items_list: List[Index] = list()
        self.scroll_bar = CustomScrollBar(self)
        self.scroll_bar.valueChanged.connect(self.scroll_bar_value_changed)
        self.scroll_bar.raise_()
        self.setMouseTracking(True)
        self.animation_map = dict()

        self.current_combobox = None

        self.inner_drag_is_active = False
        self.reorder_is_active = False
        self.inner_drag_start_position = QPoint()
        self.dragged_item_style = None
        self.dragged_item = None
        self.current_shift_value = 0
        self.dragged_y_pos: float = 0
        self.dragged_item_key = None
        self.dragged_item_row = None
        self.current_drop_row = None
        self.dragged_y_offset: float = 0
        self.current_animated_items = list()

        self.colors = [QColor("#071E22"), QColor("#1D7874"), QColor("#679289"), QColor("#F4C095"), QColor("#EE2E31")]
        count = 5
        for i in range(count):
            self.addItem(i)

        self.setAcceptDrops(True)

    def scroll_bar_value_changed(self, value) -> None:
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        self.scroll_bar.wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        _rect = QRect(0, 0, 8, self.rect().height())
        _rect.moveRight(self.rect().right())
        self.scroll_bar.setGeometry(_rect)
        self.scroll_bar.setRange(0, 60 * len(self.items_by_id) - self.height())

    def getIndexRect(self, index: int) -> QRect:
        _rect = QRect(0, index * 60 - self.scroll_bar.value(), self.width(), 60)
        return _rect

    def addItem(self, i) -> None:
        item = Item(self.colors[i])
        item_style = Style(y_offset=0)
        item_id = uuid.uuid4()
        index = Index(item, item_style, item_id)
        self.items_list.append(index)
        self.items_by_id[item_id] = index
        self.update()

    def indexAt(self, pos: QPoint) -> int:
        index = (pos.y() + self.scroll_bar.value()) // 60
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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.inner_drag_is_active:
            y_diff = event.position().y() - self.inner_drag_start_position.y()
            self.dragged_y_pos = y_diff + self.dragged_item_row * 60
            new_shift_value = int((y_diff+30)//60)
            new_drop_row = new_shift_value + self.dragged_item_row
            if new_drop_row < 0:
                new_drop_row = 0
            if new_drop_row >= self.rowCount():
                new_drop_row = self.rowCount()-1
            if new_drop_row != self.current_drop_row:
                previous_drop_row = self.current_drop_row
                self.current_drop_row = new_drop_row
                item_index: Index = self.items_list[self.current_drop_row]
                item_id = item_index.item_id
                self.animation = QVariantAnimation(self)
                self.animation.setStartValue(item_index.item_style.y_offset)
                self.animation.setDuration(200)

                if self.current_drop_row < previous_drop_row:
                    if self.current_drop_row >= self.dragged_item_row:
                        row = self.current_drop_row + 1
                        item_index: Index = self.items_list[row]
                        item_id = item_index.item_id
                        self.animation.setStartValue(item_index.item_style.y_offset)
                        self.animation.setEndValue(0)
                    else:
                        row = self.current_drop_row
                        item_index: Index = self.items_list[row]
                        item_id = item_index.item_id
                        self.animation.setStartValue(item_index.item_style.y_offset)
                        self.animation.setEndValue(60)
                else:
                    if self.current_drop_row <= self.dragged_item_row:
                        row = self.current_drop_row - 1
                        item_index: Index = self.items_list[row]
                        item_id = item_index.item_id
                        self.animation.setStartValue(item_index.item_style.y_offset)
                        self.animation.setEndValue(0)
                    else:
                        row = self.current_drop_row
                        item_index: Index = self.items_list[row]
                        item_id = item_index.item_id
                        self.animation.setStartValue(item_index.item_style.y_offset)
                        self.animation.setEndValue(-60)

                def value_changed(new_value):
                    self.items_by_id[item_id].item_style.y_offset = new_value
                    self.update()
                self.animation.valueChanged.connect(value_changed)
                self.animation.start()

            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        destination_y = self.getIndexRect(self.current_drop_row).y()
        self.reorder_animation = QVariantAnimation(self)
        start_value = float(self.dragged_y_pos)
        end_value = float(destination_y)
        self.reorder_animation.setStartValue(start_value)
        self.reorder_animation.setEndValue(end_value)
        self.reorder_animation.setDuration(100)
        self.reorder_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

        def update_value(new_value: float):
            self.dragged_y_pos = new_value
            self.update()

        self.reorder_animation.valueChanged.connect(update_value)

        def finished():
            item_to_be_moved = self.items_list.pop(self.dragged_item_row)
            for row in range(len(self.items_list)):
                self.items_list[row].item_style.y_offset = 0
            self.items_list.insert(self.current_drop_row, item_to_be_moved)

            self.inner_drag_is_active = False
            self.inner_drag_start_position = QPoint()
            self.dragged_item = None
            self.dragged_item_style = None
            self.dragged_item_row = None
            self.current_drop_row = None
            self.dragged_item_key = None

        self.reorder_animation.finished.connect(finished)
        self.reorder_animation.start()

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        delegate = Delegate(self)

        painter.save()
        sum_offset = 0
        i = 0
        for i in range(len(self.items_by_id)):
            item = self.items_list[i].item
            item_style = self.items_list[i].item_style
            sum_offset += item_style.y_offset
            _rect = self.getIndexRect(i)
            real_rect = QRect(0, i * 60 - self.scroll_bar.value() + sum_offset, self.width(), 60)
            if not real_rect.intersects(self.rect()):
                i += 1
                continue
            if self.dragged_item_row == i:
                i += 1
                continue
            painter.save()
            painter.translate(QPoint(0, item_style.y_offset))
            delegate.paint(painter, _rect, item_style, item)
            painter.restore()
            i += 1
        painter.restore()

        if self.inner_drag_is_active:
            _rect = QRect(0, self.dragged_y_pos, self.width(), 60)
            delegate.paint(painter, _rect, self.dragged_item_style, self.dragged_item)

        painter.end()
