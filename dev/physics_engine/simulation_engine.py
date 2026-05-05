import copy
import math
from datetime import time, datetime

import numpy as np
from PySide6.QtCore import QObject, Signal, Qt, QThread
from PySide6.QtGui import QPixmap, QImage, qRgba, QPainter, QPen, QColor

from dev.physics_engine.lattice_grid import LatticeGrid, D2Q9Constants
from dev.physics_engine.vector_obstacle import  VectorObstacle

class SimulationEngine(QObject):
    progressUpdated = Signal(int)
    statusMessageUpdated = Signal(str)
    iterationCompleted = Signal(list)
    maxSoftStepUpdated = Signal(int)
    dragCoefUpdated = Signal(float)
    liftCoefUpdated = Signal(float)

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

        self._current_drag_force: float = 0.0
        self._current_lift_force: float = 0.0
        self._u_ref: float = 0.0
        self._rho_ref: float = 1.0

    def run(self, data: list[float | int]):
        initial_velocity = data[0]
        initial_res = data[1]

        self._obstacle.initial_res = initial_res

        self._resolution_x = self._obstacle.binary_mask.shape[0]
        self._resolution_y = self._obstacle.binary_mask.shape[1]

        self._max_step = self._evaluate_max_soft_step()

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

        self._u_ref = initial_velocity
        self._rho_ref = 1.0

        f_eq = self._get_f_eq()
        self._grid.distributions = f_eq

        for i in range(9):
            self._grid.distributions[self._obstacle.binary_mask, i] = 0.0

        self._grid.macro_velocity_x[self._obstacle.binary_mask] = 0.0
        self._grid.macro_velocity_y[self._obstacle.binary_mask] = 0.0
        self._grid.macro_density[self._obstacle.binary_mask] = 0.0

    def _execute_time_step(self):
        for _ in range(self._max_step):
            if QThread.currentThread().isInterruptionRequested():
                break
            self._frame_start_time = datetime.now()
            self.__apply_streaming()
            self.__apply_boundaries()
            self._grid.update_macroscopic()
            self.__apply_collision()
            self.__end_current_frame()

    def _evaluate_max_soft_step(self):
        width = self._resolution_x
        height = self._resolution_y

        bytes_per_float32 = 4
        densities_bytes = width * height * 9 * bytes_per_float32 * 2
        mb_densities = densities_bytes / (1024 * 1024)

        velocity_bytes = width * height * 3 * bytes_per_float32
        mb_velocity = velocity_bytes / (1024 * 1024)

        safe_allocation = self._allocation * 0.8

        estimation = int(safe_allocation / (mb_densities + mb_velocity))
        self.maxSoftStepUpdated.emit(estimation)
        return estimation

    def _calculate_drag_coef(self):
        # C_D = F_D / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks()
        if area == 0:
            return 0.0

        coef = self._current_drag_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _calculate_lift_coef(self):
        # C_L = F_L / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks()
        if area == 0:
            return 0.0

        coef = self._current_lift_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _coef_initial_checks(self):
        mask_y = np.where(self._obstacle.binary_mask)[1]
        if len(mask_y) > 0:
            area = int(np.max(mask_y)) - int(np.min(mask_y) + 1)
        else:
            return 0.0
        if self._u_ref == 0:
            return 0.0

        return area

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
        relaxation = (1/self._tau)*(f_eq - self._grid.distributions)

        for i in range(9):
            relaxation[self._obstacle.binary_mask, i] = 0.0

        self._grid.distributions += relaxation


    def __apply_boundaries(self):
        temp_distributions = np.copy(self._grid.distributions)

        momentum_x_before = 0.0
        momentum_y_before = 0.0

        for i in range(9):
            f_in = temp_distributions[self._obstacle.binary_mask, i]
            momentum_x_before += np.sum(f_in*self._constants.E_X[i])
            momentum_y_before += np.sum(f_in*self._constants.E_Y[i])

        self._current_drag_force = 2 * momentum_x_before
        self._current_lift_force = 2 * momentum_y_before

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

        macro_velocity_x = self._grid.macro_velocity_x
        macro_velocity_y = self._grid.macro_velocity_y
        macro_density = self._grid.macro_density
        binary_mask = self._obstacle.binary_mask

        stacked_data = np.stack((macro_velocity_x, macro_velocity_y, macro_density, binary_mask), axis=-1)

        drag_coef = self._calculate_drag_coef()
        lift_coef = self._calculate_lift_coef()
        data = [stacked_data, self._current_step]

        self.iterationCompleted.emit(data)
        self.dragCoefUpdated.emit(drag_coef)
        self.liftCoefUpdated.emit(lift_coef)

    def __update_status_message(self):
        self._frame_end_time = datetime.now()
        delta_time = self._frame_end_time - self._frame_start_time
        self._last_times = np.append(self._last_times, delta_time)
        mean_time = np.mean(self._last_times)
        time_left = mean_time * (self._max_step - self._current_step)
        formatted_time = str(time_left).split('.')[0]

        self.statusMessageUpdated.emit(f"Temps restant: {formatted_time}")

    def reset(self):
        self._grid = None
        self._current_step = 0
        self._last_times = np.array([])
        self._frame_start_time = datetime.now()
        self._frame_end_time = datetime.now()
        self._estimate_time = 0
        self.progressUpdated.emit(0)
        self.statusMessageUpdated.emit("Temps restant: 00:00:00")
        self.dragCoefUpdated.emit(0.0)
        self.liftCoefUpdated.emit(0.0)

    def set_reduction_factor(self, factor: float):
        self._obstacle.reduction_factor = factor

    @property
    def vertices(self):
        return self._obstacle.vertices

    @vertices.setter
    def vertices(self, vertices: np.ndarray):
        self._obstacle.vertices = vertices

    @property
    def allocation(self):
        return self._allocation

    @allocation.setter
    def allocation(self, allocation: int):
        self._allocation = allocation

    @property
    def resolution_x(self):
        return self._resolution_x
    @resolution_x.setter
    def resolution_x(self, resolution_x: int):
        self._resolution_x = resolution_x

    @property
    def resolution_y(self):
        return self._resolution_y
    @resolution_y.setter
    def resolution_y(self, resolution_y: int):
        self._resolution_y = resolution_y