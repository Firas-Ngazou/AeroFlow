import math

import numpy as np
from lattice_grid import LatticeGrid, D2Q9Constants
from vector_obstacle import  VectorObstacle

class SimulationEngine:
    def __init__(self):
        self._grid: LatticeGrid | None = None
        self._current_obstacle: VectorObstacle
        self._tau = 0.6
        self._current_step: int = 0
        self._resolution_x: int = 10
        self._resolution_y: int = 10

        self._constants = D2Q9Constants()

    def initialize(self, initial_velocity: float):
        self._grid = LatticeGrid(self._resolution_x, self._resolution_y)
        self._grid.macro_velocity_x[:, :] = initial_velocity
        self._grid.macro_density[:, :] = 1.0

        self.__apply_collision()

    def execute_time_step(self):
        self.__apply_streaming()
        self.__apply_boundaries()
        self._grid.update_macroscopic()
        self.__apply_collision()

    def calculate_drag_coef(self):
        ...

    def calculate_lift_coef(self):
        ...

    def __apply_streaming(self):
        print(self._grid.distributions)
        new_f = np.zeros_like(self._grid.distributions)
        for i in range(9):
            new_f[:, :, i] = np.roll(self._grid.distributions[:, :, i],
                                     (self._constants.E_X[i], self._constants.E_Y[i]), axis=(0, 1))

        self._grid.distributions = new_f
        print(self._grid.distributions)

    def __apply_collision(self):

        # on trouve les valeurs de f_eq pour chaque distribution
        f_eq = np.zeros_like(self._grid.distributions)
        last_term = (self._grid.macro_velocity_x**2 +
                     self._grid.macro_velocity_y**2)

        for i in range(9):
            term_2 = (self._constants.E_X[i]*self._grid.macro_velocity_x +
                      self._constants.E_Y[i]*self._grid.macro_velocity_y)

            f_eq[:, :, i] = (self._constants.WEIGHTS[i]*self._grid.macro_density*
                             (1 + (3*term_2) + (4.5*term_2**2) - (1.5*last_term)))

        # applivation du facteur de relaxation
        self._grid.distributions += (1/self._tau)*(f_eq - self._grid.distributions)


    def __apply_boundaries(self):
        ...

    def set_obstacle(self, obstacle: VectorObstacle):
        ...

if __name__ == "__main__":
    np.set_printoptions(precision=2, suppress=True)
    engine = SimulationEngine()
    engine.initialize(10)
    engine.execute_time_step()