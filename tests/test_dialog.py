import pygame
import unittest
from singularity.code.graphics.dialog import fake_click, branch_coverage, Dialog
from singularity.code import data
from singularity.code.dirs import create_directories

def reset_branch_coverage():
    global branch_coverage
    branch_coverage = {
        "branch_1": False,  
        "branch_2": False,  
       #"branch_3": False,
        "branch_4": False,
        "branch_5": False,  
    }

class TestDialog(unittest.TestCase):

    def setUp(self):
       # self.dialog_with_parent = Dialog()
        #self.dialog_with_parent.parent = "parent"
        
        #self.dialog_without_parent = Dialog()
        #self.dialog_without_parent.parent = None

        pygame.init()
        reset_branch_coverage()

    def tearDown(self):
        pygame.quit()

    def test_fake_click_down(self):
        #branch_coverage["branch_1"] = False
        #branch_coverage["branch_2"] = False
        fake_click(down = True)
        self.assertTrue(branch_coverage["branch_1"], "Branch 1 was not hit")
        #self.assertTrue(branch_coverage["branch_3"], "Branch 3 was not hit")

    def test_fake_click_up(self):
        fake_click(down = False)
        self.assertTrue(branch_coverage["branch_2"], "Branch 2 was not hit")
        #self.assertTrue(branch_coverage["branch_3"], "Branch 3 was not hit")

if __name__ == '__main__':
    unittest.main()