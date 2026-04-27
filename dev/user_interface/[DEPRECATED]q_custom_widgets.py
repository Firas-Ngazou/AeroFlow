# # +------------------+
# # | DEPRECATED CODE  |
# # +------------------+
#
# from enum import Enum
#
# from PySide6.QtCore import Qt, Slot, Signal, QSize, QPoint
# from PySide6.QtGui import QFont, QIcon, QShowEvent, QHideEvent
# from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QApplication, QPushButton, QVBoxLayout, QLabel, \
#     QDoubleSpinBox, QSlider, QSpinBox, QTabWidget, QMainWindow
#
# from dev.user_interface.components.q_real_slider import QRealSlider
# from dev.user_interface.floating.q_floating_widget import QFloatingWidget
#
#
# #region Stuff idk
# class QVSeperator(QFrame):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#         self.setFrameShape(QFrame.Shape.VLine)
#         self.setFrameShadow(QFrame.Shadow.Sunken)
#         self.setFixedHeight(16)
#
# class QHSeperator(QFrame):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#         self.setFrameShape(QFrame.Shape.HLine)
#         self.setFrameShadow(QFrame.Shadow.Sunken)
#         self.setFixedHeight(16)
# #endregion
#
# #region PushButtons (PB)
# class QResetPB(QPushButton):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         font = QFont("JetBrains Mono", 12)
#         self.setText("RESET")
#         self.setFont(font)
#         self.setFixedSize(75, 24)
#         self.setProperty("class", "reset_pb")
#
# class QSettingsTabPB(QPushButton):
#     def __init__(self, text: str, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         font = QFont("JetBrains Mono", 12)
#         font.setBold(True)
#         self.setFont(font)
#         self.setText(text)
#         self.setCheckable(True)
#         self.setFixedSize(150, 30)
#         self.setProperty("class", "settings_tab_pb")
#
# class QSpecialSettingPB(QWidget):
#     def __init__(self, text: str, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self.setFixedHeight(30)
#         self.setFixedWidth(120)
#
#         font = QFont("JetBrains Mono", 12)
#         font.setBold(True)
#
#         self._button = QPushButton(text)
#         self._button.setFont(font)
#         self._button.setFixedSize(114, 24)
#         self._button.setProperty("class", "title_bar_pb")
#         self._button.setCheckable(True)
#
#         self._floating_widget: QFloatingWidget | None = None
#         self._floating_widget.hide() if self._floating_widget is not None else None
#
#         button_frame = QFrame()
#         button_frame.setProperty("class", "constraint_frame")
#
#         self._primary_layout = QHBoxLayout(button_frame)
#         self._primary_layout.addWidget(self._button)
#         self._primary_layout.setContentsMargins(2, 2, 2, 2)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.addWidget(button_frame)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#
#         self._button.pressed.connect(self._on_button_clicked)
#
#     @Slot()
#     def _on_button_clicked(self):
#         if self._floating_widget is None: return
#         if not self._floating_widget.isVisible():
#             self._floating_widget.show()
#
#         else: self._floating_widget.hide()
#
#     @property
#     def floating_widget(self) -> QFloatingWidget | None:
#         return self._floating_widget
#     @floating_widget.setter
#     def floating_widget(self, widget: QFloatingWidget | None):
#         self._floating_widget = widget
#
# #endregion
#
# #region Groups
# class QAbstractSliderGroup(QWidget):
#     def __init__(self, text: str, slider: QSlider | QRealSlider, spin_box: QSpinBox | QDoubleSpinBox,
#                  parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._default_value = 0
#         self._default_range = (0, 10)
#
#         # Primary frame & layout
#         primary_frame = QFrame()
#         primary_frame.setProperty("class", "primary_frame")
#         self._primary_layout = QVBoxLayout(primary_frame)
#
#         # Title
#         self._title = QLabel(text)
#         self._title.setFont(QFont("JetBrains Mono", 11))
#
#         # Reset button
#         self._reset_button = QResetPB()
#         self._reset_button.setFont(QFont("JetBrains Mono", 9))
#         self._reset_button.clicked.connect(self._on_reset_pressed)
#
#         # Slider & spinbox
#         self._slider = slider
#         self._spin_box = spin_box
#
#         self._slider.setOrientation(Qt.Orientation.Horizontal)
#         self._slider.setFixedHeight(24)
#         self._slider.setProperty("class", "settings_slider")
#         self._slider.setValue(self._default_value)
#         self._slider.setRange(*self._default_range)
#
#         # self._spin_box.setFixedWidth(100)
#         self._spin_box.setFixedHeight(24)
#         self._spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self._spin_box.setProperty("class", "settings_spin_box")
#         self._spin_box.setFont(QFont("JetBrains Mono", 7))
#         self._spin_box.setValue(self._default_value)
#         self._spin_box.setRange(*self._default_range)
#
#         # Secondary layouts
#         self._top_layout = QHBoxLayout()
#         self._top_layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignLeft)
#         self._top_layout.addWidget(self._spin_box)
#         self._top_layout.addWidget(self._reset_button, alignment=Qt.AlignmentFlag.AlignRight)
#         self._top_layout.setContentsMargins(10, 2, 10, 2)
#
#         self._bottom_layout = QHBoxLayout()
#         self._bottom_layout.addWidget(self._slider)
#         self._bottom_layout.setContentsMargins(15, 2, 15, 2)
#
#         self._primary_layout.addLayout(self._top_layout)
#         self._primary_layout.addLayout(self._bottom_layout)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#         root_layout.addWidget(primary_frame)
#
#     @Slot()
#     def _on_reset_pressed(self):
#         self._slider.setValue(self._default_value)
#         self._spin_box.setValue(self._default_value)
#
# class QRealSliderGroup(QAbstractSliderGroup):
#     realValueChanged = Signal(float)
#
#     def __init__(self, text: str, parent: QWidget | None = None):
#         super().__init__(text, QRealSlider(), QDoubleSpinBox(), parent)
#
#         # Connections
#         self._slider.realValueChanged.connect(self._spin_box.setValue)
#         self._slider.realValueChanged.connect(self.realValueChanged)
#         self._spin_box.valueChanged.connect(self._slider.setValue)
#
#     @property
#     def value(self) -> float | int:
#         return self._slider.value()
#
#     @value.setter
#     def value(self, value: float | int):
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
#     @property
#     def maximum(self) -> float | int:
#         return self._slider.maximum()
#
#     @maximum.setter
#     def maximum(self, value: float | int):
#         self._slider.setMaximum(value)
#         self._spin_box.setMaximum(value)
#
#     @property
#     def minimum(self) -> float | int:
#         return self._slider.minimum()
#
#     @minimum.setter
#     def minimum(self, value: float | int):
#         self._slider.setMinimum(value)
#         self._spin_box.setMinimum(value)
#
#     @property
#     def single_step(self) -> float | int:
#         return self._spin_box.singleStep()
#
#     @single_step.setter
#     def single_step(self, step: float | int):
#         self._spin_box.setSingleStep(step)
#         self._slider.setSingleStep(step)
#
#     def set_value(self, value: float | int):
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
#     def set_range(self, min_range: float | int, max_range: float | int):
#         self._slider.setRange(min_range, max_range)
#         self._spin_box.setRange(min_range, max_range)
#
#     @property
#     def default_value(self) -> float | int:
#         return self._default_value
#     @default_value.setter
#     def default_value(self, value: float | int):
#         self._default_value = value
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
# class QSliderGroup(QAbstractSliderGroup):
#     valueChanged = Signal(int)
#
#     def __init__(self, text: str, parent: QWidget | None = None):
#         super().__init__(text, QSlider(), QSpinBox(), parent)
#
#         # Connections
#         self._slider.valueChanged.connect(self._spin_box.setValue)
#         self._slider.valueChanged.connect(self.valueChanged)
#         self._spin_box.valueChanged.connect(self._slider.setValue)
#
#     @property
#     def value(self) -> int:
#         return self._slider.value()
#
#     @value.setter
#     def value(self, value: int):
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
#     @property
#     def maximum(self) -> int:
#         return self._slider.maximum()
#
#     @maximum.setter
#     def maximum(self, value: int):
#         self._slider.setMaximum(value)
#         self._spin_box.setMaximum(value)
#
#     @property
#     def minimum(self) -> int:
#         return self._slider.minimum()
#
#     @minimum.setter
#     def minimum(self, value: int):
#         self._slider.setMinimum(value)
#         self._spin_box.setMinimum(value)
#
#     @property
#     def single_step(self) -> int:
#         return self._spin_box.singleStep()
#
#     @single_step.setter
#     def single_step(self, step: int):
#         self._spin_box.setSingleStep(step)
#         self._slider.setSingleStep(step)
#
#     def set_value(self, value: int):
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
#     def set_range(self, min_range: int, max_range: int):
#         self._slider.setRange(min_range, max_range)
#         self._spin_box.setRange(min_range, max_range)
#
#     @property
#     def default_value(self) -> int:
#         return self._default_value
#
#     @default_value.setter
#     def default_value(self, value: int):
#         self._default_value = value
#         self._slider.setValue(value)
#         self._spin_box.setValue(value)
#
# class QHistoryGroup(QWidget):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self.setFixedHeight(30)
#         self.setFixedWidth(150)
#
#         # Icons
#         undo_icon = QIcon(":/res/undo_icon_black.png")
#         redo_icon = QIcon(":/res/redo_icon_black.png")
#         trash_icon = QIcon(":/res/trash_icon_black.png")
#
#         # Undo button
#         self._undo_button = QPushButton()
#         self._undo_button.setFixedHeight(24)
#         self._undo_button.setIcon(undo_icon)
#         self._undo_button.setIconSize(QSize(32, 32))
#         self._undo_button.setProperty("class", "title_bar_pb")
#
#         # Redo button
#         self._redo_button = QPushButton()
#         self._redo_button.setFixedHeight(24)
#         self._redo_button.setIcon(redo_icon)
#         self._redo_button.setIconSize(QSize(32, 32))
#         self._redo_button.setProperty("class", "title_bar_pb")
#
#         # Trash button
#         self._trash_button = QPushButton()
#         self._trash_button.setFixedHeight(24)
#         self._trash_button.setIcon(trash_icon)
#         self._trash_button.setIconSize(QSize(20, 20))
#         self._trash_button.setProperty("class", "title_bar_pb")
#
#         # Primary frame & layout
#         primary_frame = QFrame()
#         primary_frame.setProperty("class", "constraint_frame")
#
#         self._primary_layout = QHBoxLayout(primary_frame)
#         self._primary_layout.setContentsMargins(2, 2, 2, 2)
#         self._primary_layout.addWidget(self._undo_button)
#         self._primary_layout.addWidget(self._trash_button)
#         self._primary_layout.addWidget(self._redo_button)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.addWidget(primary_frame)
#         root_layout.setContentsMargins(0, 0, 0, 0)
# #endregion
#
# class BarStatus(Enum):
#     IDLE = 0
#     RUNNING = 1
#     FINISHED = 2
#
# class QProgressPoint(QWidget):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._idle_qss = """background-color: #BC6E6E; border-radius: 10px;""" # Red
#         self._running_qss = """background-color: #E4B653; border-radius: 10px;""" # Yellow
#         self._finished_qss = """background-color: #8DB182; border-radius: 10px;""" # Green
#
#         background_frame = QFrame()
#         background_frame.setProperty("class", "progress_point_background")
#         background_frame.setFixedSize(30, 30)
#
#         self._point_frame = QFrame()
#         self._point_frame.setStyleSheet(self._idle_qss)
#         self._point_frame.setFixedSize(20, 20)
#
#         self._status: BarStatus = BarStatus.IDLE
#
#         self._primary_layout = QHBoxLayout(background_frame)
#         self._primary_layout.addWidget(self._point_frame)
#         self._primary_layout.setContentsMargins(0, 0, 0, 0)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.addWidget(background_frame)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#
# class QProgressBar(QWidget):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._bar_length = 450
#         self._fill_percentage = 0
#         self._min_filling = 6 # Under that, filling's edges will be squared
#
#         # Colors
#         self._idle_qss = """background-color: #BC6E6E; border-radius: 10px;"""  # Red
#         self._running_qss = """background-color: #E4B653; border-radius: 10px;"""  # Yellow
#         self._finished_qss = """background-color: #8DB182; border-radius: 10px;"""  # Green
#
#         self._status: BarStatus = BarStatus.IDLE
#
#         # Backgrounds
#         background_frame = QFrame()
#         background_frame.setFixedHeight(30)
#         background_frame.setProperty("class", "light_analysis_frame")
#
#         bar_frame = QFrame()
#         bar_frame.setFixedWidth(self._bar_length)
#         bar_frame.setFixedHeight(30)
#         bar_frame.setProperty("class", "dark_analysis_frame")
#
#         # The filling
#         self._fill_frame = QFrame()
#         self._fill_frame.setFixedWidth(int(self._fill_percentage*((self._bar_length-6)/100)))
#         self._fill_frame.setFixedHeight(24)
#         self._fill_frame.setStyleSheet(self._idle_qss)
#
#         bar_layout = QHBoxLayout(bar_frame)
#         bar_layout.addWidget(self._fill_frame, alignment=Qt.AlignmentFlag.AlignLeft)
#         bar_layout.setContentsMargins(2, 2, 2, 2)
#
#         status_label = QLabel("Statut")
#         status_label.setProperty("class", "dark_text")
#         status_label.setFont(QFont("JetBrains Mono", 12))
#
#         self._progress_point = QProgressPoint()
#
#         self._primary_layout = QHBoxLayout(background_frame)
#         self._primary_layout.addSpacing(15)
#         self._primary_layout.addWidget(status_label)
#         self._primary_layout.addSpacing(10)
#         self._primary_layout.addWidget(self._progress_point)
#         self._primary_layout.addWidget(bar_frame)
#         self._primary_layout.setContentsMargins(0, 0, 0, 0)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.addWidget(background_frame)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#
# class QResultField(QWidget):
#     def __init__(self, text: str, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         primary_field_frame = QFrame()
#         primary_field_frame.setFixedHeight(30)
#         primary_field_frame.setProperty("class", "light_analysis_frame")
#
#         secondary_field_frame = QFrame()
#         secondary_field_frame.setFixedHeight(30)
#         secondary_field_frame.setProperty("class", "dark_analysis_frame")
#
#         self._result_name = QLabel(text)
#         self._result_name.setProperty("class", "dark_text")
#         self._result_name.setFont(QFont("JetBrains Mono", 8))
#
#         self._result_value = QLabel("Place Holder")
#         self._result_value.setFont(QFont("JetBrains Mono", 8))
#
#         self._primary_layout = QHBoxLayout(primary_field_frame)
#         self._primary_layout.setContentsMargins(0, 0, 0, 0)
#
#         self._secondary_field_layout = QHBoxLayout(secondary_field_frame)
#         self._secondary_field_layout.addWidget(self._result_value)
#         self._secondary_field_layout.setContentsMargins(10, 2, 10, 2)
#
#         self._primary_layout.addSpacing(10)
#         self._primary_layout.addWidget(self._result_name)
#         self._primary_layout.addSpacing(10)
#         self._primary_layout.addWidget(secondary_field_frame)
#
#         root_layout = QVBoxLayout(self)
#         root_layout.addWidget(primary_field_frame)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#
# class QAnalysisTab(QWidget):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._progress_bar = QProgressBar()
#         self._info_label = QLabel("     Durée estimée : 00:00:00")
#         self._info_label.setFont(QFont("JetBrains Mono", 7))
#
#         self._primary_layout = QVBoxLayout(self)
#         self._primary_layout.addWidget(self._progress_bar, alignment=Qt.AlignmentFlag.AlignTop)
#         self._primary_layout.addWidget(self._info_label, alignment=Qt.AlignmentFlag.AlignTop)
#
# class QOptimizationAnalysis(QAnalysisTab):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._performance_gain_field = QResultField("Gain de performance")
#         self._secondary_layout = QHBoxLayout()
#         self._secondary_layout.addWidget(self._performance_gain_field)
#         self._secondary_layout.addStretch()
#
#         self._primary_layout.addLayout(self._secondary_layout)
#         self._primary_layout.addStretch()
#
# class QResultAnalysis(QAnalysisTab):
#     def __init__(self, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._drag_coef_field = QResultField("Coefficient de traîné")
#         self._lift_coef_field = QResultField("Coefficient de portance")
#
#         self._secondary_layout = QHBoxLayout()
#         self._secondary_layout.addWidget(self._drag_coef_field)
#         self._secondary_layout.addWidget(self._lift_coef_field)
#         self._secondary_layout.addStretch()
#
#         self._primary_layout.addLayout(self._secondary_layout)
#         self._primary_layout.addStretch()
#
# class QAnalysisWidget(QFloatingWidget):
#     def __init__(self, initial_position: QPoint, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self.setMinimumWidth(600)
#         self.saved_position = initial_position
#
#         self._tabs = QTabWidget()
#         self._tabs.setProperty("class", "analysis_tabs")
#         self._tabs.tabBar().setProperty("class", "analysis_tabs")
#
#         self._optimization_tab = QOptimizationAnalysis()
#         self._tabs.addTab(self._optimization_tab, "Optimisation")
#
#         self._results_tab = QResultAnalysis()
#         self._tabs.addTab(self._results_tab, "Résultats")
#
#         self._tabs.setFont(QFont("JetBrains Mono", 12))
#
#         self._v_box_layout.addWidget(self._tabs)
#
#         self._tabs.currentChanged.connect(self.delayed_correct_position)
#
# class QFloatingSettingPB(QPushButton):
#     def __init__(self, txt: str, fill: bool = True, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self.setText(txt)
#         self.setFont(QFont("JetBrains Mono", 12))
#
#         if fill: self.setProperty("class", "apply_pb")
#         else: self.setProperty("class", "cancel_pb")
#
#         self.setFixedHeight(32)
#         self.setFixedWidth(120)
#
# class QFloatingContent(QFloatingWidget):
#     def __init__(self, title: str, parent: QWidget | None = None):
#         super().__init__(parent)
#
#         self._title_label = QLabel(title)
#
#         font = QFont("JetBrains Mono", 12)
#         font.setBold(True)
#         self._title_label.setFont(font)
#
#         self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#
#         self._apply_pb = QFloatingSettingPB("Appliquer")
#         self._cancel_pb = QFloatingSettingPB("Annuler", fill=False)
#
#         self._lower_h_layout = QHBoxLayout()
#         self._lower_h_layout.addStretch()
#         self._lower_h_layout.addWidget(self._apply_pb, alignment=Qt.AlignmentFlag.AlignRight)
#         self._lower_h_layout.addWidget(self._cancel_pb, alignment=Qt.AlignmentFlag.AlignRight)
#
#         self._v_box_layout.addWidget(self._title_label, alignment=Qt.AlignmentFlag.AlignTop)
#         self._v_box_layout.addStretch()
#         self._v_box_layout.addLayout(self._lower_h_layout)
#
# class QFloatingWarning(QFloatingContent):
#     showing = Signal(bool)
#
#     def __init__(self, initial_position: QPoint, title: str, warning_text: str, parent: QWidget | None = None):
#         super().__init__(title, parent)
#         self.setMinimumSize(300, 150)
#
#         center_point = QPoint(int(initial_position.x() - self.width()/2 - 40), int(initial_position.y() - self.height()/2))
#         self.saved_position = center_point
#
#         self._warning_text = warning_text
#         self._warning_label: QLabel = QLabel(self._warning_text)
#         self._warning_label.setFont(QFont("JetBrains Mono", 9))
#         self._v_box_layout.insertWidget(2, self._warning_label, alignment=Qt.AlignmentFlag.AlignCenter)
#
#     @property
#     def warning_text(self) -> str:
#         return self._warning_text
#     @warning_text.setter
#     def warning_text(self, text: str):
#         self._warning_text = text
#         self._warning_label.setText(self._warning_text)
#
#     def showEvent(self, event: QShowEvent) -> None:
#         self.showing.emit(True)
#
#     def hideEvent(self, event: QHideEvent) -> None:
#         self.showing.emit(False)
#
# if __name__ == "__main__":
#     app = QApplication([])
#     window = QMainWindow()
#     main = QFloatingContent("PlaceHolder", window)
#     window.show()
#     app.exec()
