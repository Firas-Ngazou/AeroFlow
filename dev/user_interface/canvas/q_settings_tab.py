import sys

from PySide6.QtCore import Qt, Slot, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QApplication, QPushButton, QVBoxLayout, QDoubleSpinBox, \
    QLabel, QComboBox, QScrollArea, QGridLayout

from dev.user_interface.components.q_buttons import QSettingsTabPB
from dev.user_interface.groups.q_slider_groups import QSliderGroup, QRealSliderGroup

class QSettingsGeneralTab(QWidget):
    qualityChanged = Signal(float)
    windSpeedChanged = Signal(float)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Resolution
        self._quality = QRealSliderGroup("QUALITY")

        self._quality.minimum = 0.1
        self._quality.maximum = 1.0
        self._quality.single_step = 0.01
        self._quality.default_value = 1.0

        high_res_warning = QLabel(" ATTENTION : Une trop haute valeur peut résulter \n"
                                  " en une perte de performance importante.")
        high_res_warning.setFont(QFont("JetBrains Mono", 8))

        # Wind speed
        self._wind_speed = QRealSliderGroup("VITESSE (m/s)")
        self._wind_speed.minimum = 1.0
        self._wind_speed.maximum = 100.0

        # Layouts
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self._quality)
        root_layout.addWidget(high_res_warning)
        root_layout.addSpacing(30)
        root_layout.addWidget(self._wind_speed)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

        # Connections
        self._quality.realValueChanged.connect(self.qualityChanged.emit)
        self._wind_speed.realValueChanged.connect(self.windSpeedChanged.emit)

    @property
    def quality(self) -> float:
        return self._quality.value
    @quality.setter
    def quality(self, value: float):
        self._quality.value = value

    @property
    def wind_speed(self) -> float:
        return self._wind_speed.value
    @wind_speed.setter
    def wind_speed(self, value: float):
        self._wind_speed.value = value

class QSettingsOptimizationTab(QWidget):
    constraintChanged = Signal(str)
    iterationsChanged = Signal(int)
    thresholdChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Constraint method
        # Title
        self._title = QLabel("CONTRAINTE")
        self._title.setFont(QFont("JetBrains Mono", 11))

        # Combobox
        self._combo_box = QComboBox()
        self._combo_box.setPlaceholderText("MÉTHODE")
        self._combo_box.setProperty("class", "settings_combo_box")
        self._combo_box.setFixedSize(150, 30)
        self._combo_box.setFont(QFont("JetBrains Mono", 9))

        self._combo_box.addItem("DISTANCE")
        self._combo_box.addItem("SURFACE")

        self._combo_box.setCurrentIndex(1)

        # Primary frame & layout
        constraint_frame = QFrame()
        constraint_frame.setProperty("class", "constraint_frame")
        self._constraint_layout = QHBoxLayout(constraint_frame)

        self._constraint_layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignLeft)
        self._constraint_layout.addWidget(self._combo_box, alignment=Qt.AlignmentFlag.AlignRight)
        self._constraint_layout.setContentsMargins(15, 0, 0, 0)

        # Threshold
        self._threshold_setting = QSliderGroup("SEUIL (%)")
        self._threshold_setting.minimum = 1
        self._threshold_setting.maximum = 100
        self._threshold_setting.single_step = 5
        self._threshold_setting.default_value = 5

        # Iterations
        self._iterations_setting = QSliderGroup("ITÉRATIONS")
        self._iterations_setting.minimum = 1
        self._iterations_setting.maximum = 1000
        self._iterations_setting.single_step = 5
        self._iterations_setting.default_value = 20

        # Root
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(constraint_frame)
        root_layout.addWidget(self._threshold_setting)
        root_layout.addWidget(self._iterations_setting)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

        # Connections
        self._combo_box.currentTextChanged.connect(self.constraintChanged.emit)
        self._threshold_setting.valueChanged.connect(self.thresholdChanged.emit)
        self._iterations_setting.valueChanged.connect(self.iterationsChanged.emit)

    @property
    def constraint_method(self) -> str:
        return self._combo_box.currentText()
    @constraint_method.setter
    def constraint_method(self, constraint: str):
        self._combo_box.setCurrentText(constraint)

    @property
    def threshold(self) -> int:
        return self._threshold_setting.value
    @threshold.setter
    def threshold(self, threshold: int):
        self._threshold_setting.set_value(threshold)

    @property
    def iterations(self) -> int:
        return self._iterations_setting.value
    @iterations.setter
    def iterations(self, iterations: int):
        self._iterations_setting.set_value(iterations)

class QSettingsSideBar(QWidget):
    constraintChanged = Signal(str)
    iterationsChanged = Signal(int)
    thresholdChanged = Signal(int)
    qualityChanged = Signal(float)
    windSpeedChanged = Signal(float)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._current_tab = 0

        self._height = 900
        self._primary_frame = QFrame()
        self._primary_frame.setProperty("class", "primary_frame")

        self._full_frame = QFrame()
        self._full_frame.setFixedHeight(self._height)

        self._side_button_layout = QHBoxLayout(self._full_frame)

        self._primary_layout = QVBoxLayout(self._primary_frame)
        self._primary_layout.setContentsMargins(10, 10, 10, 5)

        self._secondary_layout = QHBoxLayout()
        self._secondary_layout.setContentsMargins(10, 5, 10, 5)
        self._primary_layout.addLayout(self._secondary_layout)

        self._collapsed_width = 25
        self._expanded_width = 400

        self._full_frame.setMaximumWidth(self._collapsed_width)

        self._is_collapsed = True

        # Side button
        self._open_icon = QIcon(":/res/left_arrow_icon_black.png")
        self._close_icon = QIcon(":/res/right_arrow_icon_black.png")
        self._side_button = QPushButton()
        self._side_button.setIcon(self._open_icon)
        self._side_button.setProperty("class", "sidebar_pb")
        self._side_button.setFixedSize(25, self._height - 200)
        self._side_button_layout.setContentsMargins(2, 0, 0, 0)
        self._side_button_layout.addWidget(self._side_button,
                                           alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._side_button_layout.addWidget(self._primary_frame)

        # General tab
        self._general_button = QSettingsTabPB("GÉNÉRAL")
        self._general_button.setChecked(True)
        self._secondary_layout.addWidget(self._general_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                   Qt.AlignmentFlag.AlignLeft)
        self._general_tab = QSettingsGeneralTab()
        self._primary_layout.addWidget(self._general_tab)

        # Optimization tab
        self._optimization_button = QSettingsTabPB("OPTIMIZATION")
        self._secondary_layout.addWidget(self._optimization_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                        Qt.AlignmentFlag.AlignRight)
        self._optimization_tab = QSettingsOptimizationTab()
        self._primary_layout.addWidget(self._optimization_tab)
        self._optimization_tab.hide()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self._full_frame)

        # Connections
        self._general_button.clicked.connect(self._on_tab_changed)
        self._optimization_button.clicked.connect(self._on_tab_changed)

        self._general_tab.qualityChanged.connect(self.qualityChanged.emit)
        self._general_tab.windSpeedChanged.connect(self.windSpeedChanged.emit)
        self._optimization_tab.constraintChanged.connect(self.constraintChanged.emit)
        self._optimization_tab.iterationsChanged.connect(self.iterationsChanged.emit)
        self._optimization_tab.thresholdChanged.connect(self.thresholdChanged.emit)

        self._side_button.pressed.connect(self._on_side_button_pressed)

        # Animation
        self._animation = QPropertyAnimation(self._full_frame, b"maximumWidth")
        self._animation.setDuration(400)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_animation_finished)

        self.is_collapsed = True

    def resizeEvent(self, event):
        self._height = self.window().height() - 200
        self._side_button.setFixedHeight(self._height)
        self._full_frame.setFixedHeight(self._height)

    @property
    def constraint_method(self) -> str:
        return self._optimization_tab.constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint: str):
        self._optimization_tab.constraint_method = constraint

    @property
    def threshold(self) -> int:
        return self._optimization_tab.threshold
    @threshold.setter
    def threshold(self, threshold: int):
        self._optimization_tab.threshold = threshold

    @property
    def iterations(self) -> int:
        return self._optimization_tab.iterations
    @iterations.setter
    def iterations(self, iterations: int):
        self._optimization_tab.iterations = iterations

    @property
    def quality(self) -> float:
        return self._general_tab.quality
    @quality.setter
    def quality(self, quality: float):
        self._general_tab.quality = quality

    @property
    def wind_speed(self) -> float:
        return self._general_tab.wind_speed
    @wind_speed.setter
    def wind_speed(self, wind_speed: float):
        self._general_tab.wind_speed = wind_speed

    @Slot()
    def _on_tab_changed(self):
        sender = self.sender()

        # General tab was pressed
        if sender == self._general_button:

            # General tab was already pressed
            if self._current_tab == 0:
                self._general_button.setChecked(True)
                return

            # General tab was not pressed
            self._general_button.setChecked(True)
            self._optimization_button.setChecked(False)
            self._current_tab = 0
            self._optimization_tab.hide()
            self._general_tab.show()

        # Optimization tab was pressed
        else:

            # Optimization tab was already pressed
            if self._current_tab == 1:
                self._optimization_button.setChecked(True)

            # Optimization tab was not pressed
            self._optimization_button.setChecked(True)
            self._general_button.setChecked(False)
            self._current_tab = 1
            self._general_tab.hide()
            self._optimization_tab.show()

    @Slot()
    def _on_side_button_pressed(self):
        if self.is_collapsed:
            self.is_collapsed = False
        else:
            self.is_collapsed = True

    @property
    def is_collapsed(self) -> bool:
        return self._is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, value: bool):
        self._is_collapsed = value
        self._primary_frame.show()
        if self._is_collapsed:
            self._side_button.setIcon(self._open_icon)
            self._animation.setStartValue(self._expanded_width)
            self._animation.setEndValue(self._collapsed_width)
        else:
            self._side_button.setIcon(self._close_icon)
            self._animation.setStartValue(self._collapsed_width)
            self._animation.setEndValue(self._expanded_width)

        self._animation.start()

    @Slot()
    def _on_animation_finished(self):
        if self._is_collapsed:
            self._primary_frame.hide()