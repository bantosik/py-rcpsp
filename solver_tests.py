'''
Created on 31 Jul 2013

@author: Aleksandra
'''
import unittest

from class_solver import *



class Test(unittest.TestCase):
    
    def setUp(self): #funkcja ktora framework testowy bedzie wykonywala przed kazda funkcja testowa
        self.activity1=Activity("a1",3,{1:2})
        self.activity2=Activity("a2",4,{1:3})
        self.activity3=Activity("a3",2,{1:4})
        self.activity4=Activity("a4",2,{1:4})
        self.activity5=Activity("a5",1,{1:3})
        self.activity6=Activity("a6",4,{1:2})
        
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
        self.start_times.set_start_time_for_activity(self.activity1, 6)
        self.start_times.set_start_time_for_activity(self.activity2, 0)
        self.start_times.set_start_time_for_activity(self.activity3, 10)
        self.start_times.set_start_time_for_activity(self.activity4, 4)
        self.start_times.set_start_time_for_activity(self.activity5, 12)
        self.start_times.set_start_time_for_activity(self.activity6, 6)
                       
        
        self.sgs = [self.activity2, self.activity4, self.activity1, self.activity6, self.activity3, self.activity5]

    def test_solve(self):
        solver = Solver()
        solution = solver.solve(self.problem)
        self.assertEqual(solution.makespan, 13, "Makespan is not equal to 13")
        
    def test_check_if_solution_is_feasible(self):
        is_feasible = self.problem.check_if_solution_feasible(self.start_times)  
        self.assertTrue(is_feasible, "solution is shown as unfeasible")

    def test_compute_makespan(self):
        makespan = self.problem.compute_makespan(self.start_times)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13")
    
    def test_sgs_2_dict(self):
        solution = sgs_2_dict(self.sgs, self.problem)
        self.assertEqual(solution, self.start_times, "Expected %s, got %s" % (self.start_times, solution) )  
        
    def test_sgs_2_dict_2(self):
        activity1=Activity("a1",3,{1:2})
        activity2=Activity("a2",4,{1:3})
        
        activity_graph = {Activity.DUMMY_START:[activity1],
                          activity1:[activity2], 
                          activity2:[Activity.DUMMY_END]}
        resources = {1:7}
        problem = Problem(activity_graph, resources)  
        solution_sgs = sgs_2_dict([activity1, activity2], problem)
        self.assertEqual(problem.compute_makespan(solution_sgs), 7, "Makespan is not egual 7")
                

    def test_compute_latest_start(self):
        latest_start = self.problem.compute_latest_start(self.activity1)
        self.assertEqual(latest_start, 10, "Latest start of the first activity should be 10")
    
    def test_successors(self):
        succ_list = self.problem.successors(self.activity3)
        self.assertEqual(len(succ_list), 1, "activity3 should have only one successor")
        self.assertIs(succ_list[0], self.activity5, "activity5 should be successor of the activity3")
        
    def test_update_resource_usages_in_time(self):
        resource_usages_in_time = {1: {1:2,2:3},2 : {}}
        activity1 = Activity("a1",2,{1:2})
        point_in_time_1 = 1
        update_resource_usages_in_time(resource_usages_in_time, activity1, point_in_time_1)
        
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
        
        
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_solve']
    unittest.main()