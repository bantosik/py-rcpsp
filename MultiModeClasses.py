import collections
import copy
import random
from random import choice
from BaseProblem import BaseProblem
from GeneticAlgorithmSolver import SerialScheduleGenerationSchemeGenerator

import ResourceUsage
import ListUtilities

def activity_in_conflict_in_precedence(problem, solution, activity, proposed_start_time):
    """
    function to test if given activity if scheduled at given time 'proposed_start_time'
    would be in conflict with any of the already scheduled activities from 'solution'
    with the precedence constraints as given in problem
    """
    for predecessor_activity in problem.predecessors(activity):
        start_time_of_predecessor = solution.get_start_time(predecessor_activity)
        predecessor_mode = solution.get_mode(predecessor_activity)
        if start_time_of_predecessor + predecessor_mode.duration > proposed_start_time:   #samo zadanie nie wie o swoich poprzedniahc, ale wie o nich problem
            return True
    else:
        return False

class Mode(object):
    """
    Class for keeping properties of mode of activity. Keeps its name, has specified
    duration which is positive integer value, and demand which is dictionary mapping
    from resource identifier to demand to this resource in given mode. Second
    dictionary non_renewable_demand keeps demand for nonrenewable resources in
    the same format as demand parameter.
    """
    def __init__(self, name, duration, demand, non_renewable_demand = {}):
        self.duration = duration
        self.demand = demand
        self.non_renewable_demand = non_renewable_demand
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

"""
dummy activities has its special null mode.
"""
Mode.nullMode = Mode("null", 0, {})

class Activity(object):
    def __init__(self, name, mode_list):
        self.mode_list = mode_list
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def maximal_duration(self):
        return max(x.duration for x in self.mode_list)
    
    def minimal_duration(self):
        return min(x.duration for x in self.mode_list)

    
class Solution(dict):   # fenotyp rozwiazania
    """
    class represents a solution in the form from which higher level components can
    retrieve basic feature of the solution such as starting times of every task
    and mode assignment

    Solution class is itself a dictionary which for every activity stores its starting time.
    >>> startTime = solution[activity]
    It stores also a public dictionary mode_assignment which stores assignment of modes to each task
    >>> mode = solution.mode_assignment[activity]
    """
    def __init__(self):
        self.makespan = 0
        self[Activity.DUMMY_START] = 0
        self.mode_assigment = {Activity.DUMMY_START: Mode.nullMode}
    
    @staticmethod
    def makeSolution(activities, modes):
        """
        make incomplete solution from the list of tasks will have start
        time set to zero.
        """
        solution = Solution()
        for a, mode in zip(activities, modes):
            solution[a] = 0
            solution.mode_assigment[a] = mode
        return solution
            
    def set_start_time_for_activity(self, activity, start_time, mode):
        """
        sets mode and start time for a given activity.
        """
        self[activity] = start_time
        self.mode_assigment[activity] = mode
        
        
    def get_start_time(self, activity):
        return self[activity]
    
    def get_mode(self, activity):
        return self.mode_assigment[activity]
        
    def __str__(self):
        return "Solution: " + super.__str__(self)
    
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        
        for i,j in self.iteritems():
            if other[i] != j:
                return False
            if other.get_mode(i) != self.get_mode(i):
                return False
            
        return True

    @staticmethod
    def generate_solution_from_serial_schedule_generation_scheme(sgs, problem):
        """
        creates new solution object from a valid serial schedule generation scheme, which is
        list of tuples containing activities and corresponding modes
        solution will be resource feasible for renewable resources
        """
        solution = Solution()
        resource_usages_in_time = collections.defaultdict(ResourceUsage.ResourceUsage)
        time_points = [0]
        
        for activity, mode in sgs:
            last_time = time_points[-1]
            start_time = 0
            for time_unit in reversed(time_points):
                actual_resource_usage = copy.copy(resource_usages_in_time[time_unit])
                actual_resource_usage.add_resource_usage(mode.demand)
                if (actual_resource_usage.is_resource_usage_greater_than_supply(problem.resources) or (activity_in_conflict_in_precedence(problem, solution, activity, time_unit))):
                    start_time = last_time
                    break
                else:
                    last_time = time_unit
            solution.set_start_time_for_activity(activity, start_time, mode)
            ListUtilities.insert_value_to_ordered_list(time_points, start_time)
            ListUtilities.insert_value_to_ordered_list(time_points, start_time + mode.duration)         
            ResourceUsage.update_resource_usages_in_time(resource_usages_in_time, mode, start_time)
        return solution         
    

Activity.DUMMY_START = Activity("start",[Mode.nullMode])
Activity.DUMMY_END = Activity("end",[Mode.nullMode])
Activity.DUMMY_NODES = [Activity.DUMMY_START, Activity.DUMMY_END]

class Problem(BaseProblem):
    def __init__(self, activity_graph, resources, nonrenewable_resources = {}):
        self.ActivityClass = Activity
        self.activity_graph = activity_graph
        self.resources = resources
        self.nonrenewable_resources = nonrenewable_resources
        self.activities_set = set() 
        for activity in activity_graph:
            self.activities_set.add(activity)
            for nested_act in activity_graph[activity]:
                self.activities_set.add(nested_act)
                
        self.predecessors_dict = collections.defaultdict(list)
        for activity, activity_successors in self.activity_graph.iteritems():
            for successor in activity_successors:
                self.predecessors_dict[successor].append(activity)
        
        self.latest_starts = {}
        self.latest_finishes = {}

    def compute_latest_start(self, activity):
        """Computes latest possible start for activity with dependencies with other 
        activities defined in problem
        
        :param activity: activity which latest start will be computed
        :type activity: class_solver.Activity
        :param problem: problem definition which contains activity
        :type problem: class_solver.Problem
        :returns: point in time of latest start of activity
        """
        if activity in self.latest_starts:
            return self.latest_starts[activity]
        
        if activity is Activity.DUMMY_END:
            s = sum([x.maximal_duration() for x in self.activities()])
            self.latest_starts[activity] = s
            self.latest_finishes[activity] = s
            return s
        else:
            current_min = sum([x.maximal_duration() for x in self.activities()])
            for succ in self.successors(activity):
                self.compute_latest_start(succ)
                succ_latest_start = self.latest_starts[succ]
                if succ_latest_start < current_min:
                    current_min = succ_latest_start
            self.latest_finishes[activity] = current_min
            self.latest_starts[activity] = current_min - activity.minimal_duration()
            return self.latest_starts[activity]
    
    def compute_makespan(self, solution):
        makespan = 0                                                                                                                                                                                                                                             
        for activity, start_time in solution.iteritems():
            when_activity_ends = solution.get_mode(activity).duration + start_time
            if when_activity_ends >= makespan:
                makespan = when_activity_ends
        return makespan
    
    def check_if_solution_feasible(self, solution):
        result = self.check_nonrenewable_resources(solution)
        result2 = self.check_renewable_resources(solution)
        return result and result2

    def check_renewable_resources(self, solution):
        result = True
        resource_usage = ResourceUsage.ResourceUsage()
        for a in solution:
            resource_usage.add_resource_usage(solution.get_mode(a).non_renewable_demand)
        if resource_usage.is_resource_usage_greater_than_supply( self.nonrenewable_resources):
            result = False
        
        return result 
    
    def check_nonrenewable_resources(self, solution):
        makespan = self.compute_makespan(solution)
        result = True
        for i in xrange(makespan):
            resource_usage = ResourceUsage.ResourceUsage()
            for activity, start_time in solution.iteritems():
                if start_time <= i < start_time + solution.get_mode(activity).duration:
                    resource_usage.add_resource_usage(solution.get_mode(activity).demand)
            
            if resource_usage.is_resource_usage_greater_than_supply( self.resources ):
                result = False
        return result
    
    def find_all_elements_without_predecessors(self):
        return self.successors(Activity.DUMMY_START)
    
    def is_valid_sgs(self, sgs):
        for i in range(len(sgs)):
           for j in range(i,len(sgs)):
               activity1 = sgs[i][0] 
               activity2 = sgs[j][0]
               if activity2 in self.predecessors(activity1):
                   return False
        return True
    
    
def choose_random_mode(activity):
    return random.choice(activity.mode_list)


class MultiModeSgsMaker(object):
    def __init__(self, problem, retries):
        self.problem = problem
        self.retries = retries
        self.generator = SerialScheduleGenerationSchemeGenerator(problem)

    def generate_random_sgs(self):
        sgs = self.generator.generate_random_sgs()
        modes = self.generate_modes(sgs)

        return zip(sgs, modes)

    def generate_modes(self, sgs):
        modes =[choice(activity.mode_list) for activity in sgs]
        for _i in xrange(self.retries):
            temp_solution = Solution.makeSolution(sgs, modes)
            if self.problem.check_nonrenewable_resources(temp_solution):
                return modes
            else:
                self.modify_mode(sgs, modes)
        return modes

    def modify_mode(self, activities, modes):
        multimode_activities = \
        [(i,a) for (i,a) in enumerate(activities) if len(a.mode_list) > 1]
        index_to_improve, activity = choice(multimode_activities)
        wrong_mode = modes[index_to_improve]
        new_mode = choice([mode for mode in activity.mode_list if mode is not wrong_mode])
        modes[index_to_improve] = new_mode