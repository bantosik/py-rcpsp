'''
Created on 17 Aug 2013

@author: Aleksandra
'''
from SingleModeClasses import Solution
from deap import base, creator, tools, algorithms
from random import randint, random, choice
from copy import copy

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

class SerialScheduleGenerationSchemeGenerator:
    def __init__(self, problem):
        self.problem = problem
        
    def generate_random_sgs(self):
        ready_to_schedule = set(self.problem.find_all_elements_without_predecessors()) #set
        not_ready_to_schedule =  self.problem.non_dummy_activities() - set(ready_to_schedule)
        
        sgs_to_return = []
        
        for i in xrange(len(self.problem.non_dummy_activities())):
            current_activity = self._extract_random_activity_from_list(ready_to_schedule)
            sgs_to_return.append(current_activity)
            self._push_ready_activities_to_ready_to_schedule(current_activity, not_ready_to_schedule, ready_to_schedule)
        return sgs_to_return
        
        
    def _extract_random_activity_from_list(self, ready_to_schedule):
        r = choice(list(ready_to_schedule))
        ready_to_schedule.remove(r)
        return r
    
    def _push_ready_activities_to_ready_to_schedule(self, current_activity, not_ready_to_schedule, ready_to_schedule):
        for activity in self.problem.non_dummy_successors(current_activity):
            for predecessor in  self.problem.non_dummy_predecessors(activity):
                if predecessor in not_ready_to_schedule.union(ready_to_schedule):
                    break
            else:
                not_ready_to_schedule.remove(activity)
                ready_to_schedule.add(activity)
                
def crossover_sgs(sgs_mum, sgs_dad):
        q = randint(0,len(sgs_mum))
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
        toolbox.register("mate", crossover_sgs)
        toolbox.register("mutate", self.mutate_sgs, prob=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("clone", copy)
        
        return toolbox
     
    def solve(self):    
        toolbox = self.generate_toolbox_for_problem()
        population = toolbox.population(n = self.size_of_population)
        algorithms.eaSimple(population, toolbox, cxpb = self.crossover_probability , mutpb = self.mutation_probability, ngen = self.number_of_generations, verbose=False)
        return Solution.generate_solution_from_serial_schedule_generation_scheme(tools.selBest(population, 1)[0], self.problem)
    
    def evaluate_sgs(self, sgs):
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(sgs, self.problem)
        return (self.problem.compute_makespan(solution),)
        
    def mutate_sgs(self, sgs, prob = 0.05):
        new_sgs = sgs
        for i in xrange(len(new_sgs) - 1):
            copy_of_sgs = copy(new_sgs)
            if random() < prob:
                copy_of_sgs[i] = new_sgs[i+1]
                copy_of_sgs[i+1] = new_sgs[i]
            if self.problem.is_valid_sgs(copy_of_sgs):
                new_sgs = copy_of_sgs
        return (new_sgs,)
                
        
        
        
        
        
def find_lowest_index_non_existing_in(list1, list2):
    for index, element in enumerate(list1):
        if element not in list2:
            return index
    else:
        raise WrongContentOfSgsList           
        
class WrongContentOfSgsList(Exception):
    pass        