import numpy as np
from lattice_grid import LatticeGrid
from vector_obstacle import  VectorObstacle

class SimulationEngine:
    def __init__(self, lattice_grid: LatticeGrid):
        self._grid = lattice_grid
        self._current_obstacle: VectorObstacle
        self._tau: float
        self._current_step: int = 0
        self._resolution_x: int = 200
        self._resolution_y: int = 200

        self._macro_velocity: np.ndarray = np.zeros((self._resolution_x, self._resolution_y, 2))
        self._macro_density: np.ndarray = np.zeros((self._resolution_x, self._resolution_y))

    def initialize(self, initial_velocity_ms: float, initial_density: float):
        ...

    def execute_time_step(self):
        ...

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

    @property
    def macro_velocity(self) -> np.ndarray:
        return self._macro_velocity

    @property
    def macro_density(self) -> np.ndarray:
        return self._macro_density