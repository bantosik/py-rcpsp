'''
Created on 31 Jul 2013

@author: Aleksandra
'''
import unittest

from MultiModeClasses import Mode, Activity, Solution, Problem
#from GeneticAlgorithmSolverMultiMode import GeneticAlgorithmSolver, crossover_sgs_nonrandom

class Test(unittest.TestCase):
    
    def setUp(self): #funkcja ktora framework testowy bedzie wykonywala przed kazda funkcja testowa
        self.mode1=Mode("m1",3,{1:2})
        self.mode1a=Mode("m1a",23,{1:2})
        self.activity1 = Activity("a1",[self.mode1, self.mode1a]) 
        
        self.mode2=Mode("m2",4,{1:3})
        self.activity2 = Activity("a2",[self.mode2])
        self.mode3=Mode("m3",2,{1:4})
        self.activity3 = Activity("a3",[self.mode3])
        self.mode4=Mode("m4",2,{1:4})
        self.activity4 = Activity("a4",[self.mode4])
        self.mode5=Mode("m5",1,{1:3})
        self.activity5 = Activity("a5",[self.mode5])
        self.mode6=Mode("m6",4,{1:2})
        self.activity6 = Activity("a6",[self.mode6])
    
        activity_graph = {Activity.DUMMY_START:[self.activity1,self.activity2],
                          self.activity1:[self.activity3], 
                          self.activity3:[self.activity5], 
                          self.activity2:[self.activity4],
                          self.activity4:[self.activity6],
                          self.activity5:[Activity.DUMMY_END],
                          self.activity6:[Activity.DUMMY_END]}
        
        resources = {1:4}
        
        self.problem = Problem(activity_graph, resources)
        
        self.start_times = Solution()
        self.start_times.set_start_time_for_activity(self.activity1, 6, self.mode1)
        self.start_times.set_start_time_for_activity(self.activity2, 0, self.mode2)
        self.start_times.set_start_time_for_activity(self.activity3, 10, self.mode3)
        self.start_times.set_start_time_for_activity(self.activity4, 4, self.mode4)
        self.start_times.set_start_time_for_activity(self.activity5, 12, self.mode5)
        self.start_times.set_start_time_for_activity(self.activity6, 6, self.mode6)
                       
        
        self.sgs = [(self.activity2, self.mode2), 
                    (self.activity4, self.mode4),
                    (self.activity1, self.mode1), 
                    (self.activity6, self.mode6), 
                    (self.activity3,self.mode3), 
                    (self.activity5, self.mode5)]
        
        self.sgs2 = [(self.activity2, self.mode2),
                     (self.activity1, self.mode1), 
                     (self.activity4, self.mode4), 
                     (self.activity3, self.mode3), 
                     (self.activity6, self.mode6),
                     (self.activity5, self.mode5)]
        
        
    def test_solve(self):
        solver = GeneticAlgorithmSolver(self.problem)
        solution = solver.solve()
        makespan = self.problem.compute_makespan(solution)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13, in fact it is %d, %s" % (makespan, str(solution)))
        
        
    def test_check_if_solution_is_feasible(self):
        is_feasible = self.problem.check_if_solution_feasible(self.start_times)  
        self.assertTrue(is_feasible, "solution is shown as unfeasible")

    def test_compute_makespan(self):
        makespan = self.problem.compute_makespan(self.start_times)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13")
    
    def test_sgs_2_dict(self):
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(self.sgs, self.problem)
        self.assertEqual(solution, self.start_times, "Expected %s, got %s" % (self.start_times, solution) )  

    def test_compute_latest_start(self):
        latest_start = self.problem.compute_latest_start(self.activity1)
        self.assertEqual(latest_start, 10, "Latest start of the first activity should be 10")
       
    def test_update_resource_usages_in_time(self):
        from collections import defaultdict
        resource_usages_in_time = defaultdict(dict)
        resource_usages_in_time[1] = ResourceUsage({1:2,2:3})
        resource_usages_in_time[2] = ResourceUsage()
        mode1 = Mode("a1",2,{1:2})
        point_in_time_1 = 1
        update_resource_usages_in_time(resource_usages_in_time, mode1, point_in_time_1)
        
        self.assertEqual(resource_usages_in_time[1][1], 4, "Resource usage in point 1 for resource 1 should be 4")
        self.assertEqual(resource_usages_in_time[1][2], 3, "Resource usage in point 1 for resource 2 should be 3")
        self.assertEqual(resource_usages_in_time[2][1], 2, "Resource usage in point 2 for resource 1 should be 2")
        
    def test_solution_equality(self):
        s = Solution()
        o = Solution()
        s.set_start_time_for_activity(self.activity1, 5)
        s.set_start_time_for_activity(self.activity2, 3)
        
        o.set_start_time_for_activity(self.activity2, 3)
        o.set_start_time_for_activity(self.activity1, 5)
        self.assertEqual(s, o, "These solutions should be equal %s, %s" % (str(s), str(o)))
    
    def test_push_ready_activities_to_ready_to_schedule(self):
        activity_graph = {Activity.DUMMY_START: [self.activity1],
                          self.activity1: [self.activity2, self.activity3],
                          self.activity2: [self.activity4],
                          self.activity3: [self.activity4],
                          self.activity4: [Activity.DUMMY_END]}
        problem = Problem(activity_graph, {})
        ready_to_schedule = set()
        not_ready_to_schedule = set([self.activity2, self.activity3, self.activity4])
        current_activity = self.activity1
        generator = SerialScheduleGenerationSchemeGenerator(problem)
        generator._push_ready_activities_to_ready_to_schedule(current_activity, not_ready_to_schedule, ready_to_schedule)
        self.assertEqual(ready_to_schedule, set([self.activity2, self.activity3]), "Ready to schedule should be update correctly")
        self.assertEqual(not_ready_to_schedule, set([self.activity4]), "Not ready to schedule should be update correctly")
        
    def test_generate_random_sgs_from_problem(self):
        generator = SerialScheduleGenerationSchemeGenerator(self.problem)
        sgs_to_return = generator.generate_random_sgs()
        self.assertEqual(set(sgs_to_return), self.problem.non_dummy_activities(), "Sgs should have all activities")
        n = len(sgs_to_return)     
        self.assertTrue(self.problem.is_valid_sgs(sgs_to_return), "Sgs should be valid")
                             
    def test_crossover_sgs_nonrandom(self):
        sgs_mum = [1,3,2,5,4,6]
        sgs_dad = [2,4,6,1,3,5]
        q = 3
        sgs_daughter, sgs_son = crossover_sgs_nonrandom(sgs_mum, sgs_dad, q)
        self.assertEqual(sgs_daughter, [1,3,2,4,6,5],"Daughter is not correctly generated %s" % str(sgs_daughter))
        self.assertEqual(sgs_son, [2,4,6,1,3,5],"Son is not correctly generated %s" % str(sgs_son))
    
    def test_insert_value_to_ordered_list(self):
        l = [1,3,4,5]
        insert_value_to_ordered_list(l, 2)
        self.assertEqual(l, [1,2,3,4,5], "2 should be inserted after 1")
        l = [1,4,5,6]
        insert_value_to_ordered_list(l, 4)
        self.assertEqual(l, [1,4,5,6], "list should remain unchanged")
        l = [0]
        insert_value_to_ordered_list(l, 4)
        self.assertEqual(l, [0,4], "list should be updated properly")
        
        
        
    

        
        
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_solve']
    unittest.main()