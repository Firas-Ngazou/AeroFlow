import numpy as np

class VectorObstacle:
    def __init__(self, initial_res=None):
        if initial_res is None:
            initial_res = [1920, 1080]
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

        eligible_factors = [1.0, 0.5, 0.25, 0.2, 0.125]
        new_factor = min(eligible_factors, key=lambda x: abs(x - self._reduction_factor))

        target_width = int(new_factor*self._initial_res[0])
        target_height = int(new_factor*self._initial_res[1])

        # Calculate the actual factor
        factor = int(1/new_factor)

        # Clean the grid to only keep the relevant part (removes the + 1 added under _update_default_grid)
        clean_height = target_height*factor
        clean_width = target_width*factor
        clean_grid = self._default_grid[:clean_width, :clean_height]

        # Downsampling
        self._binary_mask = clean_grid.reshape(target_width, factor, target_height, factor).any(axis=(1, 3))

    def _update_default_grid(self):
        width = self._initial_res[0]
        height = self._initial_res[1]

        self._default_grid = np.zeros((width, height), dtype=bool)
        if self._vertices.size > 0:
            x_coords = self._vertices[:, 0]
            y_coords = self._vertices[:, 1]

            valid = (x_coords >= 0) & (x_coords < width) & (y_coords >= 0) & (y_coords < height)
            self._default_grid[x_coords[valid], y_coords[valid]] = True

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
    def initial_res(self) -> list[int]:
        return self._initial_res

    @initial_res.setter
    def initial_res(self, new_res: list[int] | tuple[int, int]):
        self._initial_res = new_res
        self._update_default_grid()