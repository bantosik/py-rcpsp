

__author__ = 'bartek'

class BaseProblem(object):
    def activities(self):
        return self.activities_set

    def non_dummy_activities(self):
        return self.activities_set - set([self.ActivityClass.DUMMY_START, self.ActivityClass.DUMMY_END])

    def successors(self, activity):
        try:
            return self.activity_graph[activity]
        except KeyError:
            pass

    def predecessors(self, activity):
        return self.predecessors_dict[activity]

    def non_dummy_predecessors(self,activity):
        return [x for x in self.predecessors(activity) if x not in self.ActivityClass.DUMMY_NODES]

    def non_dummy_successors(self,activity):
        return [x for x in self.successors(activity) if x not in self.ActivityClass.DUMMY_NODES]

    def compute_latest_start(self, activity):
        raise NotImplementedError()

    def compute_makespan(self, solution):
        raise NotImplementedError()

    def check_if_solution_feasible(self, solution):
        raise NotImplementedError()

    def check_renewable_resources(self, solution):
        raise NotImplementedError()

    def check_nonrenewable_resources(self, solution):
        raise NotImplementedError()

    def find_all_elements_without_predecessors(self):
        raise NotImplementedError()

    def is_valid_sgs(self, sgs):
        raise NotImplementedError()