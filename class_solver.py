'''
Created on 31 Jul 2013

@author: Aleksandra
'''

from operator import itemgetter
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

    

def add_resource_usage(resource_usage, demand):
    """
    Resources demand are added to resource_usage. resource_usage will be updated
    
    :param resource_usage: dictionary containing usage of every resource will be updated with demand param
    :param demand: dictionary of resource demands to be added to resource_usage  
    """
    for resource, amount in demand.iteritems():
        if resource in resource_usage:
            resource_usage[resource] = resource_usage[resource] + amount
        else:
            resource_usage[resource] = amount
            


def is_resource_usage_greater_than_supply(resource_demand, resource_supply):
    """
    Checks if usage of resource (resource_demand) does not exceed overall supply (resource_supply)
    
    :param resource_demand: state of usage which is to be checked
    :param resource_supply: actual supply of resources
    """
    for resource in resource_supply:
        if resource not in resource_demand:
            continue    
        if resource_demand[resource] > resource_supply[resource]:
            return True
    else:
        return False
        
def update_resource_usages_in_time(resource_usages_in_time, activity, point_in_time):
    for point in range(point_in_time, point_in_time + activity.duration):
        actual_resource_usage = resource_usages_in_time[point]
        add_resource_usage(actual_resource_usage, activity.demand)
    
  
def activity_in_conflict_in_precedence(problem, solution, activity, proposed_start_time):
    for predecessor_activity in problem.predecessors(activity):
        if solution.get_start_time(predecessor_activity) + predecessor_activity.duration > proposed_start_time:   #samo zadanie nie wie o swoich poprzedniahc, ale wie o nich problem
            return True
    else:
        return False

def sgs_2_dict(sgs, problem):
    solution = Solution()
    resource_usages_in_time = defaultdict(dict)
    
    for activity in sgs:
        latest_start = problem.compute_latest_start(activity)
        start_time = 0  
        for time_unit in reversed(range(latest_start+1)):
             actual_resource_usage = copy(resource_usages_in_time[time_unit])
             add_resource_usage(actual_resource_usage, activity.demand)
             if (is_resource_usage_greater_than_supply(actual_resource_usage, problem.resources) or (activity_in_conflict_in_precedence(problem, solution, activity, time_unit))):
                
                 start_time = time_unit + 1
                 break
        solution.set_start_time_for_activity(activity, start_time)
        update_resource_usages_in_time(resource_usages_in_time, activity, start_time)
    return solution

            
class Solution:   # fenotyp rozwiazania
    def __init__(self):
        self.makespan = 0
        self.solution={}
        self.solution[Activity.DUMMY_START] = 0
        
    def set_start_time_for_activity(self, activity, start_time):
        self.solution[activity] = start_time
        
    def get_start_time(self, activity):
        return self.solution[activity]
        
    def __str__(self):
        return "Solution: " + str(self.solution)
    
    def __eq__(self, other):
        if len(self.solution) != len(other.solution):
            return False
        
        for i,j in self.solution.iteritems():
            if other.solution[i] != j:
                return False
        return True
        
    
        
class Solver(object):
    
    def solve(self, problem):
        return Solution() 

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
    
    def successors(self, activity):
        return self.activity_graph[activity]
    
    def predecessors(self, activity):
        return self.predecessors_dict[activity]
    
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
        for activity, start_time in activities_start_times.solution.iteritems():
            when_activity_ends = activity.duration + start_time
            if when_activity_ends >= makespan:
                makespan = when_activity_ends
        return makespan
    
    def check_if_solution_feasible(self, activities_start_times):
        makespan = self.compute_makespan(activities_start_times)
        for i in xrange(makespan):
            resource_usage = {}
            for activity, start_time in activities_start_times.solution.iteritems():
                if start_time <= i < start_time + activity.duration:
                    add_resource_usage(resource_usage, activity.demand)
            
            if is_resource_usage_greater_than_supply(resource_usage, 
                                                        self.resources):
                return False
        return True