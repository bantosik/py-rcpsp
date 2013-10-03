'''
Created on 31 Jul 2013

@author: Aleksandra
'''
import unittest

from MultiModeClasses import Mode, Activity, Solution, Problem, MultiModeSgsMaker
from NaiveGeneticAlgorithmSolverMultiMode import NaiveGeneticAlgorithmSolverMultiMode
                                             

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
        
        self.non_mode1=Mode("m1",3,{1:2},{1:1})
        self.non_mode1a=Mode("m1a",23,{1:2},{1:9})
        self.non_activity1 = Activity("a1",[self.non_mode1, self.non_mode1a]) 
        self.non_mode2=Mode("m2",4,{1:3},{1:1})
        self.non_activity2 = Activity("a2",[self.non_mode2])
        self.non_mode3=Mode("m3",2,{1:4})

        self.non_activity3 = Activity("a3",[self.non_mode3])
        self.non_mode4=Mode("m4",2,{1:4})
        self.non_activity4 = Activity("a4",[self.non_mode4])
        self.non_mode5=Mode("m5",1,{1:3})
        self.non_activity5 = Activity("a5",[self.non_mode5])
        self.non_mode6=Mode("m6",4,{1:2})
        self.non_activity6 = Activity("a6",[self.non_mode6])
    
        activity_graph = {Activity.DUMMY_START:[self.activity1,self.activity2],
                          self.activity1:[self.activity3], 
                          self.activity3:[self.activity5], 
                          self.activity2:[self.activity4],
                          self.activity4:[self.activity6],
                          self.activity5:[Activity.DUMMY_END],
                          self.activity6:[Activity.DUMMY_END]}
        
        resources = {1:4}
        nonrenewable = {1:3}
        
        self.problem = Problem(activity_graph, resources)
        self.non_problem = Problem(activity_graph, resources, nonrenewable)
        
        self.start_times = Solution()
        self.start_times.set_start_time_for_activity(self.activity1, 6, self.mode1)
        self.start_times.set_start_time_for_activity(self.activity2, 0, self.mode2)
        self.start_times.set_start_time_for_activity(self.activity3, 10, self.mode3)
        self.start_times.set_start_time_for_activity(self.activity4, 4, self.mode4)
        self.start_times.set_start_time_for_activity(self.activity5, 12, self.mode5)
        self.start_times.set_start_time_for_activity(self.activity6, 6, self.mode6)
        
        self.non_renewable_feasible_solution = Solution()
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity1, 6, self.non_mode1)
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity2, 0, self.non_mode2)
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity3, 10, self.non_mode3)
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity4, 4, self.non_mode4)
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity5, 12, self.non_mode5)
        self.non_renewable_feasible_solution.set_start_time_for_activity(self.non_activity6, 6, self.non_mode6)
                       
        
        self.non_renewable_unfeasible_solution = Solution()
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity1, 6, self.non_mode1a)
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity2, 0, self.non_mode2)
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity3, 10, self.non_mode3)
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity4, 4, self.non_mode4)
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity5, 12, self.non_mode5)
        self.non_renewable_unfeasible_solution.set_start_time_for_activity(self.non_activity6, 6, self.non_mode6)
     
        
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
        solver = NaiveGeneticAlgorithmSolverMultiMode(self.problem)
        solution = solver.solve()
        makespan = self.problem.compute_makespan(solution)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13, in fact it is %d, %s" % (makespan, str(solution)))
        
        
    def test_check_if_solution_is_feasible(self):
        is_feasible = self.problem.check_if_solution_feasible(self.start_times)  
        self.assertTrue(is_feasible, "solution is shown as unfeasible")
        
    def test_non_renewable_check_if_solution_is_feasible(self):
        is_feasible = self.non_problem.check_if_solution_feasible(self.non_renewable_feasible_solution)  
        self.assertTrue(is_feasible, "solution is shown as unfeasible")

    def test_non_renewable_unfeasible_check_if_solution_is_feasible(self):
        is_feasible = self.non_problem.check_if_solution_feasible(self.non_renewable_unfeasible_solution)  
        self.assertFalse(is_feasible, "solution is shown as feasible")

    def test_compute_makespan(self):
        makespan = self.problem.compute_makespan(self.start_times)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13")
    
    def test_sgs_2_dict(self):
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(self.sgs, self.problem)
        self.assertEqual(solution, self.start_times, "Expected %s, got %s" % (self.start_times, solution) )  

    def test_compute_latest_start(self):
        latest_start = self.problem.compute_latest_start(self.activity1)
        self.assertEqual(latest_start, 30, "Latest start of the first activity should be 10 and is %d" % (latest_start))
       
    def test_solution_equality(self):
        s = Solution()
        o = Solution()
        s.set_start_time_for_activity(self.activity1, 5, self.mode1a)
        s.set_start_time_for_activity(self.activity2, 3, self.mode2)
        
        o.set_start_time_for_activity(self.activity2, 3, self.mode2)
        o.set_start_time_for_activity(self.activity1, 5, self.mode1a)
        self.assertEqual(s, o, "These solutions should be equal %s, %s" % (str(s), str(o)))
    
    def test_solution_inequality(self):
        s = Solution()
        o = Solution()
        s.set_start_time_for_activity(self.activity1, 5, self.mode1)
        s.set_start_time_for_activity(self.activity2, 3, self.mode2)
        
        o.set_start_time_for_activity(self.activity2, 3, self.mode2)
        o.set_start_time_for_activity(self.activity1, 5, self.mode1a)
        self.assertFalse(s == o, "These solutions should be not equal %s, %s" % (str(s), str(o)))

    def test_generate_random_sgs_from_problem(self):
        generator = MultiModeSgsMaker(self.problem,4)
        sgs_to_return = generator.generate_random_sgs()
        self.assertEqual(set([x[0] for x in sgs_to_return]), self.problem.non_dummy_activities(), "Sgs should have all activities")
        n = len(sgs_to_return)     
        self.assertTrue(self.problem.is_valid_sgs(sgs_to_return), "Sgs should be valid")
                             
                             
#    def test_crossover_sgs_nonrandom(self):
#        sgs_mum = [(1, 1),(3, 2),(2, 3),(5, 4),(4, 5),(6, 6)]
#        sgs_dad = [(2, 7),(4, 8),(6, 9),(1, 10),(3, 11),(5, 12)]
#        q = 3
#        sgs_daughter, sgs_son = crossover_sgs_nonrandom(sgs_mum, sgs_dad, q)
#        self.assertEqual(sgs_daughter, [1,3,2,4,6,5],"Daughter is not correctly generated %s" % str(sgs_daughter))
#        self.assertEqual(sgs_son, [2,4,6,1,3,5],"Son is not correctly generated %s" % str(sgs_son))
    
        
        
        
    

        
        
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_solve']
    unittest.main()