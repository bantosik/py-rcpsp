'''
Created on 31 Jul 2013

@author: Aleksandra
'''
from random import choice
from deap import algorithms, tools, base, creator
from copy import copy
from collections import defaultdict 

class Activity(object):
    def __init__(self, name, duration, demand):
        self.duration = duration
        self.demand = demand
        self.name = name
        
    def __repr__(self):
        return self.name
         
    #def active_tasks(proposed_solution, problem_definition): #sprawdz ktore zadania sa aktywne w czasie t

Activity.DUMMY_START = Activity("start",0, 0)
Activity.DUMMY_END = Activity("end",0, 0)
Activity.DUMMY_NODES = [Activity.DUMMY_START, Activity.DUMMY_END]

    
class ResourceUsage(dict):
    def add_resource_usage(self, demand):
        """
        Resources demand are added to self.
        
        :param demand: dictionary of resource demands to be added to self  
        """
        for resource, amount in demand.iteritems():
            if resource in self:
                self[resource] = self[resource] + amount
            else:
                self[resource] = amount
                
    def is_resource_usage_greater_than_supply(self, resource_supply):
        """
        Checks if usage of resource does not exceed overall supply (resource_supply)
        
        :param self: state of usage which is to be checked
        :param resource_supply: actual supply of resources
        """
        for resource in resource_supply:
            if resource not in self:
                continue    
            if self[resource] > resource_supply[resource]:
                return True
        else:
            return False
            
def update_resource_usages_in_time(resource_usages_in_time, activity, point_in_time):
    for point in range(point_in_time, point_in_time + activity.duration):
        actual_resource_usage = resource_usages_in_time[point]
        actual_resource_usage.add_resource_usage(activity.demand)
    
  
def activity_in_conflict_in_precedence(problem, solution, activity, proposed_start_time):
    for predecessor_activity in problem.predecessors(activity):
        if solution.get_start_time(predecessor_activity) + predecessor_activity.duration > proposed_start_time:   #samo zadanie nie wie o swoich poprzedniahc, ale wie o nich problem
            return True
    else:
        return False

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
                          
class Solution(dict):   # fenotyp rozwiazania
    def __init__(self):
        self.makespan = 0
        self[Activity.DUMMY_START] = 0
        
    def set_start_time_for_activity(self, activity, start_time):
        self[activity] = start_time
        
    def get_start_time(self, activity):
        return self[activity]
        
    def __str__(self):
        return "Solution: " + super.__str__(self)
    
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        
        for i,j in self.iteritems():
            if other[i] != j:
                return False
        return True
    @staticmethod
    def generate_solution_from_serial_schedule_generation_scheme(sgs, problem):
        solution = Solution()
        resource_usages_in_time = defaultdict(ResourceUsage)
        
        for activity in sgs:
            latest_start = problem.compute_latest_start(activity)
            start_time = 0  
            for time_unit in reversed(range(latest_start+1)):
                 actual_resource_usage = copy(resource_usages_in_time[time_unit])
                 actual_resource_usage.add_resource_usage(activity.demand)
                 if (actual_resource_usage.is_resource_usage_greater_than_supply(problem.resources) or (activity_in_conflict_in_precedence(problem, solution, activity, time_unit))):
                    
                     start_time = time_unit + 1
                     break
            solution.set_start_time_for_activity(activity, start_time)
            update_resource_usages_in_time(resource_usages_in_time, activity, start_time)
        return solution
            
    
        
class GeneticAlgorithmSolver(object):
    # n= 300 ; cxpb = 0.5 ; mutpb = 0.2 ; ngen = 40
    def __init__(self, size_of_population = 300, crossover_probability = 0.5, mutation_probability = 0.2, number_of_generations = 40):
        self.size_of_population = size_of_population
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.number_of_generations = number_of_generations

    
    def generate_toolbox_for_problem(self):
        toolbox = base.Toolbox()
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        toolbox.register("individual", self.generate_individual)
        
    def generate_individual(self):
        pass
        
     
    def solve(self, problem):
        self.initialize_problem(problem)
        
        toolbox = self.generate_toolbox_for_problem()
        population = toolbox.population(n = self.size_of_population)
        algorithms.eaSimple(population, toolbox, cxpb = self.crossover_probability , mutpb = self.mutation_probability, ngen = self.number_of_generations, verbose=False)
        return self.generate_solution_from_individual(tools.selBest(population, 1))
        

class Problem(object):
    
    def __init__(self, activity_graph, resources):
        self.activity_graph = activity_graph
        self.resources = resources
        self.activities_set = set() 
        for activity in activity_graph:
            self.activities_set.add(activity)
            for nested_act in activity_graph[activity]:
                self.activities_set.add(nested_act)
                
        self.predecessors_dict = defaultdict(list)
        for activity, activity_successors in self.activity_graph.iteritems():
            for successor in activity_successors:
                self.predecessors_dict[successor].append(activity)
                    
    def activities(self):
        return self.activities_set
    
    def non_dummy_activities(self):
        return self.activities_set - set([Activity.DUMMY_START, Activity.DUMMY_END])
    
    def successors(self, activity):
        return self.activity_graph[activity]
    
    def predecessors(self, activity):
        return self.predecessors_dict[activity]
    
    def non_dummy_predecessors(self,activity):
        return [x for x in self.predecessors(activity) if x not in Activity.DUMMY_NODES]
    
    def non_dummy_successors(self,activity):
        return [x for x in self.successors(activity) if x not in Activity.DUMMY_NODES]
    
    
    def compute_latest_start(self, activity):
        """Computes latest possible start for activity with dependencies with other 
        activities defined in problem
        
        :param activity: activity which latest start will be computed
        :type activity: class_solver.Activity
        :param problem: problem definition which contains activity
        :type problem: class_solver.Problem
        :returns: point in time of latest start of activity
        """
        latest_starts = {}
        latest_finishes = {}
        self._compute_latest_start_rec(activity, latest_starts, latest_finishes)
        return latest_starts[activity]
    
    def _compute_latest_start_rec(self, activity, latest_starts, latest_finishes):
        if activity is Activity.DUMMY_END:
            s = sum([x.duration for x in self.activities()])
            latest_starts[activity] = s
            latest_finishes[activity] = s
        else:
            current_min = sum([x.duration for x in self.activities()])
            for succ in self.successors(activity):
                self._compute_latest_start_rec(succ, latest_starts, latest_finishes)
                succ_latest_start = latest_starts[succ]
                if succ_latest_start < current_min:
                    current_min = succ_latest_start
            latest_finishes[activity] = current_min
            latest_starts[activity] = current_min - activity.duration
    
    def compute_makespan(self, activities_start_times):
        makespan = 0                                                                                                                                                                                                                                             
        for activity, start_time in activities_start_times.iteritems():
            when_activity_ends = activity.duration + start_time
            if when_activity_ends >= makespan:
                makespan = when_activity_ends
        return makespan
    
    def check_if_solution_feasible(self, activities_start_times):
        makespan = self.compute_makespan(activities_start_times)
        for i in xrange(makespan):
            resource_usage = ResourceUsage()
            for activity, start_time in activities_start_times.iteritems():
                if start_time <= i < start_time + activity.duration:
                    resource_usage.add_resource_usage(activity.demand)
            
            if resource_usage.is_resource_usage_greater_than_supply( self.resources):
                return False
        return True
    
    def find_all_elements_without_predecessors(self):
        return self.successors(Activity.DUMMY_START)