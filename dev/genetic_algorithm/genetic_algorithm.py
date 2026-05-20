import numpy as np
import math
# from xfoil import XFoil
import aerosandbox as asb
import copy
import random

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

        ...


    def __generate_mutation(self, parent: VectorObstacle, force_random: bool = False) -> VectorObstacle:
        child = copy.deepcopy(parent)
        mask = child.binary_mask.astype(bool)
        
        for _ in range(50): # max attempts to find a valid mutation
            mutated_mask = mask.copy()
            flip_matrix = np.random.rand(*mask.shape) < self.mutation_rate
            mutated_mask ^= flip_matrix
            
            if self.__verify_distance(mutated_mask) and self.__verify_area(mutated_mask):
                child.binary_mask = mutated_mask.astype(np.int8)
                return child
                
        return child # returns the parent if no mutation was valid

    def __crossover(self, parent_a: VectorObstacle, parent_b: VectorObstacle) -> VectorObstacle:
        child = copy.deepcopy(parent_a)

        mask_a = parent_a.binary_mask
        mask_b = parent_b.binary_mask

        split = mask_a.shape[0] // 2
        child.binary_mask = np.vstack((mask_a[:split, :], mask_b[split:, :])) # Top half of mask_a and bottom half of mask_b
        return child



    def __select_parents(self, population: list, fitness_scores: list) -> tuple:
        ...



    def __evaluate_fitness(self) -> float:
        return 1/self._estimated_drag

    def __verify_distance(self, mask: np.ndarray) -> bool:
        if self.constraint_method != "DISTANCE":
            return True
        
        original_mask = self.obstacle.binary_mask.astype(bool)
        new_mask = mask.astype(bool)
    
        hamming_distance = np.count_nonzero(original_mask != new_mask)

        original_area = np.count_nonzero(original_mask)
        max_allowed_distance = self.tolerance_margin / 10 * original_area 


        return hamming_distance <= max_allowed_distance



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

    