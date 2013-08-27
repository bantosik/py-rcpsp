import collections
import copy
import random

import ResourceUsage
import ListUtilities

def activity_in_conflict_in_precedence(problem, solution, activity, proposed_start_time):
    for predecessor_activity in problem.predecessors(activity):
        start_time_of_predecessor = solution.get_start_time(predecessor_activity)
        predecessor_mode = solution.get_mode(predecessor_activity)
        if start_time_of_predecessor + predecessor_mode.duration > proposed_start_time:   #samo zadanie nie wie o swoich poprzedniahc, ale wie o nich problem
            return True
    else:
        return False

class Mode(object):
    def __init__(self, name, duration, demand):
        self.duration = duration
        self.demand = demand
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
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
    def __init__(self):
        self.makespan = 0
        self[Activity.DUMMY_START] = 0
        self.mode_assigment = {Activity.DUMMY_START: Mode.nullMode}
        
    def set_start_time_for_activity(self, activity, start_time, mode):
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
        solution = Solution()
        resource_usages_in_time = collections.defaultdict(ResourceUsage.ResourceUsage)
        time_points = [0]
        
        for (activity, mode) in sgs:
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

class Problem(object):
    def __init__(self, activity_graph, resources):
        self.activity_graph = activity_graph
        self.resources = resources 
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
                    
    def activities(self):
        return self.activities_set
    
    def non_dummy_activities(self):
        return self.activities_set - set([Activity.DUMMY_START, Activity.DUMMY_END])
    
    def successors(self, activity):
        try:
            return self.activity_graph[activity]
        except KeyError:
            pass
    
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
        makespan = self.compute_makespan(solution)
        for i in xrange(makespan):
            resource_usage = ResourceUsage.ResourceUsage()
            for activity, start_time in solution.iteritems():
                if start_time <= i < start_time + solution.get_mode(activity).duration:
                    resource_usage.add_resource_usage(solution.get_mode(activity).demand)
            
            if resource_usage.is_resource_usage_greater_than_supply( self.resources):
                return False
        return True
    
    def find_all_elements_without_predecessors(self):
        return self.successors(Activity.DUMMY_START)
    
    def is_valid_sgs(self, sgs):
        for i in range(len(sgs)):
           for j in range(i,len(sgs)):
               activity1 = sgs[i] 
               activity2 = sgs[j]
               if activity2 in self.predecessors(activity1):
                   return False
        return True
    
    
def choose_random_mode(activity):
    return random.choice(activity.mode_list)
    


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
        
        result = [(activity, choose_random_mode(activity)) for activity in sgs_to_return]
        
        return result
        
        
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
           