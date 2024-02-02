import unittest
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from long_filepath_filename_shortener import shorten_long_dir, shorten_long_filename

class TestShortenLongDir(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.getcwd(), 'test', 'test_dir')
        os.makedirs(self.test_dir, exist_ok=True)
        print(f"\nCreating test directory: {self.test_dir}")

        # Create a dictionary for testing
        self.dictionary_path = os.path.join(self.test_dir, "dictionary.csv")
        print(f"\nCreating file: {self.dictionary_path}")
        with open(self.dictionary_path, "w") as f:
            f.write("old,new\n")
            f.write("long_dir,ld\n")
            f.write("long_sub_dir,lsd\n")
            f.write("project,proj\n")
            f.write("production,prod\n")
            f.write("version,ver\n")
    
        
    def tearDown(self):
        # Remove the temporary directory after testing
        shutil.rmtree(self.test_dir)
        print("Tear down completed")

    def test_shorten_long_nested_dir(self):
        print("\nTest case: a directory with a long nested directory name is shortened")
        new_dir_path = os.path.join(self.test_dir, "ld", "lsd")
        print(f"Expected new directory path: {new_dir_path} | Length: {len(new_dir_path)}")
        
        # Test case: a directory with a long nested directory name is shortened
        long_dir_path = os.path.join(self.test_dir, "long_dir", "long_sub_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        shorten_long_dir(long_dir_path, self.dictionary_path, 58)
        self.assertTrue(os.path.exists(new_dir_path))
        print(f"Test status: {os.path.exists(new_dir_path)}")

    def test_dir_already_exists(self):
        print("\nTest case: a directory with the new name already exists")
        
        # Edge case: a directory with the new name already exists
        long_dir_path = os.path.join(self.test_dir, "long_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        new_dir_path = os.path.join(self.test_dir, "ld")
        os.makedirs(new_dir_path, exist_ok=True)
        print(f"Before renaming: {long_dir_path}")
        shorten_long_dir(long_dir_path, self.dictionary_path, 56)
        new_dir_path_conflict = os.path.join(self.test_dir, "ld_1")
        print(f"After renaming: {new_dir_path_conflict}")
        self.assertTrue(os.path.exists(new_dir_path_conflict))

    def test_dir_path_too_long(self):
        print("\nTest case: the new directory path is too long after conversion")
        
        # Edge case: the new directory path is still too long after conversion
        long_dir_path = os.path.join(self.test_dir, "long_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        print(f"Before renaming: {long_dir_path}")
        with self.assertLogs(level="ERROR") as cm:
            shorten_long_dir(long_dir_path, self.dictionary_path, 10)
        self.assertIn("Not possible to conver the folder path to the threshold!! Skipping the shorten process!", cm.output[0])

    
    def test_shorten_long_nested_dir_and_filename(self):
        print("\nTest case: a directory with a long nested directory name and a file with a long name are shortened")
        
        # Test case: a directory with a long nested directory name and a file with a long name are shortened
        long_dir_path = os.path.join(self.test_dir, "long_dir", "long_sub_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        long_file_path = os.path.join(long_dir_path, "project-A123_production-version-1.0.1.3.txt")
        with open(long_file_path, "w") as f:
            f.write("test content")
        
        new_dir_path = os.path.join(self.test_dir, "ld", "lsd")
        new_filename = os.path.join(new_dir_path, "proj-A123-prod-ver-1.0.1.3.txt")
        
        print(f"Expected new file name: {new_filename} | Length: {len(new_filename)}")
        print(f"Expected new directory path: {new_dir_path} | Length: {len(new_dir_path)}")
        
        shorten_long_filename(long_file_path, self.dictionary_path, 58)
        shorten_long_dir(long_dir_path, self.dictionary_path, 58)        
        
        self.assertTrue(os.path.exists(new_dir_path))
        self.assertTrue(os.path.exists(new_filename))
        print(f"Test status for directory: {os.path.exists(new_dir_path)}")
        print(f"Test status for file: {os.path.exists(new_filename)}")

if __name__ == "__main__":
    unittest.main()