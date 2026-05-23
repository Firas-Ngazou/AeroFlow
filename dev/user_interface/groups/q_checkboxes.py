import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QApplication, QPushButton, \
    QMessageBox


class QDoubleCheckBox(QWidget):
    leftStateChanged = Signal(int)
    rightStateChanged = Signal(int)

    def __init__(self, section_name: str, left_name: str, right_name: str, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._section_name = section_name
        self._left_name = left_name
        self._right_name = right_name

        # Fonts
        title_font = QFont("JetBrains Mono", 12)
        title_font.set_bold(True)
        general_font = QFont("JetBrains Mono", 10)

        # Labels
        self._section_label = QLabel(section_name)
        self._section_label.font = title_font
        self._left_label = QLabel(left_name)
        self._left_label.font = general_font
        self._right_label = QLabel(right_name)
        self._right_label.font = general_font

        # Checkboxes
        self._left_checkbox = QCheckBox()
        self._left_checkbox.set_property("class", "checkbox")
        self._left_checkbox.set_fixed_size(30, 30)
        self._left_checkbox.checked = True
        self._right_checkbox = QCheckBox()
        self._right_checkbox.set_property("class", "checkbox")
        self._right_checkbox.set_fixed_size(30, 30)

        # Layout
        primary_frame = QFrame()
        primary_frame.set_property("class", "primary_frame")

        self._h_layout = QHBoxLayout(primary_frame)
        self._h_layout.add_widget(self._left_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        self._h_layout.add_widget(self._left_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self._h_layout.add_stretch()
        self._h_layout.add_widget(self._right_checkbox, alignment=Qt.AlignmentFlag.AlignRight)
        self._h_layout.add_widget(self._right_label, alignment=Qt.AlignmentFlag.AlignRight)
        self._h_layout.set_contents_margins(5, 5, 5, 5)
        self._h_layout.add_stretch()

        self._v_layout = QVBoxLayout(self)
        self._v_layout.spacing = 0
        self._v_layout.add_widget(self._section_label)
        self._v_layout.add_widget(primary_frame)
        self._v_layout.set_contents_margins(0, 0, 0, 0)

        # Connections
        self._left_checkbox.clicked.connect(self._on_left_clicked)
        self._right_checkbox.clicked.connect(self._on_right_clicked)
        self._left_checkbox.stateChanged.connect(self.leftStateChanged)
        self._right_checkbox.stateChanged.connect(self.rightStateChanged)

    @Slot()
    def _on_left_clicked(self):
        if self._left_checkbox.checked:
            self._right_checkbox.checked = False

    @Slot()
    def _on_right_clicked(self):
        if self._right_checkbox.checked:
            self._left_checkbox.checked = False

    def check_left(self):
        if not self._left_checkbox.checked:
            self._left_checkbox.click()

    def check_right(self):
        if not self._right_checkbox.checked:
            self._right_checkbox.click()

    def uncheck_all(self):
        if self._left_checkbox.checked: self._left_checkbox.click()
        if self._right_checkbox.checked: self._right_checkbox.click()

    @property
    def left_state(self) -> int:
        if self._left_checkbox.checked:
            return 1
        else:
            return 0
    @left_state.setter
    def left_state(self, state: int):
        if state == 0:
            self._left_checkbox.checked = False
        elif state == 1:
            self._left_checkbox.checked = True

    @property
    def right_state(self) -> int:
        if self._right_checkbox.checked:
            return 1
        else:
            return 0
    @right_state.setter
    def right_state(self, state: int):
        if state == 0:
            self._right_checkbox.checked = False
        elif state == 1:
            self._right_checkbox.checked = True

class QInfoCheckbox(QWidget):
    stateChanged = Signal(int)

    def __init__(self, name: str, info: str, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        info_icon = QIcon(":res/info_icon_black.png")
        self._name = name
        self._info = info
        title_font = QFont("JetBrains Mono", 12)
        title_font.set_bold(True)
        self._info_font = QFont("JetBrains Mono", 10)

        # Labels
        self._name_label = QLabel(self._name)
        self._name_label.font = title_font
        self._name_label.alignment = Qt.AlignmentFlag.AlignCenter

        # Info button
        self._info_button = QPushButton()
        self._info_button.icon = info_icon
        self._info_button.icon_size = QSize(20, 20)
        self._info_button.fixed_size = QSize(30, 30)
        self._info_button.set_property("class", "info_pb")

        # Checkbox
        self._checkbox = QCheckBox()
        self._checkbox.set_fixed_size(30, 30)
        self._checkbox.set_property("class", "checkbox")

        # Layout
        self._primary_layout = QHBoxLayout(self)
        self._primary_layout.add_widget(self._checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.add_widget(self._name_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.add_widget(self._info_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.set_contents_margins(2, 2, 2, 2)
        self._primary_layout.add_stretch()

        # Connections
        self._info_button.pressed.connect(self._on_info_pressed)
        self._checkbox.stateChanged.connect(self.stateChanged)

    @Slot()
    def _on_info_pressed(self):
        message_box = QMessageBox()
        message_box.text = self._info
        message_box.font = self._info_font
        message_box.window_title = "Info"
        message_box.set_window_flag(Qt.WindowType.FramelessWindowHint)
        message_box.exec()

    @property
    def state(self) -> int:
        if self._checkbox.checked:
            return 1
        else:
            return 0
    @state.setter
    def state(self, state: int):
        if state == 0:
            self._checkbox.checked = False
        elif state == 1:
            self._checkbox.checked = True