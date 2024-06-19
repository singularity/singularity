import unittest
from singularity.code.g import suspicion_to_danger_level, branch_coverage

# def suspicion_to_danger_level(suspicion):
#     if suspicion < 2500:
#         branch_coverage["branch1"] = True
#         print("Positive")
#         return 0
#     elif suspicion < 5000:
#         branch_coverage["branch2"] = True
#         print("Positive2")
#         return 1
#     elif suspicion < 7500:
#         branch_coverage["branch3"] = True
#         print("Positive3")
#         return 2
#     else:
#         branch_coverage["branch4"] = True
#         print("Non-Positive")
#         return 3


# def reset_branch_coverage():
#     global branch_coverage
#     branch_coverage = {
#         "branch_1": False,  
#         "branch_2": False,  
#         "branch_3": False,
#         "branch_4": False,

#     }

class Test_g(unittest.TestCase):
    
    
    def test_suspicion(self):
        #global branch_coverage

        
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

        
        # self.assertFalse(branch_coverage["branch2"])
        # self.assertFalse(branch_coverage["branch3"])
        # self.assertFalse(branch_coverage["branch1"])




if __name__ == '__main__':
    unittest.main()

#     def test_strip_to_null(self):
#         # Test case 1: Empty string
#         result = strip_to_null("")
#         self.assertEqual(result, "")
#         self.assertTrue(branch_coverage["strip_to_null_1"])

#         # Reset coverage for next test
#         branch_coverage["strip_to_null_1"] = False
#         branch_coverage["strip_to_null_2"] = False
#         branch_coverage["strip_to_null_3"] = False

#         # Test case 2: Leading space
#         result = strip_to_null(" abc")
#         self.assertEqual(result, "\uFEFFabc")
#         self.assertTrue(branch_coverage["strip_to_null_2"])

#         # Reset coverage for next test
#         branch_coverage["strip_to_null_1"] = False
#         branch_coverage["strip_to_null_2"] = False
#         branch_coverage["strip_to_null_3"] = False

#         # Test case 3: Trailing space
#         result = strip_to_null("abc ")
#         self.assertEqual(result, "abc\uFEFF")
#         self.assertTrue(branch_coverage["strip_to_null_3"])

#         # Reset coverage for next test
#         branch_coverage["strip_to_null_1"] = False
#         branch_coverage["strip_to_null_2"] = False
#         branch_coverage["strip_to_null_3"] = False

#         # Test case 4: Both leading and trailing spaces
#         result = strip_to_null(" abc ")
#         self.assertEqual(result, "\uFEFFabc\uFEFF")
#         self.assertTrue(branch_coverage["strip_to_null_2"])
#         self.assertTrue(branch_coverage["strip_to_null_3"])

# if __name__ == "__main__":
#     unittest.main()

#    def test_strip_to_null(self):
#         # Test case 1: Empty string
#         a_string = ""
#         result = strip_to_null(a_string)
#         self.assertEqual(result, "")
#         self.assertTrue(branch_coverage["strip_to_null_1"])

#         # Test case 2: Leading space
#         a_string = " abc"
#         result = strip_to_null(a_string)
#         self.assertEqual(result, "\uFEFFabc")
#         self.assertTrue(branch_coverage["strip_to_null_2"])

#         # Test case 3: Trailing space
#         a_string = "abc "
#         result = strip_to_null(a_string)
#         self.assertEqual(result, "abc\uFEFF")
#         self.assertTrue(branch_coverage["strip_to_null_3"])

#         # Test case 4: Both leading and trailing spaces
#         a_string = " abc "
#         result = strip_to_null(a_string)
#         self.assertEqual(result, "\uFEFFabc\uFEFF")
#         self.assertTrue(branch_coverage["strip_to_null_2"])
#         self.assertTrue(branch_coverage["strip_to_null_3"])

# if __name__ == "__main__":
#     unittest.main(exit=False)
#     print_coverage()