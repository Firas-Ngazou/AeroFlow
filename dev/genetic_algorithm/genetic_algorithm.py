import numpy as np
import aerosandbox as asb
import copy
import random
import neuralfoil as nf
from scipy.ndimage import binary_dilation

from PySide6.QtCore import QObject, Signal, QThread

from dev.physics_engine.simulation_engine import SimulationEngine
from dev.user_interface.canvas.q_editor import Shape

class GeneticAlgorithm(QObject):
    iterationCompleted = Signal(np.ndarray, int, float)
    optimizationCompleted = Signal()

    def __init__(self):
        super().__init__()
        self._max_iterations: int = 100
        self._tolerance_margin: float = 0.1
        self._constraint_method: str = "SURFACE" # surface or distance
        self._constraint_target: str = "TRAÎNÉ"    # drag or lift

        self._population_size: int = 20
        self._mutation_rate: float = 0.05

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
            QThread.current_thread().msleep(50)

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
                # is_valid = self.__verify_distance(mutated_vertices) #TEST
                print("Distance verification")
                is_valid = True
            elif self.constraint_method == "SURFACE":
                # is_valid = self.__verify_area(mutated_vertices) #TEST
                print("Surface verification")
                is_valid = True
            else:
                is_valid = True

            if is_valid:
                return mutated_vertices            
                
        return child


    def __crossover(self, parent_a: np.ndarray, parent_b: np.ndarray) -> np.ndarray:
        num_points = len(parent_a)
        split_idx = random.randint(1, num_points - 2)

        child = np.vstack((parent_a[:split_idx], parent_b[split_idx:]))
        return child


    def __select_parents(self, population: list, fitness_scores: list) -> tuple:
        def tournement():
            contenders = random.sample(list(zip(population, fitness_scores)), 3)
            contenders.sort(key= lambda x: x[1], reverse=True)
            return contenders[0][0]
        return tournement(), tournement()


    def __evaluate_fitness(self, individual: np.ndarray) -> float:
        if individual is None or len(individual) < 4:
            return -9999.0
        
        coords = np.unique(individual, axis=0)

        if not np.array_equal(coords[0], coords[-1]):
            coords = np.vstack((coords, coords[0]))

        try:
            airfoil = asb.Airfoil(name="Shape", coordinates=coords)
            airfoil.repanel(n_points_per_side=60) # makes the shape smooth for the cd approx
            aero = nf.get_aero_from_airfoil(
                airfoil=airfoil,
                alpha=0.0,
                Re=5e5
            )
            self._estimated_drag = aero["CD"][0] if hasattr(aero["CD"], "__len__") else aero["CD"]
            self._estimated_lift = aero["CL"][0] if hasattr(aero["CL"], "__len__") else aero["CL"]

            if np.isnan(self._estimated_drag) or np.isnan(self._estimated_lift):
                return -9999.0
            
            
            if self._constraint_target == "TRAÎNÉ":
                if self._estimated_drag <= 0 :
                    return -9999.0
                return float(1.0 / self._estimated_drag)
            
            if self._constraint_target == "PORTANCE":
                if self._estimated_lift <= 0:
                    return -9999.0
                return float(1.0 / self._estimated_lift)
        
        except Exception:
            return -9999.0

    def __calculate_polygon_area(self, vertices: np.ndarray) -> float:
        x = vertices[:, 0]
        y = vertices[:, 1]
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def __verify_distance(self, mask: np.ndarray) -> bool:
        if self.constraint_method != "DISTANCE":
            return True
        
        original_mask = self.obstacle.binary_mask.astype(bool)
        new_mask = mask.astype(bool)
    
        hamming_distance = np.count_nonzero(original_mask != new_mask)

        original_area = np.count_nonzero(original_mask)
        max_allowed_distance = self.tolerance_margin / 10 * original_area


        return hamming_distance <= max_allowed_distance


    def __verify_area(self, vertices: np.ndarray) -> bool:
        if not self.constraint_method == "SURFACE":
            return True
        
        old_area = self.__calculate_polygon_area(self._baseline_vertices)
        new_area = self.__calculate_polygon_area(vertices)

        if old_area == 0:
            old_area = 1.0

        relative_difference = abs(old_area - new_area) / old_area
        return relative_difference <= self.tolerance_margin # Keeps a surface relative to the inital shape

    
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
    
    @property
    def population(self):
        return self._population_size
    @population.setter
    def threshold(self, value: int):
        self._population_size = value
    
    @property
    def rate(self):
        return self._mutation_rate
    @rate.setter
    def threshold(self, value: float):
        self._mutation_rate = value