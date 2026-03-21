import numpy as np

class VectorObstacle:
    def __init__(self, vertices: np.ndarray):
        self._vertices = vertices
        self._calculated_area: float = 0

    def calculate_area(self):
        ...

    def generate_binary_mask(self, grid_width: int, grid_height: int) -> np.ndarray:
        ...

    @property
    def vertices(self) -> np.ndarray:
        return self._vertices

    @property
    def calculated_area(self) -> float:
        return self._calculated_area