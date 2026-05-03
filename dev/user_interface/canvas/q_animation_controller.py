from enum import Enum
from unittest import case

from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtGui import QPixmap, QIcon, Qt, QFont
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout

from dev.physics_engine.pixmap_gen import PixmapGen


class SimImageType(Enum):
    VELOCITY_HEAT = 0
    DENSITY_HEAT = 1
    CURL = 2
    STREAM = 3
    VELOCITY_HEAT_STREAM = 4
    DENSITY_HEAT_STREAM = 5
    VELOCITY_HEAT_CURL = 6
    DENSITY_HEAT_CURL = 7

class QSimController(QWidget):
    showPixmapRequested = Signal(QPixmap)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self.setFixedSize(300, 40)
        self._canvas_height: int = 1080
        self._canvas_width: int = 1920
        self._timer = QTimer(self)
        self._fps = 30

        # Data
        self._max_soft_steps = 400
        self._max_hard_steps = 1000
        self._sim_data = {}
        self._current_step = 0
        self._image_type = SimImageType.VELOCITY_HEAT

        # Layout
        self._primary_frame = QFrame()
        self._primary_frame.setProperty("class", "controller_frame")
        self._primary_layout = QHBoxLayout(self._primary_frame)
        self._primary_layout.setContentsMargins(5, 5, 5, 5)

        # Resume/pause button
        self._control_button = QPushButton()
        self._control_button.setCheckable(True)
        self._control_button.setProperty("class", "controller_pb")
        self._play_icon = QIcon(":/res/play_icon_black.png")
        self._pause_icon = QIcon(":/res/pause_icon_black.png")
        self._control_button.setIcon(self._play_icon)
        self._control_button.setFixedSize(26, 26)

        # Slider
        self._slider = QSlider()
        self._slider.setOrientation(Qt.Orientation.Horizontal)
        self._slider.setProperty("class", "controller_slider")
        self._slider.setFixedSize(200, 26)
        self._slider.setMaximum(self._max_hard_steps)
        self._slider.setMinimum(1)

        # Label
        self._label = QLabel()
        font = QFont("JetBrains Mono", 10)
        self._label.setFont(font)
        self._label.setProperty("class", "controller_label")
        self._label.setFixedSize(50, 16)
        self._label.setText("00:00")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._primary_layout.addWidget(self._control_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.addWidget(self._slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._primary_layout.addStretch()
        self._primary_layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignRight)
        self._primary_layout.setSpacing(10)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self._primary_frame)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Connections
        self._control_button.pressed.connect(self._on_control_button_pressed)
        self._timer.timeout.connect(self._send_sim_pixmap)
        self._slider.valueChanged.connect(self._on_slider_value_changed)

    @Slot(int)
    def _on_slider_value_changed(self, value: int):
        self._update_label(value)

        if not self._control_button.isChecked():
            self._send_sim_pixmap()

    def _update_label(self, value: int):
        total_seconds = value // self._fps
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        self._label.setText(f"{minutes:02d}:{seconds:02d}")

    @Slot()
    def _on_control_button_pressed(self):
        if self._control_button.isChecked():
            # Pause requested
            self._control_button.setIcon(self._play_icon)
            self._timer.stop()
        else:
            # Play requested
            self._control_button.setIcon(self._pause_icon)
            self._timer.start(1000 // self._fps)

    @Slot(list)
    def add_sim_data(self, data: list):
        grid = data[0]
        obstacle = data[1]
        step = data[2]

        self._sim_data[str(step)] = [grid, obstacle]
        self._slider.setMaximum(step)

    @Slot()
    def _send_sim_pixmap(self):
        step = self._slider.value()
        if self._control_button.isChecked(): self._slider.setValue(step + 1)

        grid = self._sim_data[str(step)][0]
        obstacle = self._sim_data[str(step)][1]

        match self._image_type:
            case SimImageType.VELOCITY_HEAT:
                pixmap = PixmapGen.generate_heatmap(grid, obstacle)
            case SimImageType.DENSITY_HEAT:
                pixmap = PixmapGen.generate_density(grid, obstacle)
            case SimImageType.CURL:
                pixmap = PixmapGen.generate_curl(grid, obstacle)
            case SimImageType.STREAM:
                pixmap = PixmapGen.generate_stream(grid, obstacle)
            case SimImageType.VELOCITY_HEAT_STREAM:
                raise NotImplementedError("Velocity heat stream pixmap not implemented yet")
            case SimImageType.DENSITY_HEAT_STREAM:
                raise NotImplementedError("Density heat stream pixmap not implemented yet")
            case SimImageType.VELOCITY_HEAT_CURL:
                raise NotImplementedError("Velocity heat curl pixmap not implemented yet")
            case SimImageType.DENSITY_HEAT_CURL:
                raise NotImplementedError("Density heat curl pixmap not implemented yet")
            case _:
                raise ValueError("Unknown image type")

        self.showPixmapRequested.emit(pixmap)

    @property
    def canvas_width(self) -> int:
        return self._canvas_width
    @canvas_width.setter
    def canvas_width(self, width: int):
        self._canvas_width = width

    @property
    def fps(self) -> int:
        return self._fps
    @fps.setter
    def fps(self, fps: int):
        self._fps = fps

    @property
    def image_type(self) -> SimImageType:
        return self._image_type
    @image_type.setter
    def image_type(self, image_type: SimImageType):
        self._image_type = image_type