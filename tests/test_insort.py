import unittest

def insort_right_w_key(a, x, lo=0, hi=None, key=lambda v: v):
    
    if lo < 0:
        branch_coverage["branch_1"] = True
        print("branch_1: hit")
        raise ValueError("lo must be non-negative")
    if hi is None:
        branch_coverage["branch_2"] = True
        print("branch_2: hit")
        hi = len(a)
    x_key = key(x)
    while lo < hi:
        mid = (lo + hi) // 2
        mid_key = key(a[mid])
        if x_key < mid_key:
            branch_coverage["branch_3"] = True
            print("branch_3: hit")
            hi = mid
        else:
            branch_coverage["branch_4"] = True
            print("branch_4: hit")
            lo = mid + 1
    branch_coverage["branch_5"] = True
    print("branch_5: hit")
    a.insert(lo, x)

branch_coverage = {
    "branch_1": False,
    "branch_2": False,
    "branch_3": False,
    "branch_4": False,
    "branch_5": False
}

class TestInsort(unittest.TestCase):

    def setUp(self):
        global branch_coverage
        branch_coverage = {
            "branch_1": False,
            "branch_2": False,
            "branch_3": False,
            "branch_4": False,
            "branch_5": False
        }

    def test_negative_lo(self):
        with self.assertRaises(ValueError):
            insort_right_w_key([], 1, lo=-1)
        self.assertTrue(branch_coverage["branch_1"], "Branch 1 was not hit")
    
    def test_insert_into_empty_list(self):
        a = []
        insort_right_w_key(a, 3, key=lambda x: x)
        self.assertEqual(a, [3])
        self.assertTrue(branch_coverage["branch_2"], "Branch 2 was not hit")
        self.assertTrue(branch_coverage["branch_5"], "Branch 5 was not hit")

    def test_insert_with_none_hi(self):
        a = [1, 3, 5]
        insort_right_w_key(a, 4, hi=None)
        self.assertEqual(a, [1, 3, 4, 5])
        self.assertTrue(branch_coverage["branch_2"], "Branch 2 was not hit")

    def test_insert_in_sorted_list(self):
        a = [1, 3, 5]
        insort_right_w_key(a, 4, key=lambda x: x)
        self.assertEqual(a, [1, 3, 4, 5])
        self.assertTrue(branch_coverage["branch_4"], "Branch 4 was not hit")

    def test_insert_duplicate(self):
        a = [1, 2, 2, 3]
        insort_right_w_key(a, 2, key=lambda x: x)
        self.assertEqual(a, [1, 2, 2, 2, 3])
        self.assertTrue(branch_coverage["branch_4"], "Branch 4 was not hit")

if __name__ == "__main__":
    unittest.main(exit=False)
    