import math

import numpy as np
from lattice_grid import LatticeGrid, D2Q9Constants
from vector_obstacle import  VectorObstacle

class SimulationEngine:
    def __init__(self):
        self._grid: LatticeGrid | None = None
        self._obstacle: VectorObstacle | None = None
        self._tau = 0.6
        self._current_step: int = 0
        self._resolution_x: int = 10
        self._resolution_y: int = 10

        self._constants = D2Q9Constants()

    def initialize(self, initial_velocity: float):
        self._grid = LatticeGrid(self._resolution_x, self._resolution_y)
        self._grid.macro_velocity_x[:, :] = initial_velocity
        self._grid.macro_density[:, :] = 1.0

        f_eq = self._get_f_eq()

        self._grid.distributions = f_eq

    def execute_time_step(self):
        self.__apply_streaming()
        self.__apply_boundaries()
        self._grid.update_macroscopic()
        self.__apply_collision()
        if self._current_step >= 10: return
        self._current_step += 1
        self.execute_time_step()

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
        print(self._grid.distributions)

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
            self._grid.distributions[self.obstacle.binary_mask, i] = temp_distributions[self.obstacle.binary_mask,
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

    @property
    def obstacle(self):
        return self._obstacle
    @obstacle.setter
    def obstacle(self, obstacle: VectorObstacle):
        self._obstacle = obstacle