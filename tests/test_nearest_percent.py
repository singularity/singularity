import unittest

# Branch coverage tracking dictionary
branch_coverage = {
    "nearest_percent_1": False,  # if 2 * sub_percent <= step
    "nearest_percent_2": False,  # else
}

def nearest_percent(value, step=100):
    sub_percent = value % step
    if 2 * sub_percent <= step:
        branch_coverage["nearest_percent_1"] = True
        return value - sub_percent
    else:
        branch_coverage["nearest_percent_2"] = True
        return value + (step - sub_percent)

# Function to print coverage results
def print_coverage():
    for branch, hit in branch_coverage.items():
        print(f"{branch} was {'hit' if hit else 'not hit'}")

# Unit tests
class TestNearestPercent(unittest.TestCase):

    def setUp(self):
        global branch_coverage
        branch_coverage = {
            "nearest_percent_1": False,
            "nearest_percent_2": False,
        }

    def test_nearest_percent(self):
        # Test case 1: sub_percent <= step/2
        value = 250
        step = 100
        result = nearest_percent(value, step)
        self.assertEqual(result, 200)
        self.assertTrue(branch_coverage["nearest_percent_1"])

        # Reset coverage
        branch_coverage["nearest_percent_1"] = False

        # Test case 2: sub_percent > step/2
        value = 260
        step = 100
        result = nearest_percent(value, step)
        self.assertEqual(result, 300)
        self.assertTrue(branch_coverage["nearest_percent_2"])

if __name__ == "__main__":
    unittest.main(exit=False)
    print_coverage()
