'''
Created on 17 Aug 2013

@author: Aleksandra
'''
from class_solver import SerialScheduleGenerationSchemeGenerator
from deap import base, creator, tools
from random import randint 

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

def crossover_sgs(sgs_mum, sgs_dad):
        q = randint(len_of_sgs_mum)
        return crossover_sgs_nonrandom(sgs_mum, sgs_dad, q)     
    
def crossover_sgs_nonrandom(sgs_mum, sgs_dad, q):
    len_of_sgs_mum = len(sgs_mum)
    sgs_daughter = creator.Individual()
    sgs_son = creator.Individual()
    for i in xrange(q):
        sgs_daughter.append(sgs_mum[i])
        sgs_son.append(sgs_dad[i])
    for i in xrange(q,len_of_sgs_mum):
        j = find_lowest_index_non_existing_in(sgs_dad, sgs_daughter)
        sgs_daughter.append(sgs_dad[j])
        j = find_lowest_index_non_existing_in(sgs_mum, sgs_son)
        sgs_son.append(sgs_mum[j])
    return (sgs_daughter, sgs_son)

class GeneticAlgorithmSolver(object):
    # n= 300 ; cxpb = 0.5 ; mutpb = 0.2 ; ngen = 40
    def __init__(self, problem, size_of_population = 300, crossover_probability = 0.5, mutation_probability = 0.2, number_of_generations = 40):
        self.size_of_population = size_of_population
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.number_of_generations = number_of_generations
        self.generator = SerialScheduleGenerationSchemeGenerator(problem)
        self.problem = problem

    def generate_toolbox_for_problem(self):
        toolbox = base.Toolbox()
        toolbox.register("individual", lambda: creator.Individual(self.generator.generate_random_sgs()))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate_sgs)
        
        return toolbox
     
    def solve(self, problem):
        self.initialize_problem(problem)
        
        toolbox = self.generate_toolbox_for_problem()
        population = toolbox.population(n = self.size_of_population)
        algorithms.eaSimple(population, toolbox, cxpb = self.crossover_probability , mutpb = self.mutation_probability, ngen = self.number_of_generations, verbose=False)
        return self.generate_solution_from_individual(tools.selBest(population, 1))
    
    def evaluate_sgs(self, sgs):
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(sgs, self.problem)
        return self.problem.compute_makespan(solution)
        
def find_lowest_index_non_existing_in(list1, list2):
    for index, element in enumerate(list1):
        if element not in list2:
            return index
    else:
        raise WrongContentOfSgsList           
        
class WrongContentOfSgsList(Exception):
    pass        