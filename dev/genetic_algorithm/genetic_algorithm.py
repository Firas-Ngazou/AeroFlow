import numpy as np
import math
# from xfoil import XFoil
import aerosandbox as asb


from dev.physics_engine.vector_obstacle import VectorObstacle
from dev.physics_engine.simulation_engine import SimulationEngine
from dev.user_interface.canvas.q_editor import Shape

class GeneticAlgorithm():
    def __init__(self):
        self._max_iterations: int
        self._tolerance_margin: float
        self._constraint_method: str

        self._obstacle : VectorObstacle


    def optimize(self) -> dict:
        self.__shape = asb.Airfoil("Shape", coordinates= ...)

        self.__xf = asb.XFoil(airfoil = self.__shape)
        self.__result = self.__xf.alpha(0)
        
        self._estimated_drag = self.__result["CD"]
        self._estimated_lift = self.__result["CL"]


    def __generate_mutation(self, parent: VectorObstacle) -> VectorObstacle:
        ...
    
    def __evaluate_fitness(self) -> float:
        return 1/self._estimated_drag

    def __verify_distance(self, vertices: np.ndarray) -> bool:
        x = []
        y = []
        # mask_under = vertices < ...


        # Get coords
        for i in range(len(vertices)):
            for j in range(len(vertices[i])):
                if vertices[i][j] == 1:
                    x.append(i)
                    y.append(j)

        max_norm = math.sqrt(x^2 + y^2) #?


        
        


    def __verify_area(self, mask: np.ndarray) -> bool:
        if not self.constraint_method == "SURFACE":
            return True
        
        count_old = np.count_nonzero(self.obstacle.binary_mask.astype(np.int8))
        count = np.count_nonzero(mask.astype(np.int8))
        max_diff = self.tolerance_margin*count_old

        left = count_old - max_diff
        right = count_old + max_diff

        if left < count < right:
            return True
        
        return False
    
    def calculate_aerodynamic_gain(self) -> float:
        ...

    @property
    def obstacle(self):
        return self._obstacle
    @obstacle.setter
    def obstacle(self, obstacle: VectorObstacle):
        self._obstacle = obstacle


    @property
    def max_iterations(self):
        return self._max_iterations
    @max_iterations.setter
    def max_iteration(self, max_iteration):
        self._max_iterations = max_iteration


    @property
    def tolerance_margin(self):
        return self._tolerance_margin
    @tolerance_margin.setter
    def tolerance_margin(self, tolerance_margin):
        self.tolerance_margin = tolerance_margin


    @property
    def constraint_method(self):
        return self._constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint_method):
        self._constraint_method = constraint_method

    