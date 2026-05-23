import numpy as np
import math
# from xfoil import XFoil
import aerosandbox as asb
import copy
import random
import neuralfoil as nf
from scipy.ndimage import binary_dilation

from dev.physics_engine.vector_obstacle import VectorObstacle
from dev.physics_engine.simulation_engine import SimulationEngine
from dev.user_interface.canvas.q_editor import Shape

class GeneticAlgorithm():
    def __init__(self, population_size: int = 20, mutation_rate: float = 0.05):
        self._max_iterations: int = 100
        self._tolerance_margin: float = 0.1
        self._constraint_method: str = "SURFACE"
        self._obstacle : VectorObstacle = None

        self.population_size = population_size
        self.mutation_rate = mutation_rate

        self._estimated_drag = None
        self._estimated_lift = None

    def optimize(self) -> dict:
        best_obstacle = None
        best_fitness = -float('inf')

        base_fitness = self.__evaluate_fitness(self._obstacle)

        best_fitness = base_fitness
        best_obstacle = copy.deepcopy(self._obstacle)

        population = []
        population.append(copy.deepcopy(self._obstacle))

        
        while len(population)< self.population_size:
            child = self.__generate_mutation(self._obstacle, force_random=True)
            population.append(child)


        for gen in range(self.max_iterations):
            fitness_scores = [self.__evaluate_fitness(ind) for ind in population]

            max_idx = np.argmax(fitness_scores)
            if fitness_scores[max_idx] > best_fitness:
                best_fitness = fitness_scores[max_idx]
                best_obstacle = copy.deepcopy(population[max_idx])

            next_generation = []
            next_generation.append(copy.deepcopy(population[max_idx])) # You want the best one to reappear in the next generation(?)

            while len(next_generation) < self.population_size:
                p_a, p_b = self.__select_parents(population, fitness_scores)
                child = self.__crossover(p_a, p_b)
                child = self.__generate_mutation(child, force_random=False)
                next_generation.append(child)

            population = next_generation

        return best_obstacle, best_fitness


    def __generate_mutation(self, parent: VectorObstacle, force_random: bool = False) -> VectorObstacle:
        child = copy.deepcopy(parent)
        mask_shape = child.binary_mask.shape

        if force_random:
            # mutated_mask = (np.random.rand(*mask_shape) > 0.5).astype(bool) # Bool array if index is > or < than 0.5
            mutated_mask = np.zeros(mask_shape, dtype=bool)
            y_center = mask_shape[0] // 2
            for x in range(int(mask_shape[1] * 0.1), int(mask_shape[1]*0.9)):
                thickness = random.randint(4, max(5, mask_shape[0] // 3)) # Thickness of the airfoil
                mutated_mask[y_center - thickness: y_center + thickness, x] = True

            child.binary_mask = mutated_mask.astype(np.int8)
            return child
        
        for attempt in range(50):
            current_mask = child.binary_mask.astype(bool)
            dilated = binary_dilation(current_mask)
            boundary = dilated ^ current_mask
            y_indices, x_indices = np.where(boundary)
            if len(x_indices) == 0: # If boundary is empty
                continue

            mutated_mask = current_mask.copy()
            num_mutations = random.randint(3, 7) # number of mutated pixels
            chosen_indices = random.sample(range(len(x_indices)), min(num_mutations, len(x_indices)))

            for idx in chosen_indices:
                cx, cy = x_indices[idx], y_indices[idx] # Grid coords
        
                if random.random() > 0.5:
                    mutated_mask[cy, cx] = False # Removes a pixel

                else: # Expands the shape
                    if cy + 1 < mask_shape[0]: mutated_mask[cy + 1, cx] = True
                    if cy - 1 >= 0: mutated_mask[cy - 1, cx] = True

            if self.__verify_distance(mutated_mask) or self.__verify_area(mutated_mask): # Change so that the user can pick which one
                child.binary_mask = mutated_mask.astype(np.int8)
                return child
                
        return child


    def __crossover(self, parent_a: VectorObstacle, parent_b: VectorObstacle) -> VectorObstacle: # REWORK
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


    def __evaluate_fitness(self, individual: VectorObstacle) -> float: # REWORK
        mask = individual.binary_mask.astype(bool)
        expanded_mask = binary_dilation(mask)

        # Coords
        y_indices, x_indices = np.where(expanded_mask)
        x_max, y_max = mask.shape[1], mask.shape[0]
        raw_coords = np.column_stack((x_indices / x_max, y_indices / y_max)) # Matrix of normalized coords

        airfoil = asb.Airfoil(name="Shape", coordinates=raw_coords) # Check doc for coords(?)
        aero = nf.get_aero_from_airfoil(
            airfoil=airfoil,
            alpha=0.0,
            Re=5e5
        )
        cd  = aero["CD"]

        fitness_score = 1.0 / cd
        return float(fitness_score)


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


    