import numpy as np
import aerosandbox as asb
import copy
import random
import neuralfoil as nf
from scipy.ndimage import binary_dilation

from PySide6.QtCore import QObject, Signal

from dev.physics_engine.simulation_engine import SimulationEngine
from dev.user_interface.canvas.q_editor import Shape

class GeneticAlgorithm(QObject):
    iterationCompleted = Signal(np.ndarray, int, float)
    optimizationCompleted = Signal()

    def __init__(self, population_size: int = 20, mutation_rate: float = 0.05):
        super().__init__()
        self._max_iterations: int = 100
        self._tolerance_margin: float = 0.1
        self._constraint_method: str = "SURFACE" # surface or distance
        self._constraint_target: str = "DRAG"    # drag or lift

        self.population_size = population_size
        self.mutation_rate = mutation_rate

        self._estimated_drag = None
        self._estimated_lift = None

        self._baseline_vertices = None

    def optimize(self, vertices: np.ndarray):
        self._baseline_vertices = vertices

        best_obstacle = None
        best_fitness = -float('inf')

        base_fitness = self.__evaluate_fitness(vertices)

        best_fitness = base_fitness
        best_obstacle = copy.deepcopy(vertices)

        population = []
        population.append(copy.deepcopy(vertices))

        
        while len(population)< self.population_size:
            child = self.__generate_mutation(vertices)
            population.append(child)


        for gen in range(self.max_iterations):
            fitness_scores = [self.__evaluate_fitness(ind) for ind in population]

            max_idx = np.argmax(fitness_scores)
            if fitness_scores[max_idx] > best_fitness:
                best_fitness = fitness_scores[max_idx]
                best_obstacle = copy.deepcopy(population[max_idx])

            self.iterationCompleted.emit(best_obstacle.copy(), gen, float(best_fitness))

            next_generation = []
            next_generation.append(copy.deepcopy(population[max_idx]))

            while len(next_generation) < self.population_size:
                p_a, p_b = self.__select_parents(population, fitness_scores)
                child = self.__crossover(p_a, p_b)
                child = self.__generate_mutation(child)
                next_generation.append(child)

            population = next_generation

        self.optimizationCompleted.emit()


    def __generate_mutation(self, parent: np.ndarray) -> np.ndarray:
        child = copy.deepcopy(parent)
        num_points = len(child)

        for attempt in range(50):
            mutated_vertices = copy.deepcopy(child)

            for i in range(1, num_points-1): # Anchors both ends
                if random.random() < self.mutation_rate:
                    y_nudge = np.random.normal(0, 0.015)
                    mutated_vertices[i, 1] += y_nudge

                    x_nudge = np.random.normal(0, 0.015)
                    mutated_vertices[i, 0] += x_nudge

            is_valid = False
            if self.constraint_method == "DISTANCE":
                is_valid = self.__verify_distance(mutated_vertices)
            elif self.constraint_method == "SURFACE":
                is_valid = self.__verify_area(mutated_vertices)
            else:
                is_valid = True

            if is_valid:
                return mutated_vertices            
                
        return child


    def __crossover(self, parent_a: np.ndarray, parent_b: np.ndarray) -> np.ndarray:
        child = copy.deepcopy(parent_a)

        mask_a = parent_a.binary_mask.astype(bool)
        mask_b = parent_b.binary_mask.astype(bool)

        crossover_mask = np.random.rand(*mask_a.shape) > 0.5 # Random mask
        child_mask = np.where(crossover_mask, mask_a, mask_b)

        child.binary_mask = child_mask.astype(np.int8)
        return child


    def __select_parents(self, population: list, fitness_scores: list) -> tuple:
        def tournement():
            contenders = random.sample(list(zip(population, fitness_scores)), 3)
            contenders.sort(key= lambda x: x[1], reverse=True)
            return contenders[0][0]
        return tournement(), tournement()


    def __evaluate_fitness(self, individual: np.ndarray) -> float: # REWORK
        mask = individual.binary_mask.astype(bool)
        expanded_mask = binary_dilation(mask)

        if np.count_nonzero(mask) < 4 : # empty mask
            return -9999.0

        # Coords
        y_indices, x_indices = np.where(expanded_mask)
        x_max, y_max = mask.shape[1], mask.shape[0]
        raw_coords = np.column_stack((x_indices / x_max, y_indices / y_max)) # Matrix of normalized coords
        raw_coords = np.unique(raw_coords, axis=0)

        y_mean = np.mean(raw_coords[:, 1]) # centerline of the shape
        upper_pts = raw_coords[raw_coords[:, 1] >= y_mean]
        lower_pts = raw_coords[raw_coords[:, 1] < y_mean]

        upper_pts = upper_pts[np.argsort(upper_pts[:, 0])[::-1]] # Right to left
        lower_pts = lower_pts[np.argsort(lower_pts[:, 0])] # Left to right => Aerospace eng standard data format for airfoils to be strictly CLOCKWISE
        # the simulator connects the dots in the exact order they appear in the array

        coords = np.vstack((upper_pts, lower_pts, upper_pts[0]))

        try:

            airfoil = asb.Airfoil(name="Shape", coordinates=coords)
            airfoil.repanel(n_points_per_side=60) # makes the shape smooth for the cd approx
            aero = nf.get_aero_from_airfoil(
                airfoil=airfoil,
                alpha=0.0,
                Re=5e5
            )
            self._estimated_drag  = aero["CD"]
            self._estimated_lift  = aero["CL"]

            if np.isnan(self._estimated_drag) or np.isnan(self._estimated_lift):
                return -9999.0
            
            
            if self._constraint_target == "DRAG":
                if self._estimated_drag <= 0 :
                    return -9999.0
                return float(1.0 / self._estimated_drag)
            
            if self._constraint_target == "LIFT":
                if self._estimated_lift <= 0:
                    return -9999.0
                return float(1.0 / self._estimated_lift)
        
        except Exception:
            return -9999.0


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
    def max_iterations(self):
        return self._max_iterations
    @max_iterations.setter
    def max_iterations(self, max_iteration):
        self._max_iterations = max_iteration

    @property
    def tolerance_margin(self):
        return self._tolerance_margin
    @tolerance_margin.setter
    def tolerance_margin(self, tolerance_margin):
        self._tolerance_margin = tolerance_margin

    @property
    def constraint_method(self):
        return self._constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint_method):
        self._constraint_method = constraint_method

    @property
    def constraint(self):
        return self._constraint_method
    @constraint.setter
    def constraint(self, constraint: str):
        self._constraint_method = constraint

    @property
    def target(self):
        return self._constraint_target
    @target.setter
    def target(self, target: str):
        self._constraint_target = target

    @property
    def iterations(self):
        return self._max_iterations
    @iterations.setter
    def iterations(self, max : int):
        self._max_iterations = max

    @property
    def threshold(self):
        return self._tolerance_margin
    @threshold.setter
    def threshold(self, value: float):
        self._tolerance_margin = value