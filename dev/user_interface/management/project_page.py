import numpy as np
from PySide6.QtCore import Qt, Signal, QPoint, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame

from dev.user_interface.analysis.q_analysis_tabs import QAnalysisWidget
from dev.user_interface.floating.q_floating_content import QFloatingWarning
from dev.physics_engine.vector_obstacle import VectorObstacle
from dev.user_interface.canvas.q_state_manager import QStateManager
from dev.user_interface.canvas.q_editor import QEditor
from dev.user_interface.canvas.q_tool_bar import QToolBar
from dev.user_interface.management.q_custom_window_frame import FramelessWindow, QCustomTitleBar

class ProjectPage(QWidget):
    saveProject = Signal()
    homeRequested = Signal()
    constraintChanged = Signal(str)
    iterationsChanged = Signal(int)
    thresholdChanged = Signal(int)
    qualityChanged = Signal(float)
    windSpeedChanged = Signal(float)
    vectorDrawingChanged = Signal(np.ndarray)

    def __init__(self, parent: FramelessWindow):
        super().__init__(parent)

        self._initial_res = 1080
        self.resize(int((16/9)*self._initial_res), self._initial_res)
        self.setMinimumWidth(450)

        self._editor: QEditor
        self._state_manager = QStateManager(self)
        self._window = parent

        self._title_bar: QCustomTitleBar = self._window.titleBar

        self.__initialize_canvas()
        self.__initialize_title_bar()
        self.__initialize_connections()

        self._primary_layout = QVBoxLayout(self)
        self._primary_layout.setContentsMargins(0, 0, 0, 0)
        self._primary_layout.addWidget(self._editor)

        self._holding_ctrl = False

    def __initialize_canvas(self):
        self._editor = QEditor(self._state_manager)
        self._editor.switch_cursor(QStateManager.CursorState.DEFAULT)

        self._tool_bar = QToolBar(self._state_manager)

        self._vector_obstacle = VectorObstacle(self._initial_res)

        self._lower_layout = QHBoxLayout()
        self._lower_layout.addWidget(self._tool_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._secondary_layout = QVBoxLayout(self._editor)
        self._secondary_layout.setContentsMargins(0, 0, 0, 0)
        self._secondary_layout.addStretch()
        self._secondary_layout.addLayout(self._lower_layout)

    def __initialize_title_bar(self):
        self._analysis_tab = QAnalysisWidget(QPoint(0, 0), self)
        self._analysis_tab.hide()

        self._save_warning = QFrame(self)
        self._save_warning.setObjectName("save_warning")
        self._save_warning.setStyleSheet("#save_warning { background-color: rgba(245, 245, 245, 70);}")
        self._save_warning.setFixedSize(self.width(), self.height())
        self._save_warning_window = QFloatingWarning(QPoint(int(self.width()/2), int(self.height()/2)),
                                                     "Attention",
                                                     "Quitter sans sauvegarder vos modifications "
                                                     "risque de\n"
                                                     "résulter en une perte totale de votre travail.\n\n"
                                                     "Souhaitez-vous sauvegarder vos modifications ?",
                                                     self._save_warning)
        self._save_warning.hide()

        self._secondary_layout.insertWidget(0, self._analysis_tab, 0,
                                            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._secondary_layout.insertWidget(2, self._save_warning, 0,
                                            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

    def __initialize_connections(self):
        self._tool_bar.constraintChanged.connect(self.constraintChanged.emit)
        self._tool_bar.iterationsChanged.connect(self.iterationsChanged.emit)
        self._tool_bar.thresholdChanged.connect(self.thresholdChanged.emit)
        self._tool_bar.qualityChanged.connect(self.qualityChanged.emit)
        self._tool_bar.windSpeedChanged.connect(self.windSpeedChanged.emit)
        self._editor.vectorDrawingChanged.connect(self.vectorDrawingChanged.emit)
        
        self._state_manager.cursorStateChanged.connect(self._editor.switch_cursor)
        self._state_manager.cursorStateChanged.connect(self._tool_bar.update_cursor_state)

        self._title_bar.analysisPressed.connect(lambda y: self._on_analysis_pressed(y))

        self.vectorDrawingChanged.connect(self._vector_obstacle.set_vertices)
        self.qualityChanged.connect(self._vector_obstacle.set_reduction_factor)

        self._save_warning_window.showing.connect(self._on_warning_showing)

    def keyPressEvent(self, event):
        self._editor.keyPressEvent(event)

        if event.key() == Qt.Key.Key_Control:
            self._holding_ctrl = True

        if event.key() == Qt.Key.Key_S and self._holding_ctrl:
            self.saveProject.emit()

    def keyReleaseEvent(self, event):
        self._editor.keyReleaseEvent(event)

    @Slot(bool)
    def _on_warning_showing(self, showing: bool):
        self._title_bar.setDisabled(showing)

        if showing:
            self._save_warning.show()
            if self._title_bar.is_analysis_checked:
                self._title_bar.is_analysis_checked = False
                self._analysis_tab.hide()
        else:
            self._save_warning.hide()

    @Slot(bool)
    def _on_analysis_pressed(self, pressed: bool):
        self._analysis_tab.show() if pressed else self._analysis_tab.hide()

    @property
    def title_bar(self) -> QCustomTitleBar:
        return self._title_bar

    @property
    def save_warning(self) -> QFrame:
        return self._save_warning

    @property
    def constraint_method(self) -> str:
        return self._tool_bar.constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint: str):
        self._tool_bar.constraint_method = constraint

    @property
    def threshold(self) -> int:
        return self._tool_bar.threshold
    @threshold.setter
    def threshold(self, threshold: int):
        self._tool_bar.threshold = threshold

    @property
    def iterations(self) -> int:
        return self._tool_bar.iterations
    @iterations.setter
    def iterations(self, iterations: int):
        self._tool_bar.iterations = iterations

    @property
    def quality(self) -> float:
        return self._tool_bar.quality
    @quality.setter
    def quality(self, quality: float):
        self._tool_bar.quality = quality

    @property
    def wind_speed(self) -> float:
        return self._tool_bar.wind_speed
    @wind_speed.setter
    def wind_speed(self, wind_speed: float):
        self._tool_bar.wind_speed = wind_speed