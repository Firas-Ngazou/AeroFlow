import copy
import math
import threading
from datetime import datetime

import numpy as np
from PySide6.QtCore import QObject, Signal, Qt, QThread, Slot

from dev.physics_engine.lattice_grid import LatticeGrid, D2Q9Constants
from dev.physics_engine.vector_obstacle import  VectorObstacle

class SimulationEngine(QObject):
    """
    Manages the execution of a Lattice Boltzmann Method (LBM)-based simulation, including
    velocity and density initialization, obstacle handling, and iterative computations.

    This class establishes a simulation engine for fluid dynamics using the LBM. It
    handles grid setup, macroscopic variable updates, runtime settings like live editing,
    and signal-based communication of progress or results. - Generated using OpenAI's GPT-5.5

    :ivar progressUpdated: Signal emitted to notify progress updates, transmitting
        an integer indicating the progress percentage.
    :type progressUpdated: Signal[int]
    :ivar statusMessageUpdated: Signal emitted to notify status or error messages during
        execution, carrying a string message.
    :type statusMessageUpdated: Signal[str]
    :ivar iterationCompleted: Signal emitted after the completion of each iteration step,
        carrying a list of values for key metrics or data.
    :type iterationCompleted: Signal[list]
    :ivar maxStepUpdated: Signal emitted to communicate an updated maximum step count.
    :type maxStepUpdated: Signal[int]
    :ivar dragCoefUpdated: Signal emitted to notify an updated drag coefficient value.
    :type dragCoefUpdated: Signal[float]
    :ivar liftCoefUpdated: Signal emitted to notify an updated lift coefficient value.
    :type liftCoefUpdated: Signal[float]
    :ivar finished: Signal emitted when the simulation execution completes.
    :type finished: Signal
    """
    progressUpdated = Signal(int)
    statusMessageUpdated = Signal(str)
    iterationCompleted = Signal(list)
    maxStepUpdated = Signal(int)
    dragCoefUpdated = Signal(float)
    liftCoefUpdated = Signal(float)
    reynoldsUpdated = Signal(float)
    machUpdated = Signal(float)
    kineticEnergyUpdated = Signal(float)
    pressureDropUpdated = Signal(float)
    massUpdated = Signal(float)
    enstrophyUpdated = Signal(float)
    maxVorticityUpdated = Signal(float)

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

        # Data
        self._current_drag_force: float = 0.0
        self._current_lift_force: float = 0.0
        self._u_ref: float = 0.0
        self._rho_ref: float = 1.0
        self._viscosity: float = 0.014

        # Live-edit settings
        self._live_edit = False
        self._pause_requested = False
        self._previous_obstacle_mask: np.ndarray | None = None
        self._pending_live_edit_vertices: np.ndarray | None = None
        self._live_edit_lock = threading.Lock()
        self._live_edit_interval = 1

    def run(self, data: list[float | int]):
        """
        Executes the main pipeline for initializing and processing data relevant to boltzmann
        velocity and obstacle configuration. - Generated using OpenAI's GPT-5.5

        :param data: A list containing numerical values:
                     - `data[0]` represents the initial velocity (float or int).
                     - `data[1]` represents the initial resolution (float or int).
        :return: None
        """
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
        """
        Calculates the Boltzmann velocity for a given initial velocity.

        This method computes the velocity using the Boltzmann factor, which is
        derived from the Boltzmann constant, the room temperature, and the
        mass of an air particle. It divides the input initial velocity by the
        calculated factor to determine the result. - Generated using OpenAI's GPT-5.5

        :param initial_velocity: The initial velocity value to be used in the
            calculation.
        :type initial_velocity: float
        :return: The calculated Boltzmann velocity based on the initial velocity.
        :rtype: float
        """
        factor = math.sqrt(2 * self._boltzmann_k * self._room_temperature / self._air_particle_mass)
        return initial_velocity / factor

    def _initialize(self, initial_velocity: float):
        """
        Initializes the lattice grid with the provided initial velocity.

        This method configures the lattice grid with default macro quantities, distribution
        functions, and applies the obstacle mask to the grid. The equilibrium distribution
        function is computed and assigned to initialize the grid distributions. - Generated using OpenAI's GPT-5.5

        :param initial_velocity: The initial velocity to be set for the macro velocity
                                 in the X direction across the lattice grid.
        :type initial_velocity: float
        """
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
        """
        Executes a time-stepping loop for a simulation process.

        This method iterates through a maximum number of time steps (`_max_step`) while
        performing various updates necessary for simulating the system. The method checks
        for external interruption requests and pauses and handles live editing scenarios
        as needed. During each time step, multiple updates, including streaming, boundary
        applications, collision handling, and frame-end operations, are applied. If the
        process is paused, the thread sleeps for a short duration before resuming. At the
        end of the time-stepping loop, an event (`finished`) is emitted. - Generated using OpenAI's GPT-5.5

        :raises RuntimeError: If certain low-level simulation preconditions are not met.
        """
        i = 0

        while i < self._max_step:
            if QThread.currentThread().isInterruptionRequested():
                self.reset()
                break

            if not self._pause_requested:
                if not self._live_edit: i += 1
                self._frame_start_time = datetime.now()

                self._apply_pending_live_edit_vertices()
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
        """
        Calculates the maximum number of steps that can be performed given the current
        resolution and memory allocation. This computation assesses the memory usage
        for density and velocity fields, as well as the memory required per step,
        to ensure that the allocation remains within safe limits. - Generated using OpenAI's GPT-5.5

        :return: The estimated maximum number of steps that can be executed without
            exceeding the safe memory allocation.
        :rtype: int
        """
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
        """
        Calculates the drag coefficient based on the current drag force, reference density,
        reference velocity, and the effective area derived from the obstacle mask. - Generated using OpenAI's GPT-5.5

        The drag coefficient is computed using the formula:
            C_D = F_D / ((1/2) * rho_ref * U^2 * D)

        :param obstacle_mask: An array representing the mask of the obstacle, used to calculate
                              the effective area.
        :type obstacle_mask: numpy.ndarray
        :return: The computed drag coefficient. If the effective area is zero, it returns 0.0.
        :rtype: float
        """
        # C_D = F_D / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks(obstacle_mask)
        if area == 0:
            return 0.0

        coef = self._current_drag_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _calculate_lift_coef(self, obstacle_mask: np.ndarray):
        """
        Calculates the lift coefficient for the given obstacle mask. The lift coefficient (C_L)
        is determined using the formula:

        C_L = F_L / ((1/2) * rho_ref * U^2 * D)

        where F_L is the current lift force, rho_ref is the reference density, U is the
        reference velocity, and D is the relevant area associated with the obstacle mask.
        If the calculated area is zero, a lift coefficient of 0.0 is returned. - Generated using OpenAI's GPT-5.5

        :param obstacle_mask: A 2D numpy array representing the obstacle mask
                              used in the calculation of the lift coefficient.
        :type obstacle_mask: numpy.ndarray
        :return: The calculated lift coefficient. Returns 0.0 if the area is zero.
        :rtype: float
        """
        # C_L = F_L / ((1/2) * rho_ref * U^2 * D)
        area = self._coef_initial_checks(obstacle_mask)
        if area == 0:
            return 0.0

        coef = self._current_lift_force/(0.5 * self._rho_ref * (self._u_ref ** 2) * area)
        return coef

    def _coef_initial_checks(self, obstacle_mask: np.ndarray):
        """
        Performs initial coefficient checks based on the given obstacle mask. This method
        determines the area of the obstacle mask along the y-axis and uses it to calculate
        a value, which is used in further processing. Returns 0.0 if no valid area can be
        computed or certain conditions are not met. - Generated using OpenAI's GPT-5.5

        :param obstacle_mask: A 2D array representing the obstacle mask, where nonzero values
            indicate the presence of obstacles.
        :type obstacle_mask: np.ndarray
        :return: The calculated area coefficient as a float, or 0.0 if computation is not
            possible.
        :rtype: float
        """
        mask_y = np.where(obstacle_mask)[1]
        if len(mask_y) > 0:
            area = int(np.max(mask_y)) - int(np.min(mask_y)) + 1
        else:
            return 0.0
        if self._u_ref == 0:
            return 0.0

        return area

    def _calculate_reynolds_number(self, obstacle_mask: np.ndarray) -> float:
        area = self._coef_initial_checks(obstacle_mask)

        if area == 0.0:
            return 0.0

        if self._viscosity <= 0:
            return float('inf')

        return (self._u_ref * area) / self._viscosity

    def _calculate_max_mach(self):
        c_s = 0.57735 # Speed of sound in LBM engine
        v_sq = self._grid.macro_velocity_x**2 + self._grid.macro_velocity_y**2
        max_velocity = math.sqrt(float(np.max(v_sq)))

        return max_velocity/c_s

    def _calculate_kinetic_energy(self):
        v_sq = self._grid.macro_velocity_x**2 + self._grid.macro_velocity_y**2
        return 0.5 * self._grid.macro_density * np.sum(v_sq)

    def _calculate_pressure_drop(self):
        mask_x = np.where(self._obstacle.binary_mask)[0]
        if len(mask_x) == 0:
            return 0.0

        front_x = int(np.min(mask_x))
        back_x = int(np.max(mask_x))

        upstream_x = max(0, front_x - 5)
        downstream_x = min(self._resolution_x - 1, back_x + 5)

        pressure_upstream = np.mean(self._grid.macro_density[upstream_x, :]) / 3.0
        pressure_downstream = np.mean(self._grid.macro_density[downstream_x, :]) / 3.0

        return pressure_upstream - pressure_downstream

    def _calculate_total_mass(self) -> float:
        return np.sum(self._grid.macro_density)

    def __apply_streaming(self):
        """
        Applies the streaming step in a lattice Boltzmann method simulation. This function updates
        the particle distribution functions, macrovelocity, and macrodensity at the boundaries
        of the simulation grid based on predefined constants and equilibrium distribution.
        - Generated using OpenAI's GPT-5.5

        :return: None
        """
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
        Applies collision dynamics to update the distributions of the grid based on
        the relaxation factor and equilibrium distribution function while excluding
        cells marked by the obstacle mask. - Generated using OpenAI's GPT-5.5

        :param obstacle_mask: A boolean array indicating cells to exclude during
            collision processing. True values represent cells that are obstacles.
        :return: This method does not return any value. Modifies the grid distributions
            in place.
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
        Applies boundary conditions for the given obstacle mask by updating particle
        distributions and calculating drag and lift forces.

        The method updates the distributions of particles in the grid based on the
        provided boundary conditions defined by the obstacle mask. Additionally, it
        computes the drag and lift forces acting on the system by summing the
        momentum contributions of particles interacting with the obstacles. - Generated using OpenAI's GPT-5.5

        :param obstacle_mask: A boolean mask defining the position of obstacles
            in the grid. True values indicate the presence of obstacles.
        :type obstacle_mask: np.ndarray
        :return: This method does not return any value.
        :rtype: None
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
        Computes the equilibrium distribution function for the current state of the grid.

        This method loops through all discrete velocity directions and computes the
        equilibrium distribution values based on the macroscopic velocity and density
        fields of the grid, using the appropriate weights and constants associated
        with the employed lattice Boltzmann model. - Generated using OpenAI's GPT-5.5

        :return: A numpy array representing the equilibrium distribution function
            computed for all grid points and velocity directions.
        :rtype: np.ndarray
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
        Ends the current simulation frame, updates the simulation progress, computes drag and lift
        coefficients, and emits the corresponding data and updates. - Generated using OpenAI's GPT-5.5

        :param obstacle_mask: A NumPy array representing the obstacle mask where obstacles
            are marked in the simulation grid.
        :return: This method does not return any value.
        """
        self._current_step += 1

        if self._live_edit and self._current_step % self._live_edit_interval != 0:
            return

        progress = int((self._current_step / self._max_step) * 100)
        self.progressUpdated.emit(progress)
        self.__update_status_message()

        macro_velocity_x = self._grid.macro_velocity_x
        macro_velocity_y = self._grid.macro_velocity_y
        macro_density = self._grid.macro_density

        stacked_data = np.stack((macro_velocity_x, macro_velocity_y, macro_density, obstacle_mask), axis=-1)

        drag_coef = self._calculate_drag_coef(obstacle_mask)
        lift_coef = self._calculate_lift_coef(obstacle_mask)
        data = [stacked_data, self._current_step]

        self.iterationCompleted.emit(data)
        self.dragCoefUpdated.emit(drag_coef)
        self.liftCoefUpdated.emit(lift_coef)

    def __update_status_message(self) -> None:
        """
        Updates the status message with the computed time remaining for the process to complete.
        The time remaining is calculated based on the average time per step and the number
        of remaining steps. - Generated using OpenAI's GPT-5.5

        :return: None
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
        Resets the state of the object to its initial configuration.

        Resets various internal attributes to their default initial values, including
        step count, timing-related variables, and internal state variables. Emits multiple
        signals to inform any observers about the reset activity, setting drag and lift
        coefficients, progress updates, and status message updates. - Generated using OpenAI's GPT-5.5

        :return: None
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
        Sets the reduction factor for an obstacle.

        The reduction factor is used to adjust the behavior of the obstacle
        by modifying certain properties based on the provided factor. - Generated using OpenAI's GPT-5.5

        :param factor: A floating-point value that defines the new reduction
            factor for the obstacle.
        :return: None
        """
        self._obstacle.reduction_factor = factor

    def _apply_live_obstacle_changes(self):
        """
        Updates the simulation grid to reflect dynamic changes in obstacles during the simulation.

        This method handles the adjustment of the simulation grid when obstacles in the domain switch between
        solid and air. It ensures proper redistribution of fluid properties, including density, velocity, and
        particle distributions, to account for these dynamic changes. Additionally, the method enforces
        boundary conditions, reinitializes properties for areas that transition, and maintains the overall
        stability of the simulation. - Generated using OpenAI's GPT-5.5

        :return: A binary mask representing the current state of obstacles in the domain.
        :rtype: numpy.ndarray
        """
        obstacle_mask = self._obstacle.binary_mask.copy()

        if self._previous_obstacle_mask is None:
            self._previous_obstacle_mask = obstacle_mask.copy()
            return obstacle_mask

        if obstacle_mask.shape != self._previous_obstacle_mask.shape:
            self._previous_obstacle_mask = obstacle_mask.copy()
            return obstacle_mask

        became_solid = obstacle_mask & ~self._previous_obstacle_mask
        became_air = self._previous_obstacle_mask & ~obstacle_mask

        if np.any(became_air):
            source_fluid = ~obstacle_mask & ~became_air

            density_sum = np.zeros_like(self._grid.macro_density)
            velocity_x_sum = np.zeros_like(self._grid.macro_velocity_x)
            velocity_y_sum = np.zeros_like(self._grid.macro_velocity_y)
            distributions_sum = np.zeros_like(self._grid.distributions)
            neighbor_count = np.zeros_like(self._grid.macro_density)

            for i in range(1, 9):
                shifted_source = np.roll(source_fluid,(self._constants.E_X[i], self._constants.E_Y[i]),
                                         axis=(0, 1))

                density_sum += np.where(
                    shifted_source,
                    np.roll(self._grid.macro_density,(self._constants.E_X[i], self._constants.E_Y[i]),
                            axis=(0, 1)),0.0)
                velocity_x_sum += np.where(shifted_source, np.roll(self._grid.macro_velocity_x,
                                                                   (self._constants.E_X[i],
                                                                    self._constants.E_Y[i]),
                                                                   axis=(0, 1)),0.0)
                velocity_y_sum += np.where(shifted_source, np.roll(self._grid.macro_velocity_y,
                                                                   (self._constants.E_X[i],
                                                                    self._constants.E_Y[i]), axis=(0, 1)),0.0)

                shifted_distributions = np.roll(self._grid.distributions,(self._constants.E_X[i],
                                                                          self._constants.E_Y[i]), axis=(0, 1))
                distributions_sum += np.where(shifted_source[:, :, np.newaxis], shifted_distributions,0.0)

                neighbor_count += shifted_source.astype(float)

            has_neighbors = became_air & (neighbor_count > 0)
            no_neighbors = became_air & (neighbor_count == 0)

            self._grid.macro_density[has_neighbors] = (density_sum[has_neighbors] / neighbor_count[has_neighbors])
            self._grid.macro_velocity_x[has_neighbors] = (velocity_x_sum[has_neighbors] / neighbor_count[has_neighbors])
            self._grid.macro_velocity_y[has_neighbors] = (velocity_y_sum[has_neighbors] / neighbor_count[has_neighbors])
            self._grid.distributions[has_neighbors, :] = (distributions_sum[has_neighbors, :] /
                                                          neighbor_count[has_neighbors, np.newaxis])

            if np.any(no_neighbors):
                self._grid.macro_velocity_x[no_neighbors] = self._u_ref
                self._grid.macro_velocity_y[no_neighbors] = 0.0
                self._grid.macro_density[no_neighbors] = self._rho_ref

                f_eq = self._get_f_eq()
                for i in range(9):
                    self._grid.distributions[no_neighbors, i] = f_eq[no_neighbors, i]

        if np.any(became_solid):
            self._grid.macro_velocity_x[became_solid] = 0.0
            self._grid.macro_velocity_y[became_solid] = 0.0
            self._grid.macro_density[became_solid] = 0.0

            for i in range(9):
                self._grid.distributions[became_solid, i] = 0.0

        self._previous_obstacle_mask = obstacle_mask.copy()
        return obstacle_mask

    @Slot(np.ndarray)
    def queue_live_edit_vertices(self, to_queue: np.ndarray) -> None:
        """
        Adds the provided vertices to the queue for live editing. This operation is
        thread-safe and ensures that the queued vertices are independent of the
        original data by creating a copy. - Generated using OpenAI's GPT-5.5

        :param to_queue: The array of vertex data to be queued for live editing.
        :type to_queue: numpy.ndarray
        """
        with self._live_edit_lock:
            self._pending_live_edit_vertices = to_queue.copy()

    def _apply_pending_live_edit_vertices(self):
        """
        Applies any pending live edit vertices to the associated obstacle.

        This method ensures thread-safe application of changes to the obstacle's
        vertices by utilizing a thread lock. If there are no pending vertices, the
        method exits without performing any action. - Generated using OpenAI's GPT-5.5

        :raises RuntimeError: If an unexpected threading issue occurs
        """
        with self._live_edit_lock:
            if self._pending_live_edit_vertices is None:
                return

            pending = self._pending_live_edit_vertices
            self._pending_live_edit_vertices = None

        self._obstacle.vertices = pending

    @property
    def vertices(self) -> np.ndarray:
        """
        Provides access to the vertices of the obstacle.

        The `vertices` property returns a numpy array representing the vertices
        of the associated obstacle. This property is read-only and allows external
        access to the geometry of the obstacle. - Generated using OpenAI's GPT-5.5

        :return: A numpy array representing the vertices of the obstacle.
        :rtype: np.ndarray
        """
        return self._obstacle.vertices

    @vertices.setter
    def vertices(self, vertices: np.ndarray) -> None:
        """
        Sets the vertices of the obstacle.

        This property setter is used to update the vertices attribute of the obstacle.
        The input must be a numpy ndarray representing the vertices of the obstacle. - Generated using OpenAI's GPT-5.5

        :param vertices: An ndarray containing the vertices of the obstacle. The
            structure and dimensions of the array depend on the specific use case.

        :return: None
        """
        self._obstacle.vertices = vertices

    @property
    def allocation(self) -> int:
        """
        Provides a property to access the allocation value.

        This property allows for retrieving the current allocation value
        which is an internally managed attribute. - Generated using OpenAI's GPT-5.5

        :return: The currently assigned allocation value.
        :rtype: int
        """
        return self._allocation

    @allocation.setter
    def allocation(self, allocation: int) -> None:
        """
        Sets the allocation value. - Generated using OpenAI's GPT-5.5

        :param allocation: An integer value to set as the allocation.
        :type allocation: int
        :return: None
        :rtype: None
        """
        self._allocation = allocation

    @property
    def resolution_x(self) -> int:
        """
        Retrieves the horizontal resolution. - Generated using OpenAI's GPT-5.5

        :return: The horizontal resolution as an integer.
        :rtype: int
        """
        return self._resolution_x
    @resolution_x.setter
    def resolution_x(self, resolution_x: int) -> None:
        """
        Sets the horizontal resolution for the object. - Generated using OpenAI's GPT-5.5

        :param resolution_x: The new horizontal resolution to set.
        :type resolution_x: int
        """
        self._resolution_x = resolution_x

    @property
    def resolution_y(self) -> int:
        """
        Retrieves the vertical resolution (resolution_y) value.

        This property provides access to the vertical resolution of an object and
        should be handled purely as a read-only property. - Generated using OpenAI's GPT-5.5

        :return: Returns the vertical resolution value as an integer.
        :rtype: int
        """
        return self._resolution_y
    @resolution_y.setter
    def resolution_y(self, resolution_y: int) -> None:
        """
        Sets the vertical resolution property of the object. - Generated using OpenAI's GPT-5.5

        :param resolution_y: The vertical resolution to set for the object.
                             Must be an integer specifying the number of
                             vertical pixels.
        :type resolution_y: int
        :return: None
        :rtype: None
        """
        self._resolution_y = resolution_y

    @property
    def viscosity(self) -> float | None:
        """
        Represents the viscosity property of a material or fluid. - Generated using OpenAI's GPT-5.5

        This property provides a mechanism to access and compute the viscosity
        value, which may be used in scientific or engineering calculations.

        :return: The viscosity value as a float if defined, otherwise None.
        :rtype: float | None
        """
        return self._viscosity
    @viscosity.setter
    def viscosity(self, viscosity: float) -> None:
        """
        Sets the viscosity value, which is used to calculate the relaxation time (tau).
        The relaxation time is updated internally based on the provided viscosity. - Generated using OpenAI's GPT-5.5

        :param viscosity: The kinematic viscosity of the fluid. It is a positive
           floating-point value.
        :type viscosity: float
        """
        # viscosity = (1/3) * (tau - 0.5)
        # tau = (viscosity * 3) + 0.5
        if viscosity <= 0.0035:
            raise ValueError("Viscosity must be greater than 0.0035 for numerical stability")
        self._viscosity = viscosity
        self._tau = (viscosity * 3) + 0.5

    @property
    def live_edit(self):
        """
        Indicates whether live editing is enabled or not.

        This property retrieves the internal configuration that determines
        if the live editing feature is currently enabled. - Generated using OpenAI's GPT-5.5

        :return: A boolean indicating the state of the live edit feature.
        :rtype: bool
        """
        return self._live_edit
    @live_edit.setter
    def live_edit(self, live_edit: bool) -> None:
        """
        Sets the value of the live_edit attribute.

        This method allows setting the value of the internal live_edit attribute to
        enable or disable live editing functionality. - Generated using OpenAI's GPT-5.5

        :param live_edit: The new value for the live_edit attribute.
        :type live_edit: bool
        """
        self._live_edit = live_edit

    @property
    def pause_requested(self):
        """
        Indicates whether a pause has been requested.

        This property provides a boolean value that reflects the current state
        of the pause request. - Generated using OpenAI's GPT-5.5

        :return: True if a pause has been requested, False otherwise
        :rtype: bool
        """
        return self._pause_requested

    @pause_requested.setter
    def pause_requested(self, pause_requested: bool) -> None:
        """
        Sets the pause request status.

        This setter method updates the internal state indicating whether a pause
        is requested. The value assigned is expected to be of type bool. - Generated using OpenAI's GPT-5.5

        :param pause_requested: Flag to indicate if a pause is requested.
        :type pause_requested: bool
        :return: None
        :rtype: None
        """
        self._pause_requested = pause_requested