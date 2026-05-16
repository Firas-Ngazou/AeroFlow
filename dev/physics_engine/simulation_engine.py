import copy
import math
from datetime import time, datetime

import numpy as np
from PySide6.QtCore import QObject, Signal, Qt, QThread, Slot
from PySide6.QtGui import QPixmap, QImage, qRgba, QPainter, QPen, QColor

from dev.physics_engine.lattice_grid import LatticeGrid, D2Q9Constants
from dev.physics_engine.vector_obstacle import  VectorObstacle

class SimulationEngine(QObject):
    progressUpdated = Signal(int)
    statusMessageUpdated = Signal(str)
    iterationCompleted = Signal(list)
    maxStepUpdated = Signal(int)
    dragCoefUpdated = Signal(float)
    liftCoefUpdated = Signal(float)
    finished = Signal()

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

        # Live-edit settings
        self._live_edit = False
        self._pause_requested = False
        self._previous_obstacle_mask: np.ndarray | None = None

    def run(self, data: list[float | int]):
        initial_velocity = data[0]
        initial_res = data[1]

        self._obstacle.initial_res = initial_res

        self._resolution_x = self._obstacle.binary_mask.shape[0]
        self._resolution_y = self._obstacle.binary_mask.shape[1]

        if not self._live_edit: self._max_step = self._evaluate_max_steps()

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

        obstacle_mask = self._obstacle.binary_mask.copy()
        self._previous_obstacle_mask = obstacle_mask.copy()

        f_eq = self._get_f_eq()
        self._grid.distributions = f_eq

        for i in range(9):
            self._grid.distributions[obstacle_mask, i] = 0.0

        self._grid.macro_velocity_x[obstacle_mask] = 0.0
        self._grid.macro_velocity_y[obstacle_mask] = 0.0
        self._grid.macro_density[obstacle_mask] = 0.0

    def _execute_time_step(self):
        i = 0

        while i < self._max_step:
            if QThread.currentThread().isInterruptionRequested():
                self.reset()
                break

            if not self._pause_requested:
                if not self._live_edit: i += 1
                self._frame_start_time = datetime.now()

                obstacle_mask = self._apply_live_obstacle_changes()

                self.__apply_streaming()
                self.__apply_boundaries(obstacle_mask)
                self._grid.update_macroscopic()
                self.__apply_collision(obstacle_mask)
                self.__end_current_frame(obstacle_mask)

            else:
                QThread.currentThread().msleep(50)

        self.finished.emit()

    def _evaluate_max_steps(self):
        width = self._resolution_x
        height = self._resolution_y

        bytes_per_float32 = 4
        densities_bytes = width * height * 9 * bytes_per_float32 * 2
        velocity_bytes = width * height * 3 * bytes_per_float32

        mb_engine = (densities_bytes + velocity_bytes) / (1024**2)

        step_bytes = width * height * 4 * bytes_per_float32
        mb_per_step = step_bytes / (1024**2)

        safe_allocation = self._allocation * 0.8
        available_memory = safe_allocation - mb_engine

        estimation = int(available_memory / mb_per_step)
        self.maxStepUpdated.emit(estimation)
        return estimation

    def _calculate_drag_coef(self, obstacle_mask: np.ndarray):
        # C_D = F_D / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks(obstacle_mask)
        if area == 0:
            return 0.0

        coef = self._current_drag_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _calculate_lift_coef(self, obstacle_mask: np.ndarray):
        # C_L = F_L / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks(obstacle_mask)
        if area == 0:
            return 0.0

        coef = self._current_lift_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _coef_initial_checks(self, obstacle_mask: np.ndarray):
        mask_y = np.where(obstacle_mask)[1]
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

        self._grid.distributions[-1, :, :] = self._grid.distributions[-2, :, :]

        self._grid.macro_velocity_x[0, :] = self._u_ref
        self._grid.macro_velocity_y[0, :] = 0.0
        self._grid.macro_density[0, :] = self._rho_ref

        self._grid.macro_velocity_x[:, 0] = self._u_ref
        self._grid.macro_velocity_y[:, 0] = 0.0
        self._grid.macro_density[:, 0] = self._rho_ref

        self._grid.macro_velocity_x[:, -1] = self._u_ref
        self._grid.macro_velocity_y[:, -1] = 0.0
        self._grid.macro_density[:, -1] = self._rho_ref

        f_eq = self._get_f_eq()
        for i in range(9):
            self._grid.distributions[0, :, i] = f_eq[0, :, i]
            self._grid.distributions[:, 0, i] = f_eq[:, 0, i]
            self._grid.distributions[:, -1, i] = f_eq[:, -1, i]

    def __apply_collision(self, obstacle_mask: np.ndarray) -> None:
        """
        Applies the collision step of the LBM using BGK relaxation. - Generated by OpenAI's GPT 5.5
        """
        # on trouve les valeurs de f_eq pour chaque distribution
        f_eq = self._get_f_eq()

        # application du facteur de relaxation
        relaxation = (1/self._tau)*(f_eq - self._grid.distributions)

        for i in range(9):
            relaxation[obstacle_mask, i] = 0.0

        self._grid.distributions += relaxation


    def __apply_boundaries(self, obstacle_mask: np.ndarray) -> None:
        """
        Applies boundary conditions (bounce-back) and calculates forces. - Generated by OpenAI's GPT 5.5
        """
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
            self._grid.distributions[obstacle_mask, i] = temp_distributions[obstacle_mask, opposite]

    def _get_f_eq(self) -> np.ndarray:
        """
        Calculates the equilibrium distribution function. - Generated by OpenAI's GPT 5.5

        :return: The calculated equilibrium distribution.
        """
        f_eq = np.zeros_like(self._grid.distributions)
        last_term = (self._grid.macro_velocity_x ** 2 +
                     self._grid.macro_velocity_y ** 2)
        for i in range(9):
            term_2 = (self._constants.E_X[i] * self._grid.macro_velocity_x +
                      self._constants.E_Y[i] * self._grid.macro_velocity_y)

            f_eq[:, :, i] = (self._constants.WEIGHTS[i] * self._grid.macro_density *
                             (1 + (3 * term_2) + (4.5 * term_2 ** 2) - (1.5 * last_term)))

        return f_eq

    def __end_current_frame(self, obstacle_mask: np.ndarray) -> None:
        """
        Finalizes the current simulation step and emits relevant data. - Generated by OpenAI's GPT 5.5
        """
        self._current_step += 1

        progress = int((self._current_step / self._max_step) * 100)
        self.progressUpdated.emit(progress)
        self.__update_status_message()

        macro_velocity_x = self._grid.macro_velocity_x
        macro_velocity_y = self._grid.macro_velocity_y
        macro_density = self._grid.macro_density

        stacked_data = np.stack((macro_velocity_x, macro_velocity_y, macro_density, obstacle_mask), axis=-1)

        drag_coef = self._calculate_drag_coef()
        lift_coef = self._calculate_lift_coef()
        data = [stacked_data, self._current_step]

        self.iterationCompleted.emit(data)
        self.dragCoefUpdated.emit(drag_coef)
        self.liftCoefUpdated.emit(lift_coef)

    def __update_status_message(self) -> None:
        """
        Updates the status message with an estimate of the remaining time. - Generated by OpenAI's GPT 5.5
        """
        self._frame_end_time = datetime.now()
        delta_time = self._frame_end_time - self._frame_start_time
        self._last_times = np.append(self._last_times, delta_time)
        mean_time = np.mean(self._last_times)
        time_left = mean_time * (self._max_step - self._current_step)
        formatted_time = str(time_left).split('.')[0]

        self.statusMessageUpdated.emit(f"Temps restant: {formatted_time}")

    def reset(self) -> None:
        """
        Resets the simulation engine state. - Generated by OpenAI's GPT 5.5
        """
        self._grid = None
        self._current_step = 0
        self._last_times = np.array([])
        self._frame_start_time = datetime.now()
        self._frame_end_time = datetime.now()
        self._estimate_time = 0
        self.dragCoefUpdated.emit(0.0)
        self.liftCoefUpdated.emit(0.0)
        self.progressUpdated.emit(0)
        self.statusMessageUpdated.emit("Temps restant: 00:00:00")

    def set_reduction_factor(self, factor: float) -> None:
        """
        Sets the reduction factor for the obstacle. - Generated by OpenAI's GPT 5.5

        :param factor: The reduction factor to set.
        """
        self._obstacle.reduction_factor = factor

    def _apply_live_obstacle_changes(self):
        obstacle_mask = self._obstacle.binary_mask.copy()

        if self._previous_obstacle_mask is None:
            self._previous_obstacle_mask = obstacle_mask.copy()
            return obstacle_mask

        if obstacle_mask.shape is not self._previous_obstacle_mask.shape:
            self._previous_obstacle_mask = obstacle_mask.copy()
            return obstacle_mask

        became_solid = obstacle_mask & ~self._previous_obstacle_mask
        became_air = self._previous_obstacle_mask & ~obstacle_mask

        if np.any(became_air):
            self._grid.macro_velocity_x[became_air] = self._u_ref
            self._grid.macro_velocity_y[became_air] = 0.0
            self._grid.macro_density[became_air] = self._rho_ref

            f_eq = self._get_f_eq()
            for i in range(9):
                self._grid.distributions[became_air, i] = f_eq[became_air, i]

        if np.any(became_solid):
            self._grid.macro_velocity_x[became_solid] = 0.0
            self._grid.macro_velocity_y[became_solid] = 0.0
            self._grid.macro_density[became_solid] = 0.0

            for i in range(9):
                self._grid.distributions[became_solid, i] = 0.0

        self._previous_obstacle_mask = obstacle_mask.copy()
        return obstacle_mask

    @property
    def vertices(self) -> np.ndarray:
        """
        Returns the vertices of the obstacle. - Generated by OpenAI's GPT 5.5
        """
        return self._obstacle.vertices

    @vertices.setter
    def vertices(self, vertices: np.ndarray) -> None:
        """
        Sets the vertices for the obstacle. - Generated by OpenAI's GPT 5.5
        """
        self._obstacle.vertices = vertices

    @property
    def allocation(self) -> int:
        """
        Returns the memory allocation for the simulation. - Generated by OpenAI's GPT 5.5
        """
        return self._allocation

    @allocation.setter
    def allocation(self, allocation: int) -> None:
        """
        Sets the memory allocation for the simulation. - Generated by OpenAI's GPT 5.5
        """
        self._allocation = allocation

    @property
    def resolution_x(self) -> int:
        """
        Returns the X resolution of the simulation. - Generated by OpenAI's GPT 5.5
        """
        return self._resolution_x
    @resolution_x.setter
    def resolution_x(self, resolution_x: int) -> None:
        """
        Sets the X resolution of the simulation. - Generated by OpenAI's GPT 5.5
        """
        self._resolution_x = resolution_x

    @property
    def resolution_y(self) -> int:
        """
        Returns the Y resolution of the simulation. - Generated by OpenAI's GPT 5.5
        """
        return self._resolution_y
    @resolution_y.setter
    def resolution_y(self, resolution_y: int) -> None:
        """
        Sets the Y resolution of the simulation. - Generated by OpenAI's GPT 5.5
        """
        self._resolution_y = resolution_y

    @property
    def viscosity(self) -> float | None:
        """
        Returns the viscosity of the simulation. - Generated by OpenAI's GPT 5.5
        """
        return
    @viscosity.setter
    def viscosity(self, viscosity: float) -> None:
        """
        Sets the viscosity and updates the relaxation time tau. - Generated by OpenAI's GPT 5.5
        """
        # viscosity = (1/3) * (tau - 0.5)
        # tau = (viscosity * 3) + 0.5
        self._tau = (viscosity * 3) + 0.5

    @property
    def live_edit(self):
        return self._live_edit
    @live_edit.setter
    def live_edit(self, live_edit: bool) -> None:
        self._live_edit = live_edit

    @property
    def pause_requested(self):
        return self._pause_requested
    @pause_requested.setter
    def pause_requested(self, pause_requested: bool) -> None:
        self._pause_requested = pause_requested