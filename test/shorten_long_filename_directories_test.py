import unittest
import os
import shutil
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from long_filepath_filename_shortener import read_config_values, shorten_long_dir, shorten_long_filename

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
        
        # Test case: a directory with a long nested directory name is shortened
        long_dir_path = os.path.join(self.test_dir, "long_dir", "long_sub_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        
        long_file_path = os.path.join(long_dir_path, "project-A123_production-version-camelTest-1.0.1.3.txt")
        with open(long_file_path, "w") as f:
            f.write("test content")
        
        new_dir_path = os.path.join(self.test_dir, "ld", "lsd")
        
        shorten_long_dir(long_file_path, self.dictionary_path, len(new_dir_path), dry_run=False)
        self.assertTrue(os.path.exists(new_dir_path))
        print(f"Test status: {os.path.exists(new_dir_path)}")

    def test_filename_already_exists(self):
        print("\nTest case: a filename with the new name already exists")
        
        # Edge case: a filename with the new name already exists
        long_dir_path = os.path.join(self.test_dir, "long_dir", "long_sub_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        duplicate_long_file_path = os.path.join(long_dir_path, "proj-A123-prod-ver-camel-Test-1.0.1.3.txt")
        with open(duplicate_long_file_path, "w") as f:
            f.write("test content")
        
        long_file_path = os.path.join(long_dir_path, "project-A123_production-version-camelTest-1.0.1.3.txt")
        with open(long_file_path, "w") as f:
            f.write("test content")
            
        new_dir_path = os.path.join(self.test_dir, "ld", "lsd")
        new_filename = os.path.join(new_dir_path, "proj-A123-prod-ver-camel-Test-1.0.1.3_1.txt")
        
        print(f"Expected filename change from: {os.path.basename(long_file_path)} | Length: {len(os.path.basename(long_file_path))} => {os.path.basename(new_filename)} | Length: {len(os.path.basename(new_filename))}")
        print(f"Expected directory change from: {os.path.dirname(long_file_path)} | Length: {len(os.path.dirname(long_file_path))} => {os.path.dirname(new_filename)} | Length: {len(os.path.dirname(new_filename))}")
        
        shorten_long_filename(long_file_path, self.dictionary_path, len(new_filename), False)
        shorten_long_dir(long_file_path, self.dictionary_path, len(new_dir_path), False)  

        self.assertTrue(os.path.exists(new_filename))
        print(f"Test status for test_filename_already_exists: {os.path.exists(new_filename)}")

    def test_dir_path_too_long(self):
        print("\nTest case: the new directory path is too long after conversion")
        
        # Edge case: the new directory path is still too long after conversion
        long_dir_path = os.path.join(self.test_dir, "long_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        print(f"Before renaming: {long_dir_path}")
        with self.assertLogs(level="ERROR") as cm:
            shorten_long_dir(long_dir_path, self.dictionary_path, 10, dry_run=False)
        self.assertIn("New directory path is still too long", cm.output[0])

    
    def test_shorten_long_nested_dir_and_filename(self):
        print("\nTest case: a directory with a long nested directory name and a file with a long name are shortened")
        
        # Test case: a directory with a long nested directory name and a file with a long name are shortened
        long_dir_path = os.path.join(self.test_dir, "long_dir", "long_sub_dir")
        os.makedirs(long_dir_path, exist_ok=True)
        long_file_path = os.path.join(long_dir_path, "project-A123_production-version-camelTest-1.0.1.3.txt")
        with open(long_file_path, "w") as f:
            f.write("test content")
        
        new_dir_path = os.path.join(self.test_dir, "ld", "lsd")
        new_filename = os.path.join(new_dir_path, "proj-A123-prod-ver-camel-Test-1.0.1.3.txt")
        
        print(f"Expected new file name: {new_filename} | Length: {len(new_filename)}")
        print(f"Expected new directory path: {new_dir_path} | Length: {len(new_dir_path)}")
        
        shorten_long_filename(long_file_path, self.dictionary_path, len(new_filename), False)
        shorten_long_dir(long_file_path, self.dictionary_path, len(new_dir_path), False)     
        
        self.assertTrue(os.path.exists(new_dir_path))
        self.assertTrue(os.path.exists(new_filename))
        print(f"Test status for directory: {os.path.exists(new_dir_path)}")
        print(f"Test status for file: {os.path.exists(new_filename)}")


    def test_shorten_long_nested_dir_and_filename_dry_run(self):
        print("\nTest case: a directory with a long nested directory name and a file with a long name are shortened (dry run)")

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

        shorten_long_filename(long_file_path, self.dictionary_path, len(new_filename), True)
        shorten_long_dir(long_file_path, self.dictionary_path, len(new_dir_path), True)     

        # Since it's a dry run, the directories and files should not actually be renamed
        self.assertFalse(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(new_dir_path))
        print(f"Test status for file: {os.path.exists(new_filename)}")
        print(f"Test status for directory: {os.path.exists(new_dir_path)}")

        # Check if the CSV file contains the expected changed paths
        config_values = read_config_values()     
        # print("Configuration values:", config_values)
        
        dry_run_dir = config_values['dry_run_dir']
        long_dir_path_modified_output = config_values['long_dir_path_modified_output']
        date_str = config_values['date_str']
        output_dir = config_values['output_dir']
        
        csv_file_path = f'{output_dir}/{dry_run_dir}/dry_run_{long_dir_path_modified_output}_{date_str}.csv'
        with open(csv_file_path, 'r') as f:
            reader = csv.reader(f)
            expected_rows = [
                [os.path.join(self.test_dir, "long_dir", "long_sub_dir"), os.path.join(self.test_dir, "long_dir", "lsd")],
                [os.path.join(self.test_dir, "long_dir"), os.path.join(self.test_dir, "ld")]
            ]
            for row, expected_row in zip(reader, expected_rows):
                self.assertEqual(row, expected_row)


if __name__ == "__main__":
    unittest.main()