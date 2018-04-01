import pyade.commons
import numpy as np
import scipy.stats
import random
from typing import Callable, Union


def get_default_jade_params():
    """
        Returns the default parameters of the JADE Differential Evolution Algorithm
        :return: Dict with the default parameters of the JADE Differential
        Evolution Algorithm.
        :rtype dict
        """
    return {'cr': 0.5, 'f': 0.5, 'max_iters': 10000, 'seed': None}


def jade(population_size: int, individual_size: int, f: Union[float, int],
         cr: Union[float, int], bounds: np.ndarray,
         func: Callable[[np.ndarray], float], p: Union[int, float], c: Union[int, float],
         max_iters: int, seed: Union[int, None]) -> [np.ndarray, int]:
    """
    Applies the standard differential evolution algorithm.
    :param population_size: Size of the population.
    :type population_size: int
    :param individual_size: Number of gens/features of an individual.
    :type individual_size: int
    :param bounds: Numpy ndarray with individual_size rows and 2 columns.
    First column represents the minimum value for the row feature.
    Second column represent the maximum value for the row feature.
    :type bounds: np.ndarray
    :param func: Evaluation function. The function used must receive one
     parameter.This parameter will be a numpy array representing an individual.
    :type func: Callable[[np.ndarray], float]
    :param p: Parameter to choose the best vectors. Must be in (0, 1].
    :type p: Union[int, float]
    :param c: Variable to control parameter adoption. Must be in [0, 1].
    :type c: Union[int, float]
    :param max_iters: Number of generations after the algorithm is stopped.
    :type max_iters: int
    :param seed: Random number generation seed. Fix a number to reproduce the
    same results in later experiments.
    :type seed: Union[int, None]
    :return: A pair with the best solution found and its fitness.
    :rtype [np.ndarray, int]
    """
    # 0. Check parameters are valid
    if type(population_size) is not int or population_size <= 0:
        raise ValueError("population_size must be a positive integer.")

    if type(individual_size) is not int or individual_size <= 0:
        raise ValueError("individual_size must be a positive integer.")


    if type(max_iters) is not int or max_iters <= 0:
        raise ValueError("max_iter must be a positive integer.")

    if type(bounds) is not np.ndarray or bounds.shape != (individual_size, 2):
        raise ValueError("bounds must be a NumPy ndarray.\n"
                         "The array must be of individual_size length. "
                         "Each row must have 2 elements.")

    if type(seed) is not int and seed is not None:
        raise ValueError("seed must be an integer or None.")

    if type(p) not in [int, float] and 0 < p <= 1:
        raise ValueError("p must be a real number in (0, 1].")
    if type(p) not in [int, float] and 0 <= c <= 1:
        raise ValueError("c must be an rela number in [0, 1].")

    np.random.seed(seed)

    # 1. Init population
    population = pyade.commons.init_population(population_size, individual_size, bounds)
    u_cr = 0.5
    u_f = 0.6

    fitness = pyade.commons.apply_fitness(population, func)

    for iter in range(max_iters):
        # 2.1 Generate parameter values for current generation
        cr = np.random.normal(u_cr, 0.1, population_size)
        f = np.random.rand(population_size // 3) * 1.2
        f = np.concatenate((f, np.random.normal(u_f, 0.1, population_size - (population_size // 3))))

        # 2.2 Common steps
        mutated = pyade.commons.current_to_pbest_mutation(population, fitness, f.reshape(len(f), 1), p, bounds)
        crossed = pyade.commons.crossover(population, mutated, cr.reshape(len(f), 1))
        c_fitness = pyade.commons.apply_fitness(crossed, func)
        population = pyade.commons.selection(population, crossed,
                                             fitness, c_fitness)

        # 2.3 Adapt for next generation
        indexes = np.where(c_fitness < fitness)
        u_cr = (1 - c) * u_cr + c * np.mean(cr[indexes])
        u_f = (1 - c) * u_f + c * (np.sum(f[indexes]**2)/ np.sum(f[indexes]))

        fitness = pyade.commons.apply_fitness(population, func)

    best = np.argmin(fitness)
    return population[best], fitness[best]