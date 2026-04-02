import math

import numpy as np
from lattice_grid import LatticeGrid
from vector_obstacle import  VectorObstacle

class SimulationEngine:
    def __init__(self):
        self._grid: LatticeGrid | None = None
        self._current_obstacle: VectorObstacle
        self._tau: float
        self._current_step: int = 0
        self._resolution_x: int = 10
        self._resolution_y: int = 10

    def initialize(self, initial_velocity_ms: float):
        self._grid = LatticeGrid(self._resolution_x, self._resolution_y)
        self._grid.update_macroscopic()
        self._grid.macro_velocity_x[:, 0] = initial_velocity_ms

    def execute_time_step(self):
        self.__apply_streaming()
        self.__apply_collision()
        self.__apply_boundaries()

    def calculate_drag_coef(self):
        ...

    def calculate_lift_coef(self):
        ...

    def __apply_collision(self):
        ...

    def __apply_streaming(self):
        ...

    def __apply_boundaries(self):
        ...

    def set_obstacle(self, obstacle: VectorObstacle):
        ...

if __name__ == "__main__":
    engine = SimulationEngine()
    engine.initialize(10)