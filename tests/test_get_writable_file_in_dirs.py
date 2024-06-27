import os
import unittest

# Branch coverage tracking dictionary
branch_coverage = {
    "get_writable_file_in_dirs_1": False,  # if write_dir is not None
    "get_writable_file_in_dirs_2": False,  # if outer_paths is not None
    "get_writable_file_in_dirs_3": False,  # else (return None)
}

# Simulated global variable for write directories
write_dirs = {
    "dir1": "/path/to/dir1",
    "dir2": "/path/to/dir2",
    "dir3": None,
}

def get_writable_file_in_dirs(filename, dir_name, outer_paths=None):
    global write_dirs
    write_dir = write_dirs.get(dir_name)
    
    if write_dir is not None:
        branch_coverage["get_writable_file_in_dirs_1"] = True
        real_path = os.path.join(write_dir, filename)
        
        if outer_paths is not None:
            branch_coverage["get_writable_file_in_dirs_2"] = True
            outer_paths.append(real_path)
        
        return real_path
    else:
        branch_coverage["get_writable_file_in_dirs_3"] = True
        return None

# Function to print coverage results
def print_coverage():
    for branch, hit in branch_coverage.items():
        print(f"{branch} was {'hit' if hit else 'not hit'}")

# Unit tests
class TestGetWritableFileInDirs(unittest.TestCase):

    def setUp(self):
        global branch_coverage
        branch_coverage = {
            "get_writable_file_in_dirs_1": False,
            "get_writable_file_in_dirs_2": False,
            "get_writable_file_in_dirs_3": False,
        }

    def test_get_writable_file_in_dirs(self):
        # Test case 1: write_dir is not None, outer_paths is None
        filename = "testfile.txt"
        dir_name = "dir1"
        result = get_writable_file_in_dirs(filename, dir_name)
        expected_path = os.path.join(write_dirs[dir_name], filename)
        self.assertEqual(result, expected_path)
        self.assertTrue(branch_coverage["get_writable_file_in_dirs_1"])
        self.assertFalse(branch_coverage["get_writable_file_in_dirs_2"])
        self.assertFalse(branch_coverage["get_writable_file_in_dirs_3"])

        # Reset coverage
        branch_coverage["get_writable_file_in_dirs_1"] = False

        # Test case 2: write_dir is not None, outer_paths is not None
        outer_paths = []
        result = get_writable_file_in_dirs(filename, dir_name, outer_paths)
        self.assertEqual(result, expected_path)
        self.assertTrue(branch_coverage["get_writable_file_in_dirs_1"])
        self.assertTrue(branch_coverage["get_writable_file_in_dirs_2"])
        self.assertFalse(branch_coverage["get_writable_file_in_dirs_3"])
        self.assertIn(expected_path, outer_paths)

        # Reset coverage
        branch_coverage["get_writable_file_in_dirs_1"] = False
        branch_coverage["get_writable_file_in_dirs_2"] = False

        # Test case 3: write_dir is None
        dir_name = "dir3"
        result = get_writable_file_in_dirs(filename, dir_name)
        self.assertIsNone(result)
        self.assertFalse(branch_coverage["get_writable_file_in_dirs_1"])
        self.assertFalse(branch_coverage["get_writable_file_in_dirs_2"])
        self.assertTrue(branch_coverage["get_writable_file_in_dirs_3"])

if __name__ == "__main__":
    unittest.main(exit=False)
    print_coverage()
