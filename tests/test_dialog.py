import pygame
import unittest
from singularity.code.graphics.dialog import fake_click, branch_coverage


def reset_branch_coverage():
    global branch_coverage
    branch_coverage.update({
        "branch_6": False,
        "branch_7": False,
    })

def print_branch_coverage():
    print("Branch Coverage Information:")
    for branch, hit in branch_coverage.items():
        print(f"{branch}: {'Hit' if hit else 'Missed'}")

class TestDialog(unittest.TestCase):

    def setUp(self):
        pygame.init()
        reset_branch_coverage()

    def tearDown(self):
        pygame.quit()

    def test_fake_click_down(self):
        fake_click(down = True)
        self.assertTrue(branch_coverage["branch_6"], "Branch 6 was not hit")
        

    def test_fake_click_up(self):
        fake_click(down = False)
        self.assertTrue(branch_coverage["branch_7"], "Branch 7 was not hit")


print_branch_coverage()
if __name__ == '__main__':
    unittest.main(exit=False)
    