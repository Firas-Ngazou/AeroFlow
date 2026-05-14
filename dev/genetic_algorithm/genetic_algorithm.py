import numpy as np
# from xfoil import XFoil
import aerosandbox as asb


from dev.physics_engine.vector_obstacle import VectorObstacle
from dev.physics_engine.simulation_engine import SimulationEngine

class GeneticAlgorithm():
    def __init__(self):
        self._max_iterations: int = ...
        self._tolerance_margin: float = ...
        self._constraint_method: str = ...
        

    def optimize(self, initial_shape: VectorObstacle, engine: SimulationEngine) -> dict:
        ...

    def __generate_mutation(self, parent: VectorObstacle) -> VectorObstacle:
        ...
    
    def __evaluate_fitness(self, condidate: VectorObstacle, engine: SimulationEngine) -> float:
        ...

    def __verify_distance(self, original: VectorObstacle, candidate: VectorObstacle) -> bool:
        ...

    def __verify_area(self, original: VectorObstacle, candidate: VectorObstacle) -> bool:
        ...
    
    def calculate_aerodynamic_gain(self, initial_cd: float, optimized_cd: float) -> float:
        ...

    