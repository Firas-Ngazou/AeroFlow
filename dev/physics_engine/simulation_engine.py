import math
from datetime import time, datetime

import numpy as np
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QPixmap, QImage, qRgba, QPainter, QPen, QColor

from dev.physics_engine.lattice_grid import LatticeGrid, D2Q9Constants
from dev.physics_engine.vector_obstacle import  VectorObstacle

class SimulationEngine(QObject):
    progressUpdated = Signal(int)
    streamFrameFinished = Signal(QPixmap)
    heatmapFrameFinished = Signal(list)
    statusMessageUpdated = Signal(str)
    heatmapFinished = Signal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._grid: LatticeGrid | None = None
        self._obstacle = VectorObstacle()
        self._tau = 0.8
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
        # self._max_step = 1

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

        self.heatmapFinished.emit()

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

        heatmap = self._generate_curl()
        # stream_lines = self._generate_stream()

        self.heatmapFrameFinished.emit([heatmap, self._current_step])
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

        unaffected = speeds.shape[1]//2
        base_speed = speeds[0, unaffected]

        if self._obstacle.binary_mask is not None:
            speeds[self._obstacle.binary_mask] = 0

        max_speed = np.max(speeds)
        if max_speed == 0:
            max_speed = 1

        base_index = int((base_speed / max_speed) * 255)
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

            if i == 0:
                alpha = 0

            else:
                difference = abs(i - base_index)
                alpha = int(np.clip(difference * difference, 0, 255))

            color_table.append(qRgba(r, g, b, alpha))

        temp_image.setColorTable(color_table)
        heatmap_pixmap = QPixmap.fromImage(temp_image.copy())

        final_pixmap = QPixmap(self._background.size())
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, self._background)

        painter.drawPixmap(final_pixmap.rect(), heatmap_pixmap)
        painter.end()

        return final_pixmap

    def _generate_stream(self):
        velocity_x = self._grid.macro_velocity_x
        velocity_y = self._grid.macro_velocity_y

        width_grid = velocity_x.shape[0]
        height_grid = velocity_y.shape[1]

        final_pixmap = QPixmap(self._background.size())
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, self._background)

        pen = QPen(QColor(230, 230, 230, 150))
        pen.setWidth(2)
        painter.setPen(pen)

        spacing_y = 30 # la distance entre les lignes
        max_steps = 1920 # resolution max
        min_speed = 1e-8
        step_size = 3.0

        scale_x = self._background.width() / width_grid
        scale_y = self._background.height() / height_grid

        # for start_x in range(0, width_grid, spacing_x):
        for start_y in range(spacing_y//2, height_grid, spacing_y):
            x = 0.0
            y = float(start_y)

            last_x = None
            last_y = None

            for _ in range(max_steps):
                if not np.isfinite(x) or not np.isfinite(y):
                    break

                rounded_x = int(round(x))
                rounded_y = int(round(y))

                if rounded_x < 0 or rounded_x >= width_grid:
                    break

                if rounded_y < 0 or rounded_y >= height_grid:
                    break

                if self._obstacle.binary_mask[rounded_x, rounded_y]:
                    break

                vx = velocity_x[rounded_x, rounded_y]
                vy = velocity_y[rounded_x, rounded_y]
                speed = math.sqrt(vx**2 + vy**2)

                # if speed < min_speed:
                #     break

                screen_x = int(scale_x*x)
                screen_y = int(scale_y*y)

                if last_x is not None and last_y is not None:
                    painter.drawLine(last_x, last_y, screen_x, screen_y)

                last_x = rounded_x
                last_y = rounded_y

                x += (vx/speed)*step_size
                y += (vy/speed)*step_size

        painter.end()

        return final_pixmap

    def _generate_density(self):
        densities = np.copy(self._grid.macro_density)

        unaffected = densities.shape[1]//2
        base_density = densities[0, unaffected]

        if self._obstacle.binary_mask is not None:
            densities[self._obstacle.binary_mask] = base_density

        density_difference = densities - base_density
        max_difference = np.max(np.abs(density_difference))

        if max_difference == 0:
            max_difference = 1

        normalized_densities = np.clip(((density_difference/max_difference)*127) + 127, 0, 255).astype(np.uint8)
        image_data = np.ascontiguousarray(normalized_densities.T)
        height, width = image_data.shape
        bytes_per_line = width

        temp_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_Indexed8)

        color_table = []
        base_index = 127
        for i in range(256):
            difference = abs(i - base_index)
            strength = difference/127

            gray = int(255*strength)
            alpha = int(np.clip(difference**2, 0, 255))
            color_table.append(qRgba(gray, gray, gray, alpha))

        temp_image.setColorTable(color_table)
        stream_pixmap = QPixmap.fromImage(temp_image.copy())

        final_pixmap = QPixmap(self._background.size())
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, self._background)
        painter.drawPixmap(final_pixmap.rect(), stream_pixmap)
        painter.end()

        return final_pixmap

    def _generate_curl(self):
        ux = self._grid.macro_velocity_x
        uy = self._grid.macro_velocity_y

        # curl = d(uy)/dx - d(ux)/dy
        curls = (np.roll(uy, -1, axis=0) - np.roll(uy, 1, axis=0) - np.roll(ux, -1, axis=1) + np.roll(ux, 1, axis=1))

        if self._obstacle.binary_mask is not None:
            curls[self._obstacle.binary_mask] = 0

        max_curl = np.max(np.abs(curls))

        if max_curl == 0:
            max_curl = 1

        normalized_curls = np.clip(((curls/max_curl)*127) + 127,0,255).astype(np.uint8)

        image_data = np.ascontiguousarray(normalized_curls.T)
        height, width = image_data.shape
        bytes_per_line = width

        temp_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_Indexed8)

        color_table = []
        base_index = 127
        for i in range(256):
            difference = abs(i - base_index)
            strength = difference / 127

            gray = int(255*strength)
            alpha = int(np.clip(difference**2, 0, 255))

            color_table.append(qRgba(gray, gray, gray, alpha))

        temp_image.setColorTable(color_table)
        curl_pixmap = QPixmap.fromImage(temp_image.copy())

        final_pixmap = QPixmap(self._background.size())
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, self._background)
        painter.drawPixmap(final_pixmap.rect(), curl_pixmap)
        painter.end()

        return final_pixmap

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