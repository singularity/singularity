import pygame
import unittest
from singularity.code.graphics.dialog import fake_click, branch_coverage

def reset_branch_coverage():
    global branch_coverage
    branch_coverage = {
        "branch_1": False,  
        "branch_2": False,  
        "branch_3": False,
        "branch_4": False,
        "branch_5": False,  
    }