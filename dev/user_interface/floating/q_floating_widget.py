import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QImage, QPixmap, QPainter, QMouseEvent, QFont
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QStyleOption, QStyle, QFrame, QTabWidget, \
    QHBoxLayout

class QFloatingWidget(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.set_property("class", "floating_widget")
        self.mouse_tracking = True

        floating_dots = QPixmap(":/res/floating_dots_white.png")
        floating_dots_label = QLabel()
        floating_dots_label.pixmap = floating_dots.scaled(50, 10)

        self._v_box_layout = QVBoxLayout(self)
        self._v_box_layout.add_widget(floating_dots_label, alignment=Qt.AlignmentFlag.AlignTop |
                                                                   Qt.AlignmentFlag.AlignRight)
        self._v_box_layout.set_contents_margins(5, 2, 10, 5)

        self._old_pos = None
        self._saved_position = self.pos

    def mouse_press_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.global_position().to_point()
        if event.button() == Qt.MouseButton.RightButton:
            self._correct_position()
            self._old_pos = None

    def mouse_move_event(self, event: QMouseEvent):
        if self._old_pos is not None:
            current_pos = event.global_position().to_point()
            delta = current_pos - self._old_pos

            new_x = delta.x() + self.x
            new_y = delta.y() + self.y

            # Clamping
            max_x_pos = self.parent().width - self.width
            max_y_pos = self.parent().height - self.height
            new_x = max(0, min(new_x, max_x_pos))
            new_y = max(0, min(new_y, max_y_pos))

            self.move(new_x, new_y)
            self._old_pos = current_pos

    def mouse_release_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = None
            self._saved_position = self.pos

    def _correct_position(self):
        self.move(self._saved_position)

    @property
    def saved_position(self):
        return self._saved_position
    @saved_position.setter
    def saved_position(self, new_pos: QPoint):
        self._saved_position = new_pos