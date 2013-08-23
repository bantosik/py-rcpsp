import unittest
from ResourceUsage import ResourceUsage, update_resource_usages_in_time
from SingleModeClasses import Activity

class ResourceUsagesTest(unittest.TestCase):
    def test_update_resource_usages_in_time(self):
        from collections import defaultdict
        resource_usages_in_time = defaultdict(dict)
        resource_usages_in_time[1] = ResourceUsage({1:2,2:3})
        resource_usages_in_time[2] = ResourceUsage()
        activity1 = Activity("a1",2,{1:2})
        point_in_time_1 = 1
        update_resource_usages_in_time(resource_usages_in_time, activity1, point_in_time_1)
        
        self.assertEqual(resource_usages_in_time[1][1], 4, "Resource usage in point 1 for resource 1 should be 4")
        self.assertEqual(resource_usages_in_time[1][2], 3, "Resource usage in point 1 for resource 2 should be 3")
        self.assertEqual(resource_usages_in_time[2][1], 2, "Resource usage in point 2 for resource 1 should be 2")
        