from typing import Optional

from PySide6.QtCore import QTimer, QVariantAnimation
from PySide6.QtWidgets import QScrollBar, QWidget, QGraphicsOpacityEffect


class CustomScrollBar(QScrollBar):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSingleStep(10)
        self.setPageStep(20)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.hide()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hideScrollBar)
        self.sliderPressed.connect(self.slider_pressed)
        self.sliderReleased.connect(self.slider_released)

    def slider_pressed(self) -> None:
        self.timer.stop()
        self.show()

    def slider_released(self) -> None:
        self.start_single_shot()

    def start_single_shot(self) -> None:
        self.opacity_effect.setOpacity(1)
        self.show()
        self.timer.stop()
        self.timer.start(1000)

    def wheelEvent(self, event) -> None:
        super().wheelEvent(event)
        self.start_single_shot()

    def getAnimation(self, start_value, end_value) -> QVariantAnimation:
        animation = QVariantAnimation(self.opacity_effect)
        animation.setDuration(500)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)

        def valueChanged(new_value):
            self.opacity_effect.setOpacity(new_value / 100)

        animation.valueChanged.connect(valueChanged)
        return animation

    def showScrollBar(self) -> None:
        animation = self.getAnimation(0, 100)
        animation.finished.connect(self.show)
        animation.start()

    def hideScrollBar(self):
        animation = self.getAnimation(100, 0)
        animation.finished.connect(self.hide)
        animation.start()
