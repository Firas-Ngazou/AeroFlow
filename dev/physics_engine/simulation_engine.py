import math
from datetime import time, datetime

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage, qRgb

from dev.physics_engine.lattice_grid import LatticeGrid, D2Q9Constants
from dev.physics_engine.vector_obstacle import  VectorObstacle

class SimulationEngine(QObject):
    progressUpdated = Signal(int)
    streamFrameFinished = Signal(QPixmap)
    heatmapFrameFinished = Signal(QPixmap)
    statusMessageUpdated = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._grid: LatticeGrid | None = None
        self._obstacle = VectorObstacle()
        self._tau = 0.6
        self._boltzmann_k = 1.38 * (10 ** -23)
        self._air_particle_mass = 4.81 * (10 ** -26)
        self._room_temperature = 293
        self._current_step: int = 0
        self._max_step: int = 10
        self._resolution_x: int = 1689
        self._resolution_y: int = 950

        self._allocation = 5000
        self._estimate_time = 0

        self._frame_start_time = datetime.now()
        self._frame_end_time = datetime.now()
        self._last_times = np.array([])

        self._constants = D2Q9Constants()

        self._background: QPixmap | None = None

    def run(self, data: list[float | int]):
        self._max_step = self._evaluate_max_step()
        # self._max_step = 10

        initial_velocity = data[0]
        initial_res = data[1]

        self._obstacle.initial_res = initial_res

        self._resolution_x = self._obstacle.binary_mask.shape[0]
        self._resolution_y = self._obstacle.binary_mask.shape[1]

        boltzmann_velocity = self._get_boltzmann_v(initial_velocity)
        self._initialize(boltzmann_velocity)
        self._execute_time_step()

    def _get_boltzmann_v(self, initial_velocity: float):
        factor = math.sqrt(2 * self._boltzmann_k * self._room_temperature / self._air_particle_mass)
        return initial_velocity / factor

    def _initialize(self, initial_velocity: float):
        self._grid = LatticeGrid(self._resolution_x, self._resolution_y)
        self._grid.macro_velocity_x[:, :] = initial_velocity
        self._grid.macro_density[:, :] = 1.0

        f_eq = self._get_f_eq()

        self._grid.distributions = f_eq

    def _execute_time_step(self):
        for _ in range(self._max_step):
            self._frame_start_time = datetime.now()
            self.__apply_streaming()
            self.__apply_boundaries()
            self._grid.update_macroscopic()
            self.__apply_collision()
            self.__end_current_frame()

    def _evaluate_max_step(self):
        width = self._resolution_x
        height = self._resolution_y

        # 16-bits
        size_bytes = (width * height * 2) + height + 100
        size = size_bytes / 1024 / 1024
        return math.ceil(self._allocation / size)

    def calculate_drag_coef(self):
        ...

    def calculate_lift_coef(self):
        ...

    def __apply_streaming(self):
        new_f = np.zeros_like(self._grid.distributions)
        for i in range(9):
            new_f[:, :, i] = np.roll(self._grid.distributions[:, :, i],
                                     (self._constants.E_X[i], self._constants.E_Y[i]), axis=(0, 1))

        self._grid.distributions = new_f

    def __apply_collision(self):

        # on trouve les valeurs de f_eq pour chaque distribution
        f_eq = self._get_f_eq()

        # application du facteur de relaxation
        self._grid.distributions += (1/self._tau)*(f_eq - self._grid.distributions)


    def __apply_boundaries(self):
        temp_distributions = np.copy(self._grid.distributions)
        for i in range(9):
            opposite = self._constants.OPPOSITES[i]
            # on bouge les particules dans le coter opposee
            self._grid.distributions[self._obstacle.binary_mask, i] = temp_distributions[self._obstacle.binary_mask,
            opposite]

    def _get_f_eq(self):
        f_eq = np.zeros_like(self._grid.distributions)
        last_term = (self._grid.macro_velocity_x ** 2 +
                     self._grid.macro_velocity_y ** 2)
        for i in range(9):
            term_2 = (self._constants.E_X[i] * self._grid.macro_velocity_x +
                      self._constants.E_Y[i] * self._grid.macro_velocity_y)

            f_eq[:, :, i] = (self._constants.WEIGHTS[i] * self._grid.macro_density *
                             (1 + (3 * term_2) + (4.5 * term_2 ** 2) - (1.5 * last_term)))

        return f_eq

    def __end_current_frame(self):
        self._current_step += 1

        progress = int((self._current_step / self._max_step) * 100)
        self.progressUpdated.emit(progress)
        self.__update_status_message()

        heatmap = self._generate_heatmap()
        # stream_lines = self._generate_stream()

        self.heatmapFrameFinished.emit(heatmap)
        # self.streamFrameFinished.emit(stream_lines)

    def __update_status_message(self):
        self._frame_end_time = datetime.now()
        delta_time = self._frame_end_time - self._frame_start_time
        self._last_times = np.append(self._last_times, delta_time)
        mean_time = np.mean(self._last_times)
        time_left = mean_time * (self._max_step - self._current_step)
        formatted_time = str(time_left).split('.')[0]

        self.statusMessageUpdated.emit(f"Temps restant: {formatted_time}")

    def _generate_heatmap(self):
        speeds = np.sqrt(self._grid.macro_velocity_x**2 + self._grid.macro_velocity_y**2)

        if self._obstacle.binary_mask is not None:
            speeds[self._obstacle.binary_mask] = 0

        max_speed = np.max(speeds)
        if max_speed == 0:
            max_speed = 1

        normalized_speeds = np.clip((speeds / max_speed) * 255, 0, 255).astype(np.uint8)

        image_data = np.ascontiguousarray(normalized_speeds.T)
        height, width = image_data.shape
        bytes_per_line = width

        temp_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_Indexed8)

        color_table = []
        for i in range(256):
            f = i / 255.0
            r = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.5)))))
            g = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.25)))))
            b = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * f))))
            color_table.append(qRgb(r, g, b))

        temp_image.setColorTable(color_table)

        image = temp_image.copy()
        return QPixmap.fromImage(image)

    def _generate_stream(self):
        ...

    def set_reduction_factor(self, factor: float):
        self._obstacle.reduction_factor = factor

    @property
    def vertices(self):
        return self._obstacle.vertices

    @vertices.setter
    def vertices(self, vertices: np.ndarray):
        self._obstacle.vertices = vertices

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, background: QPixmap):
        self._background = background

    @property
    def allocation(self):
        return self._allocation

    @allocation.setter
    def allocation(self, allocation: int):
        self._allocation = allocation