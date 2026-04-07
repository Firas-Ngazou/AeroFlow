import numpy as np

class D2Q9Constants:
    WEIGHTS = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36])
    E_X = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1])
    E_Y = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1])
    SPEED_OF_SOUND_SQUARED = 1/3
    OPPOSITES = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])

class LatticeGrid:
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._constants = D2Q9Constants()

        # distribution dans chacune des 9 directions dans chaque cellule (f_i)

        self._distributions = np.zeros((width, height, 9))
        for i in range(9):
            self._distributions[:, :, i] = self._constants.WEIGHTS[i]

        self._macro_density = np.zeros((width, height)) # Les densites dans chaque cellule (rho) (pas la mm chose que distributions)
        self._macro_velocity_x = np.zeros((width, height))
        self._macro_velocity_y = np.zeros((width, height))

        # print(self._distributions)

    def update_macroscopic(self):
        self._macro_density = np.sum(self._distributions, axis=2)
        self._macro_velocity_x = np.sum(self._distributions*self._constants.E_X, axis=2)/self.macro_density
        self._macro_velocity_y = np.sum(self._distributions*self._constants.E_Y, axis=2)/self.macro_density

    @property
    def distributions(self):
        return self._distributions
    @distributions.setter
    def distributions(self, new_distributions):
        self._distributions = new_distributions

    @property
    def macro_density(self):
        return self._macro_density
    @macro_density.setter
    def macro_density(self, new_macro_density):
        self._macro_density = new_macro_density

    @property
    def macro_velocity_x(self):
        return self._macro_velocity_x
    @macro_velocity_x.setter
    def macro_velocity_x(self, new_macro_velocity_x):
        self._macro_velocity_x = new_macro_velocity_x

    @property
    def macro_velocity_y(self):
        return self._macro_velocity_y