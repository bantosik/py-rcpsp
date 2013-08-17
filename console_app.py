'''
Created on 17 Aug 2013

@author: Aleksandra
'''
from class_solver import *
from GeneticAlgorithmSolver import GeneticAlgorithmSolver

activity1=Activity("a1",3,{1:2})
activity2=Activity("a2",4,{1:3})
activity3=Activity("a3",2,{1:4})
activity4=Activity("a4",2,{1:4})
activity5=Activity("a5",1,{1:3})
activity6=Activity("a6",4,{1:2})
        
activity_graph = {Activity.DUMMY_START:[activity1,activity2],
                  activity1:[activity3], 
                  activity3:[activity5], 
                  activity2:[activity4],
                  activity4:[activity6],
                  activity5:[Activity.DUMMY_END],
                  activity6:[Activity.DUMMY_END]}

resources = {1:4}
problem = Problem(activity_graph, resources)

solver = GeneticAlgorithmSolver(problem)
toolbox = solver.generate_toolbox_for_problem()
solution = solver.solve()
print problem.compute_makespan(solution)
