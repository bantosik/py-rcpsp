'''
Created on 17 Aug 2013

@author: Aleksandra
'''

from GenericEvolutionaryRcpspAlgorithmSolver import GenericGeneticAlgorithmSolver
from GeneticAlgorithmSolver import crossover_sgs, mutate_sgs
from MultiModeClasses import MultiModeSgsMaker, Solution


class NaiveGeneticAlgorithmSolverMultiMode(GenericGeneticAlgorithmSolver):
    def __init__(self, *args, **kwargs):
        self.crossover_sgs = crossover_sgs
        self.mutate_sgs = mutate_sgs
        if not 'number_of_retries' in kwargs:
            retries = 4
        else:
            retries = kwargs['number_of_retries']
        self.SgsMaker = lambda problem : MultiModeSgsMaker(problem, retries)
        self.Solution = Solution
        super(NaiveGeneticAlgorithmSolverMultiMode, self).__init__(*args)



                
