from GenericEvolutionaryRcpspAlgorithmSolver import GenericGeneticAlgorithmSolver
from GeneticAlgorithmSolver import find_lowest_index_non_existing_in
from MultiModeClasses import MultiModeSgsMaker

__author__ = 'bartek'
'''
Created on 17 Aug 2013

@author: Aleksandra
'''

from MultiModeClasses import Solution
from deap import creator, base, tools, algorithms
from copy import copy
from random import random, randint

def negative_leftover(problem, mode_assignment):
    leftovers = [leftover_capacity(problem, resource, mode_assignment) for resource in problem.non_renewable_resources]
    return sum(-leftover for leftover in leftovers if leftover < 0 )

def leftover_capacity(problem, resource, mode_assignment):
    return problem.non_renewable_resources[resource] - sum(mode.demand[resource] for mode in mode_assignment)

def evaluate_sgs_function(SolutionClass, problem_instance, sgs):
    #TODO: make test of evaluation function
    solution = SolutionClass.generate_solution_from_serial_schedule_generation_scheme(sgs, problem_instance)
    #unpack activities and modes list to the separate lists
    activities, modes = zip(*sgs)
    total_negative_leftover = negative_leftover(problem_instance, modes)
    maximal_makespan = sum(act.maximal_duration() for act in activities)
    if total_negative_leftover > 0:
        return (maximal_makespan + total_negative_leftover,)
    else:
        return (problem_instance.compute_makespan(solution),)

class GeneticAlgorithmSolverMultimode(GenericGeneticAlgorithmSolver):
    def __init__(self, *args, **kwargs):
        #TODO: implement crossover and mutate functions
        self.crossover_sgs = crossover_sgs_multimode
        self.mutate_sgs = mutate_sgs_multimode
        if not 'number_of_retries' in kwargs:
            retries = 4
        else:
            retries = kwargs['number_of_retries']
        self.SgsMaker = lambda problem : MultiModeSgsMaker(problem, retries)
        self.Solution = Solution
        super(GeneticAlgorithmSolverMultimode, self).__init__(*args)

    def evaluate_sgs(self, sgs):
        """
        evaluation of an genotype of a solution to multimode rcpsp.
        sgs is defined as a list of tuples of (assignment, corresponding mode).
        evaluation takes into account nonrenewable resources infeasibility,
        see [Sonke Hartmann Project Scheduling under limited constraints chapter 7.1.1]
        """
        return evaluate_sgs_function(self.Solution, self.problem, sgs)




