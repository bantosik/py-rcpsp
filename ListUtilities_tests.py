import unittest
import ListUtilities

class ListUtiltiesTest(unittest.TestCase):    
    def test_insert_value_to_ordered_list(self):
        l = [1,3,4,5]
        ListUtilities.insert_value_to_ordered_list(l, 2)
        self.assertEqual(l, [1,2,3,4,5], "2 should be inserted after 1")
        l = [1,4,5,6]
        ListUtilities.insert_value_to_ordered_list(l, 4)
        self.assertEqual(l, [1,4,5,6], "list should remain unchanged")
        l = [0]
        ListUtilities.insert_value_to_ordered_list(l, 4)
        self.assertEqual(l, [0,4], "list should be updated properly")
        
        
        
    

        