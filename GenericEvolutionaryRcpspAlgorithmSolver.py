from copy import copy
from deap import base, creator, tools, algorithms

__author__ = 'bartek'

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

class GenericGeneticAlgorithmSolver(object):
    # n= 300 ; cxpb = 0.5 ; mutpb = 0.2 ; ngen = 40
    def __init__(self, problem, size_of_population = 300, crossover_probability = 0.5, mutation_probability = 0.2, number_of_generations = 40):
        self.size_of_population = size_of_population
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.number_of_generations = number_of_generations
        self.generator = self.SgsMaker(problem)
        self.problem = problem


    def generate_toolbox_for_problem(self):
        toolbox = base.Toolbox()
        toolbox.register("individual", lambda: creator.Individual(self.generator.generate_random_sgs()))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate_sgs)
        toolbox.register("mate", self.crossover_sgs)
        toolbox.register("mutate", lambda sgs: self.mutate_sgs(self.problem, sgs, prob = 0.05))
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("clone", copy)

        return toolbox

    def solve(self):
        toolbox = self.generate_toolbox_for_problem()
        population = toolbox.population(n = self.size_of_population)
        algorithms.eaSimple(population, toolbox, cxpb = self.crossover_probability , mutpb = self.mutation_probability, ngen = self.number_of_generations, verbose=False)
        return self.Solution.generate_solution_from_serial_schedule_generation_scheme(tools.selBest(population, 1)[0], self.problem)

    def evaluate_sgs(self, sgs):
        solution = self.Solution.generate_solution_from_serial_schedule_generation_scheme(sgs, self.problem)
        return (self.problem.compute_makespan(solution),)