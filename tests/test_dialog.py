import pygame
import unittest
from singularity.code.graphics.dialog import fake_click, branch_coverage, insort_right_w_key


def reset_branch_coverage():
    global branch_coverage
    branch_coverage = {
        "branch_1": False,  
        "branch_2": False,  
        "branch_3": False,
        "branch_4": False,
        "branch_5": False,
        "branch_6": False,
        "branch_7": False,  
    }

class TestDialog(unittest.TestCase):

    def setUp(self):
        pygame.init()
        reset_branch_coverage()

    def tearDown(self):
        pygame.quit()

    def test_fake_click_down(self):
        fake_click(down = True)
        self.assertTrue(branch_coverage["branch_1"], "Branch 1 was not hit")
        

    def test_fake_click_up(self):
        fake_click(down = False)
        self.assertTrue(branch_coverage["branch_2"], "Branch 2 was not hit")
        

    def test_insert_into_empty_list(self):
        a = []
        insort_right_w_key(a, 5)
        self.assertEqual(a, [5])
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")

    def test_insert_in_sorted_list(self):
        a = [1, 3, 5, 7]
        insort_right_w_key(a, 4)
        self.assertEqual(a, [1, 3, 4, 5, 7])
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")
        self.assertTrue(branch_coverage["branch_6"], "Branch 6 was not hit")
        self.assertTrue(branch_coverage["branch_7"], "Branch 7 was not hit")


    def test_insert_to_rightmost_existing_element(self):
        a = [1, 2, 2, 3]
        insort_right_w_key(a, 2)
        self.assertEqual(a, [1, 2, 2, 2, 3])
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")
        self.assertTrue(branch_coverage["branch_7"], "Branch 7 was not hit")

    def test_insert_with_negative_lo(self):
        a = [1, 3, 5]
        with self.assertRaises(ValueError):
            insort_right_w_key(a, 4, lo=-1)
        self.assertTrue(branch_coverage["branch_3"], "Branch 3 was not hit")

    def test_insert_with_none_hi(self):
        a = [1, 3, 5]
        insort_right_w_key(a, 4, hi=None)
        self.assertEqual(a, [1, 3, 4, 5])
        self.assertTrue(branch_coverage["branch_4"], "Branch 4 was not hit")
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")
        self.assertTrue(branch_coverage["branch_6"], "Branch 6 was not hit")
        self.assertTrue(branch_coverage["branch_7"], "Branch 7 was not hit")


    def test_insert_with_custom_key(self):
        a = [(1, 'one'), (3, 'three'), (5, 'five')]
        insort_right_w_key(a, (4, 'four'), key=lambda v: v[0])
        self.assertEqual(a, [(1, 'one'), (3, 'three'), (4, 'four'), (5, 'five')])
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")
        self.assertTrue(branch_coverage["branch_6"], "Branch 6 was not hit")
        self.assertTrue(branch_coverage["branch_7"], "Branch 7 was not hit")

        

if __name__ == '__main__':
    unittest.main()