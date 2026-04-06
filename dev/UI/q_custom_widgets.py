import os
import ressources_rc

from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QFont, QFontDatabase, QPalette, QColor, QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QDoubleSpinBox, QSlider, QSpinBox, QComboBox

from q_real_slider import QRealSlider

#region Stuff idk
class QVSeperator(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFixedHeight(16)
#endregion

#region PushButtons (PB)
class QResetPB(QPushButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        font = QFont("JetBrains Mono", 12)
        self.setText("RESET")
        self.setFont(font)
        self.setFixedSize(75, 24)
        self.setProperty("class", "reset_pb")

class QSettingsTabPB(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)

        font = QFont("JetBrains Mono", 12)
        font.setBold(True)
        self.setFont(font)
        self.setText(text)
        self.setCheckable(True)
        self.setFixedSize(150, 30)
        self.setProperty("class", "settings_tab_pb")

class QAnalysisTabPB(QWidget):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.setFixedHeight(30)
        self.setFixedWidth(120)

        font = QFont("JetBrains Mono", 12)
        font.setBold(True)

        button = QPushButton(text)
        button.setFont(font)
        button.setFixedSize(114, 24)
        button.setProperty("class", "title_bar_pb")
        button.setCheckable(True)

        analysis_frame = QFrame()
        analysis_frame.setProperty("class", "constraint_frame")

        primary_layout = QHBoxLayout(analysis_frame)
        primary_layout.addWidget(button)
        primary_layout.setContentsMargins(2, 2, 2, 2)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(analysis_frame)
        root_layout.setContentsMargins(0, 0, 0, 0)
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
        self._reset_button.setFont(QFont("JetBrains Mono", 9))
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
        self._spin_box.setFont(QFont("JetBrains Mono", 7))
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

    @property
    def value(self) -> float | int:
        return self._slider.value()

    @value.setter
    def value(self, value: float | int):
        self._slider.setValue(value)
        self._spin_box.setValue(value)

    @property
    def maximum(self) -> float | int:
        return self._slider.maximum()

    @maximum.setter
    def maximum(self, value: float | int):
        self._slider.setMaximum(value)
        self._spin_box.setMaximum(value)

    @property
    def minimum(self) -> float | int:
        return self._slider.minimum()

    @minimum.setter
    def minimum(self, value: float | int):
        self._slider.setMinimum(value)
        self._spin_box.setMinimum(value)

    @property
    def single_step(self) -> float | int:
        return self._spin_box.singleStep()

    @single_step.setter
    def single_step(self, step: float | int):
        self._spin_box.setSingleStep(step)
        self._slider.setSingleStep(step)

    def set_value(self, value: float | int):
        self._slider.setValue(value)
        self._spin_box.setValue(value)

    def set_range(self, min_range: float | int, max_range: float | int):
        self._slider.setRange(min_range, max_range)
        self._spin_box.setRange(min_range, max_range)

class QSliderGroup(QAbstractSliderGroup):
    valueChanged = Signal(int)

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, QSlider(), QSpinBox(), parent)

        # Connections
        self._slider.valueChanged.connect(self._spin_box.setValue)
        self._slider.valueChanged.connect(self.valueChanged)
        self._spin_box.valueChanged.connect(self._slider.setValue)

    @property
    def value(self) -> int:
        return self._slider.value()

    @value.setter
    def value(self, value: int):
        self._slider.setValue(value)
        self._spin_box.setValue(value)

    @property
    def maximum(self) -> int:
        return self._slider.maximum()

    @maximum.setter
    def maximum(self, value: int):
        self._slider.setMaximum(value)
        self._spin_box.setMaximum(value)

    @property
    def minimum(self) -> int:
        return self._slider.minimum()

    @minimum.setter
    def minimum(self, value: int):
        self._slider.setMinimum(value)
        self._spin_box.setMinimum(value)

    @property
    def single_step(self) -> int:
        return self._spin_box.singleStep()

    @single_step.setter
    def single_step(self, step: int):
        self._spin_box.setSingleStep(step)
        self._slider.setSingleStep(step)

    def set_value(self, value: int):
        self._slider.setValue(value)
        self._spin_box.setValue(value)

    def set_range(self, min_range: int, max_range: int):
        self._slider.setRange(min_range, max_range)
        self._spin_box.setRange(min_range, max_range)

class QHistoryGroup(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setFixedHeight(30)
        self.setFixedWidth(150)

        # Icons
        undo_icon = QIcon(":/res/undo_icon_black.png")
        redo_icon = QIcon(":/res/redo_icon_black.png")
        trash_icon = QIcon(":/res/trash_icon_black.png")

        # Undo button
        self._undo_button = QPushButton()
        self._undo_button.setFixedHeight(24)
        self._undo_button.setIcon(undo_icon)
        self._undo_button.setIconSize(QSize(32, 32))
        self._undo_button.setProperty("class", "title_bar_pb")

        # Redo button
        self._redo_button = QPushButton()
        self._redo_button.setFixedHeight(24)
        self._redo_button.setIcon(redo_icon)
        self._redo_button.setIconSize(QSize(32, 32))
        self._redo_button.setProperty("class", "title_bar_pb")

        # Trash button
        self._trash_button = QPushButton()
        self._trash_button.setFixedHeight(24)
        self._trash_button.setIcon(trash_icon)
        self._trash_button.setIconSize(QSize(20, 20))
        self._trash_button.setProperty("class", "title_bar_pb")

        # Primary frame & layout
        primary_frame = QFrame()
        primary_frame.setProperty("class", "constraint_frame")

        self._primary_layout = QHBoxLayout(primary_frame)
        self._primary_layout.setContentsMargins(2, 2, 2, 2)
        self._primary_layout.addWidget(self._undo_button)
        self._primary_layout.addWidget(self._trash_button)
        self._primary_layout.addWidget(self._redo_button)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(primary_frame)
        root_layout.setContentsMargins(0, 0, 0, 0)

#endregion