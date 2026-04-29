import numpy as np

class VectorObstacle:
    def __init__(self, initial_res: int = 1080):
        self._vertices: np.ndarray = np.array([])

        self._default_grid: np.ndarray | None = None
        self._initial_res = initial_res
        self._reduction_factor = 1.0

        self._binary_mask: np.ndarray | None = None
        self._calculated_area: float = 0

    def calculate_area(self):
        ...

    def _update_binary_mask(self):
        if self._default_grid is None: return

        # Get the target size with respect to a 16:9 ratio
        target_width = int(self._reduction_factor*(16/9)*self._initial_res)
        target_height = int(self._reduction_factor*self._initial_res)

        # Calculate the actual factor
        factor = int(1/self._reduction_factor)

        # Clean the grid to only keep the relevant part (removes the + 1 added under _update_default_grid)
        clean_height = target_height*factor
        clean_width = target_width*factor
        clean_grid = self._default_grid[:clean_width, :clean_height]

        # Downsampling
        self._binary_mask = clean_grid.reshape(target_width, factor, target_height, factor).any(axis=(1, 3))

    def _update_default_grid(self):
        height = self._initial_res + 1
        width = int((16/9) * self._initial_res) + 1

        self._default_grid = np.zeros((width, height), dtype=bool)
        if self._vertices.size > 0:
            x_coords = self._vertices[:, 0]
            y_coords = self._vertices[:, 1]

            valids = (x_coords >= 0) & (x_coords < width) & (y_coords >= 0) & (y_coords < height)
            self._default_grid[x_coords[valids], y_coords[valids]] = True

        self._update_binary_mask()

    @property
    def vertices(self) -> np.ndarray:
        return self._vertices
    @vertices.setter
    def vertices(self, new_vertices: np.ndarray):
        self._vertices = new_vertices
        self._update_default_grid()

    @property
    def binary_mask(self) -> np.ndarray:
        return self._binary_mask

    @property
    def calculated_area(self) -> float:
        return self._calculated_area

    @property
    def reduction_factor(self) -> float:
        return self._reduction_factor
    @reduction_factor.setter
    def reduction_factor(self, new_factor: float):
        self._reduction_factor = new_factor
        self._update_binary_mask()

    @property
    def initial_res(self) -> int:
        return self._initial_res

    @initial_res.setter
    def initial_res(self, new_res: int):
        self._initial_res = new_res
        self._update_default_grid()