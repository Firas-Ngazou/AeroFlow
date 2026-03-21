import numpy as np

class LatticeGrid:
    def __init__(self, width: int, height: int, distributions: np.ndarray, distributions_temp: np.ndarray):
        self._width = width
        self._height = height
        self._distributions = distributions
        self._distributions_temp = distributions_temp

    def get_distribution(self, x: int, y: int) -> np.ndarray:
        ...

    def update_macroscopic(self) -> tuple[np.ndarray, np.ndarray]:
        ...

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height