import unittest
from singularity.code.g import nearest_percent, branch_coverage


class Test_nearest_percent(unittest.TestCase):

    def test_nearest(self):
        
        result = nearest_percent(140, 100)
        self.assertEqual(result, 100)
        self.assertTrue(branch_coverage["branch5"])

        result = nearest_percent(180, 100)
        self.assertEqual(result, 200)
        self.assertTrue(branch_coverage["branch6"])


if __name__ == '__main__':
    unittest.main()