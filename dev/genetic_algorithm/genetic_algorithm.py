import numpy as np
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


        self._current_vertices : np.ndarray
        self.__shape = asb.Airfoil("Shape", coordinates= self._current_vertices)

        self.__xf = asb.XFoil(airfoil = self.__shape)
        self.__result = self.__xf.alpha(0)
        
        self._estimated_drag = self.__result["CD"]
        self._estimated_lift = self.__result["CL"]


    def optimize(self, initial_shape: VectorObstacle, engine: SimulationEngine) -> dict:
        ...

    def __generate_mutation(self, parent: VectorObstacle) -> VectorObstacle:
        ...
    
    def __evaluate_fitness(self, condidate: VectorObstacle, engine: SimulationEngine) -> float:
        return 1/self._estimated_drag

    def __verify_distance(self, original: VectorObstacle, candidate: VectorObstacle) -> bool:
        ...

    def __verify_area(self, original: VectorObstacle, candidate: VectorObstacle) -> bool:
        ...
    
    def calculate_aerodynamic_gain(self, initial_cd: float, optimized_cd: float) -> float:
        ...

    @property
    def current_vertices(self):
        return self._current_vertices
    @current_vertices.setter
    def current_vertices(self, vertices):
        self._current_vertices = vertices


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