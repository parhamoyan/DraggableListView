import sys
from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from qutewindow import QuteWindow

from DraggableListView import DraggableListView


class Window(QuteWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.resize(QSize(800, 600))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(40, 40, 40, 40)
        self.setStyleSheet("background-color: #333333;")
        self.listView = DraggableListView()
        self.verticalLayout.addWidget(self.listView)
        # TEMP
        self.listView.setStyleSheet("""
/* VERTICAL SCROLLBAR */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 6px;
    border-radius: 3px;
}
/*  HANDLE BAR VERTICAL */
QScrollBar::handle:vertical {
    background-color: #CCCCCC;
    min-height: 30px;
    border-radius: 3px;
    margin-top: 0px;
}
/* BTN TOP - SCROLLBAR */
QScrollBar::sub-line:vertical {
    border: none;
    background-color: #222327;
    height: 0px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
/* BTN BOTTOM - SCROLLBAR */
QScrollBar::add-line:vertical {
    border: none;
    background-color:  #222327;
    height: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
/* RESET ARROW        */
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* HORIZONTAL SCROLLBAR */
QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 6px;
    border-radius: 3px;
}

/* HANDLE BAR HORIZONTAL */
QScrollBar::handle:horizontal {
    background-color: #CCCCCC;
    min-width: 30px;
    border-radius: 3px;
    margin-left: 0px;
}

/* BTN LEFT - SCROLLBAR */
QScrollBar::sub-line:horizontal {
    border: none;
    background-color: #222327;
    width: 0px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

/* BTN RIGHT - SCROLLBAR */
QScrollBar::add-line:horizontal {
    border: none;
    background-color: #222327;
    width: 0px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}

/* RESET ARROW */
QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    background: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QComboBox {
    color: #F2F2F2;
    border: none;
    border-radius: 5px;
    background-color: #181C35;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 11px;
    font-weight: bold;
}

QComboBox:disabled {
    background-color: #343434;
}

QComboBox QAbstractItemView {
    color: white;
    background-color: #181C35;
    outline: none;
    border: 2px solid #333333;
    padding: 10px;
    border-radius: 5px;
}


QComboBox QAbstractItemView:item {
    padding-left: 10px;
}

/* VERTICAL SCROLLBAR */
QComboBox QScrollBar:vertical {
    border: none;
    background-color:  #121215;
    width: 6px;
    border-radius: 0px;
}

/*  HANDLE BAR VERTICAL */
QComboBox QScrollBar::handle:vertical {
    background-color: #4c4d52;
    min-height: 30px;
    border-radius: 5px;
}

/* BTN TOP - SCROLLBAR */
QComboBox QScrollBar::sub-line:vertical {
    border: none;
    background-color: transparent;
    height: 15px;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

/* BTN BOTTOM - SCROLLBAR */
QComboBox QScrollBar::add-line:vertical {
    border: none;
    background-color: transparent;
    height: 15px;
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

/* RESET ARROW        */
QComboBox QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}

QComboBox QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
""")
        self.center()

    def center(self):
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        fg = self.frameGeometry()
        fg.moveCenter(center)
        self.move(fg.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Window()
    demo.show()
    sys.exit(app.exec())
