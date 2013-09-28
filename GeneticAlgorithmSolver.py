'''
Created on 17 Aug 2013

@author: Aleksandra
'''
from GenericEvolutionaryRcpspAlgorithmSolver import GenericGeneticAlgorithmSolver
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

def mutate_sgs(problem, sgs, prob = 0.05):
    new_sgs = sgs
    for i in xrange(len(new_sgs) - 1):
        copy_of_sgs = copy(new_sgs)
        if random() < prob:
            copy_of_sgs[i] = new_sgs[i+1]
            copy_of_sgs[i+1] = new_sgs[i]
        if problem.is_valid_sgs(copy_of_sgs):
            new_sgs = copy_of_sgs
    return (new_sgs,)

class GeneticAlgorithmSolver(GenericGeneticAlgorithmSolver):
    def __init__(self, *args):
        self.crossover_sgs = crossover_sgs
        self.mutate_sgs = mutate_sgs
        self.SgsMaker = SerialScheduleGenerationSchemeGenerator
        self.Solution = Solution
        super(GeneticAlgorithmSolver, self).__init__(*args)

def find_lowest_index_non_existing_in(list1, list2):
    for index, element in enumerate(list1):
        if element not in list2:
            return index
    else:
        raise WrongContentOfSgsList           
        
class WrongContentOfSgsList(Exception):
    pass        