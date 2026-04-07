import os
import sys
import ressources_rc

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QMouseEvent
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QStyleOption, QStyle, QFrame

class QFloatingWidget(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(600, 300)

        self.setWindowFlags(self.windowFlags().FramelessWindowHint | self.windowFlags().WindowStaysOnTopHint)
        self.setProperty("class", "floating_widget")
        self.setMouseTracking(True)

        floating_dots = QPixmap(":/res/floating_dots_white.png")
        floating_dots_label = QLabel()
        floating_dots_label.setPixmap(floating_dots.scaled(50, 10))

        self.v_box_layout = QVBoxLayout(self)
        self.v_box_layout.addWidget(floating_dots_label, alignment=Qt.AlignmentFlag.AlignTop |
                                                                   Qt.AlignmentFlag.AlignRight)
        self.v_box_layout.setContentsMargins(5, 2, 10, 5)

        self._old_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = None

def load_styles(q_app: QApplication):
    base_path = os.path.dirname(os.path.abspath(__file__))
    styles_path = os.path.join(base_path, "styles.qss")

    if os.path.exists(styles_path):
        with open(styles_path, "r") as file:
            q_app.setStyleSheet(file.read())

    else:
        print("'styles.qss' file was not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_styles(app)
    window = QFloatingWidget()
    window.show()
    app.exec()