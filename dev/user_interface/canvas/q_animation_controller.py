from datetime import datetime
from enum import Enum
import h5py
import threading
import queue
import numpy as np

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
    stepLoadedFromDisk = Signal(int, np.ndarray)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self.setFixedSize(380, 40)
        self._timer = QTimer(self)
        self._fps = 30
        self._canvas_height = 1080
        self._canvas_width = 1920
        self._reduction_factor = 1.0

        # Data
        self._max_soft_steps = 600
        self._max_soft_ratio = 0.6
        self._max_steps = 1000
        self._sim_data = {}
        self._image_type = SimImageType.STREAM # Curl ???

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
        self._slider.setMinimum(1)

        # Time label
        self._label = QLabel()
        font = QFont("JetBrains Mono", 10)
        self._label.setFont(font)
        self._label.setFixedSize(50, 16)
        self._label.setText("00:00")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # FPS label
        self._fps_label = QLabel()
        self._fps_label.setFont(font)
        self._fps_label.setFixedSize(60, 16)
        self._fps_label.setText("30 FPS")
        self._fps_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._update_fps = False

        self._primary_layout.addWidget(self._control_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.addWidget(self._slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._primary_layout.addStretch()
        self._primary_layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignRight)
        self._primary_layout.addWidget(self._fps_label, alignment=Qt.AlignmentFlag.AlignRight)
        self._primary_layout.setSpacing(10)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self._primary_frame)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Connections
        self._control_button.pressed.connect(self._on_control_button_pressed)
        self._timer.timeout.connect(self._send_sim_pixmap)
        self._slider.valueChanged.connect(self._on_slider_value_changed)
        self.stepLoadedFromDisk.connect(self._on_step_loaded_from_disk)

        # h5py
        self._h5py_file = None
        self._dataset = None

        # I/O
        self._lock = threading.Lock()
        self._io_write_queue = queue.Queue()
        self._io_read_queue = queue.Queue()

        self._io_write_thread = threading.Thread(target=self._io_write_worker, daemon=True)
        self._io_write_thread.start()

        self._io_read_thread = threading.Thread(target=self._io_read_worker, daemon=True)
        self._io_read_thread.start()

    def _io_write_worker(self):
        while True:
            step, data = self._io_write_queue.get()
            with self._lock:
                if self._dataset is not None:
                    # if self._dataset.shape[0] <= step:
                        # self._dataset.resize(step + 1, axis=0)
                    self._dataset[step] = data

            self._io_write_queue.task_done()

    def _io_read_worker(self):
        while True:
            step = self._io_read_queue.get()
            if step in self._sim_data:
                self._io_read_queue.task_done()
                continue

            with self._lock:
                if self._dataset is None or self._dataset.shape[0] <= step:
                    self._io_read_queue.task_done()
                    continue
                stacked_data = self._dataset[step]

            self.stepLoadedFromDisk.emit(step, stacked_data)
            self._io_read_queue.task_done()

    @Slot(int)
    def _on_slider_value_changed(self, value: int):
        self._update_label(value)
        self._update_sim_data()

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
            self._update_fps = False
        else:
            # Play requested
            self._control_button.setIcon(self._pause_icon)
            self._timer.start(1000 // self._fps)
            self._update_fps = True

    @Slot(list)
    def add_sim_data(self, data: list):
        stacked_data = data[0]
        step = data[1]

        _, _, _, mask = np.unstack(stacked_data, axis=-1)

        if self._h5py_file is None:
            self._initiate_cache(mask.shape[0], mask.shape[1])

        self._sim_data[step] = [stacked_data]
        self._slider.setMaximum(step)

    @Slot()
    def _send_sim_pixmap(self):
        signal_start = datetime.now()
        step = self._slider.value()
        if step not in self._sim_data: return

        if self._control_button.isChecked(): self._slider.setValue(step + 1)

        stacked_data = self._sim_data[step][0]

        w = int(self._canvas_width * self._reduction_factor)
        h = int(self._canvas_height * self._reduction_factor)

        match self._image_type:
            case SimImageType.VELOCITY_HEAT:
                pixmap = PixmapGen.generate_heatmap(stacked_data, h, w)
            case SimImageType.DENSITY_HEAT:
                pixmap = PixmapGen.generate_density(stacked_data, h, w)
            case SimImageType.CURL:
                pixmap = PixmapGen.generate_curl(stacked_data, h, w)
            case SimImageType.STREAM:
                pixmap = PixmapGen.generate_stream(stacked_data, h, w)
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

        if self._update_fps and not self._slider.value() == self._max_steps:
            signal_end = datetime.now()
            delta_time_s = (signal_end - signal_start).total_seconds()
            self._fps_label.setText(f"{(1/delta_time_s):.0f} FPS")

    def _initiate_cache(self, width: int, height: int):
        with self._lock:
            optimal_chunk = (1, width, height, 4)

            self._h5py_file = h5py.File("sim_cache.h5", "w")
            self._dataset = self._h5py_file.create_dataset("sim_data", (self._max_steps + 1, width, height, 4),
                                                           maxshape=(None, width, height, 4),
                                                           dtype=np.float32,
                                                           chunks=optimal_chunk, compression="lzf")

    def _update_sim_data(self):
        current_step = self._slider.value()
        left_soft = max(current_step - self._max_soft_steps//2, 1)
        right_soft = min(current_step + self._max_soft_steps//2, self._slider.maximum())

        left_hard = None
        right_hard = None
        if left_soft != 1:
            left_hard = 1 + current_step - left_soft
        if right_soft != self._slider.maximum():
            right_hard = self._slider.maximum() - (right_soft + current_step)

        if left_hard is not None:
            for step in range(1, left_hard):
                self._save_step_to_disk(step)

        if right_hard is not None:
            for step in range(right_soft, self._slider.maximum() + 1):
                self._save_step_to_disk(step)

        with self._io_read_queue.mutex:
            self._io_read_queue.queue.clear()

        for step in range(left_soft, right_soft):
            self._make_soft(step)

    def _save_step_to_disk(self, step: int):
        if step not in self._sim_data: return
        stacked_data = self._sim_data[step][0]

        self._io_write_queue.put((step, stacked_data))

        self._sim_data.pop(step)

    def _make_soft(self, step: int):
        if step in self._sim_data: return

        self._io_read_queue.put(step)

    @Slot(int, np.ndarray)
    def _on_step_loaded_from_disk(self, step: int, stacked_data: np.ndarray):
        self._sim_data[step] = [stacked_data]

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

    @property
    def canvas_height(self) -> int:
        return self._canvas_height
    @canvas_height.setter
    def canvas_height(self, canvas_height: int):
        self._canvas_height = canvas_height

    @property
    def canvas_width(self) -> int:
        return self._canvas_width
    @canvas_width.setter
    def canvas_width(self, canvas_width: int):
        self._canvas_width = canvas_width

    @Slot(float)
    def set_reduction_factor(self, value: float):
        self._reduction_factor = value

    @property
    def max_steps(self):
        return self._max_steps

    @max_steps.setter
    def max_steps(self, max_steps: int):
        self._max_steps = max_steps
        self._max_soft_steps = int(max_steps * self._max_soft_ratio)

    @Slot(int)
    def set_max_steps(self, max_steps: int):
        self.max_steps = max_steps

    def reset(self):
        self._slider.setValue(1)
        self._update_label(0)
        self._control_button.setChecked(False)
        self._control_button.setIcon(self._play_icon)
        self._timer.stop()
        self._sim_data.clear()

        with self._io_write_queue.mutex:
            self._io_write_queue.queue.clear()
        with self._io_read_queue.mutex:
            self._io_read_queue.queue.clear()

        with self._lock:
            if self._h5py_file is not None:
                self._h5py_file.close()

            self._h5py_file = None
            self._dataset = None