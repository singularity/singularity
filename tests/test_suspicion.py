import unittest
from singularity.code.g import suspicion_to_danger_level, branch_coverage


class Test_g(unittest.TestCase):
    
    
    def test_suspicion(self):
        
        result = suspicion_to_danger_level(1000)
        self.assertEqual(result, 0)
        self.assertTrue(branch_coverage["branch1"])

        result = suspicion_to_danger_level(3000)
        self.assertEqual(result, 1)
        self.assertTrue(branch_coverage["branch2"])
        
        result = suspicion_to_danger_level(6000)
        self.assertEqual(result, 2)
        self.assertTrue(branch_coverage["branch3"])

        result = suspicion_to_danger_level(8000)
        self.assertEqual(result, 3)
        self.assertTrue(branch_coverage["branch4"])

        


if __name__ == '__main__':
    unittest.main()
