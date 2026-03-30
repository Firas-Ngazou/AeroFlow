from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QDoubleSpinBox, QSlider, QSpinBox, QComboBox

from q_real_slider import QRealSlider

#region PushButtons (PB)
class QResetPB(QPushButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        font = QFont("Author", 12)
        self.setText("RESET")
        self.setFont(font)
        self.setFixedSize(75, 24)
        self.setProperty("class", "reset_pb")

class QSettingsTabPB(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)

        font = QFont("Author", 12)
        self.setFont(font)
        self.setText(text)
        self.setCheckable(True)
        self.setFixedSize(150, 30)
        self.setProperty("class", "settings_tab_pb")
#endregion

#region Groups
class QAbstractSliderGroup(QWidget):
    def __init__(self, text: str, slider: QSlider | QRealSlider, spin_box: QSpinBox | QDoubleSpinBox,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self._default_value = 0
        self._default_range = (0, 10)

        # Primary frame & layout
        primary_frame = QFrame()
        primary_frame.setProperty("class", "primary_frame")
        self._primary_layout = QVBoxLayout(primary_frame)

        # Title
        self._title = QLabel(text)
        self._title.setFont(QFont("Author", 11))

        # Reset button
        self._reset_button = QResetPB()
        self._reset_button.setFont(QFont("Author", 9))
        self._reset_button.clicked.connect(self._on_reset_pressed)

        # Slider & spinbox
        self._slider = slider
        self._spin_box = spin_box

        self._slider.setOrientation(Qt.Orientation.Horizontal)
        self._slider.setFixedHeight(24)
        self._slider.setProperty("class", "settings_slider")
        self._slider.setValue(self._default_value)
        self._slider.setRange(*self._default_range)

        # self._spin_box.setFixedWidth(100)
        self._spin_box.setFixedHeight(24)
        self._spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spin_box.setProperty("class", "settings_spin_box")
        self._spin_box.setFont(QFont("Author", 7))
        self._spin_box.setValue(self._default_value)
        self._spin_box.setRange(*self._default_range)

        # Secondary layouts
        self._top_layout = QHBoxLayout()
        self._top_layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignLeft)
        self._top_layout.addWidget(self._spin_box)
        self._top_layout.addWidget(self._reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        self._top_layout.setContentsMargins(10, 2, 10, 2)

        self._bottom_layout = QHBoxLayout()
        self._bottom_layout.addWidget(self._slider)
        self._bottom_layout.setContentsMargins(15, 2, 15, 2)

        self._primary_layout.addLayout(self._top_layout)
        self._primary_layout.addLayout(self._bottom_layout)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(primary_frame)

    @Slot()
    def _on_reset_pressed(self):
        self._slider.setValue(self._default_value)
        self._spin_box.setValue(self._default_value)

class QRealSliderGroup(QAbstractSliderGroup):
    realValueChanged = Signal(float)

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, QRealSlider(), QDoubleSpinBox(), parent)

        # Connections
        self._slider.realValueChanged.connect(self._spin_box.setValue)
        self._slider.realValueChanged.connect(self.realValueChanged)
        self._spin_box.valueChanged.connect(self._slider.setValue)

class QSliderGroup(QAbstractSliderGroup):
    valueChanged = Signal(int)

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, QSlider(), QSpinBox(), parent)

        # Connections
        self._slider.valueChanged.connect(self._spin_box.setValue)
        self._slider.valueChanged.connect(self.valueChanged)
        self._spin_box.valueChanged.connect(self._slider.setValue)
#endregion