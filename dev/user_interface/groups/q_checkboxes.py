from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QApplication, QPushButton, \
    QMessageBox


class QDoubleCheckBox(QWidget):
    leftRequested = Signal()
    rightRequested = Signal()

    def __init__(self, section_name: str, left_name: str, right_name: str, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._section_name = section_name
        self._left_name = left_name
        self._right_name = right_name

        # Fonts
        title_font = QFont("JetBrains Mono", 12)
        title_font.setBold(True)
        general_font = QFont("JetBrains Mono", 10)

        # Labels
        self._section_label = QLabel(section_name)
        self._section_label.setFont(title_font)
        self._left_label = QLabel(left_name)
        self._left_label.setFont(general_font)
        self._right_label = QLabel(right_name)
        self._right_label.setFont(general_font)

        # Checkboxes
        self._left_checkbox = QCheckBox()
        self._left_checkbox.setProperty("class", "checkbox")
        self._left_checkbox.setFixedSize(30, 30)
        self._left_checkbox.setChecked(True)
        self._right_checkbox = QCheckBox()
        self._right_checkbox.setProperty("class", "checkbox")
        self._right_checkbox.setFixedSize(30, 30)

        # Layout
        primary_frame = QFrame()
        primary_frame.setProperty("class", "primary_frame")

        self._h_layout = QHBoxLayout(primary_frame)
        self._h_layout.addWidget(self._left_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        self._h_layout.addWidget(self._left_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self._h_layout.addStretch()
        self._h_layout.addWidget(self._right_checkbox, alignment=Qt.AlignmentFlag.AlignRight)
        self._h_layout.addWidget(self._right_label, alignment=Qt.AlignmentFlag.AlignRight)
        self._h_layout.setContentsMargins(5, 5, 5, 5)
        self._h_layout.addStretch()

        self._v_layout = QVBoxLayout(self)
        self._v_layout.setSpacing(0)
        self._v_layout.addWidget(self._section_label)
        self._v_layout.addWidget(primary_frame)
        self._v_layout.setContentsMargins(0, 0, 0, 0)

        # Connections
        self._left_checkbox.clicked.connect(self._on_left_clicked)
        self._right_checkbox.clicked.connect(self._on_right_clicked)

    @Slot()
    def _on_left_clicked(self):
        if self._left_checkbox.isChecked():
            self._right_checkbox.setChecked(False)
            self.leftRequested.emit()

    @Slot()
    def _on_right_clicked(self):
        if self._right_checkbox.isChecked():
            self._left_checkbox.setChecked(False)
            self.rightRequested.emit()

    def check_left(self):
        if not self._left_checkbox.isChecked():
            self._left_checkbox.click()

    def check_right(self):
        if not self._right_checkbox.isChecked():
            self._right_checkbox.click()

    def uncheck_all(self):
        if self._left_checkbox.isChecked(): self._left_checkbox.click()
        if self._right_checkbox.isChecked(): self._right_checkbox.click()

class QInfoCheckbox(QWidget):
    stateChanged = Slot(bool)

    def __init__(self, name: str, info: str, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        info_icon = QIcon(":res/info_icon_black.png")
        self._name = name
        self._info = info
        title_font = QFont("JetBrains Mono", 12)
        title_font.setBold(True)
        self._info_font = QFont("JetBrains Mono", 10)

        # Labels
        self._name_label = QLabel(self._name)
        self._name_label.setFont(title_font)
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Info button
        self._info_button = QPushButton()
        self._info_button.setIcon(info_icon)
        self._info_button.setIconSize(QSize(20, 20))
        self._info_button.setFixedSize(30, 30)
        self._info_button.setProperty("class", "info_pb")

        # Checkbox
        self._checkbox = QCheckBox()
        self._checkbox.setFixedSize(30, 30)
        self._checkbox.setProperty("class", "checkbox")

        # Layout
        self._primary_layout = QHBoxLayout(self)
        self._primary_layout.addWidget(self._checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.addWidget(self._name_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.addWidget(self._info_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.setContentsMargins(2, 2, 2, 2)
        self._primary_layout.addStretch()

        # Connections
        self._info_button.pressed.connect(self._on_info_pressed)
        self._checkbox.stateChanged.connect(self.stateChanged)

    @Slot()
    def _on_info_pressed(self):
        message_box = QMessageBox()
        message_box.setText(self._info)
        message_box.setFont(self._info_font)
        message_box.setWindowTitle("Info")
        message_box.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        message_box.exec()