import os
import sys
import unittest
from unittest.mock import call, patch
from os.path import normpath
from os.path import join

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from long_filepath_filename_shortener import process_dir_or_filename

class TestProcessDirOrFilename(unittest.TestCase):
    def setUp(self):
        self.config_values = {
            'config_dir': os.path.join('path', 'to', 'config'),
            'dictionary_path': 'dictionary.txt',
            'base_dir': os.path.join('path', 'to', 'base'),
            'output_dir': 'output_dir',
            'dir_scan_dir': 'dir_scan',
            'filename_scan_dir': 'filename_scan',
            'long_dir_path_scan_output': 'long_dir_path_scan',
            'long_filename_scan_output': 'long_filename_scan',
            'date_str': '20220101',
            'dir_length_threshold': 10,
            'filename_length_threshold': 15,
            'dry_run': True
        }
        
    def tearDown(self):
        pass  # Add any cleanup code here if necessary
    

    def test_process_dir(self):
        """Test case: a file with a list of directories is processed"""
        
        print("Running test_process_dir...")
        
        config_values = {
            'dictionary_path': 'dictionary.txt',
            'config_dir': 'path\\to\\config',
            'base_dir': os.path.join('path', 'to', 'base'),
            'output_dir': 'output_dir',
            'dir_scan_dir': 'dir_scan',
            'filename_scan_dir': 'filename_scan',
            'long_dir_path_scan_output': 'long_dir_path_scan',
            'long_filename_scan_output': 'long_filename_scan',
            'date_str': '20220101',
            'dir_length_threshold': 10,
            'filename_length_threshold': 15,
            'dry_run': True,
            'regular_expression': True
        }

        with patch('long_filepath_filename_shortener.CONFIG_VALUES', config_values):
            with patch('builtins.open', create=True) as mock_open:
                # Mocking the file content
                mock_open.return_value.__enter__.return_value = iter([
                    join('path', 'to', 'directory1'),
                    join('path', 'to', 'directory2'),
                    join('path', 'to', 'directory3')
                ])

                # Mocking the glob.glob function
                with patch('glob.glob') as mock_glob:
                    mock_glob.return_value = ['dummy_file_path']

                    # Mocking the shorten_long_dir function
                    with patch('long_filepath_filename_shortener.shorten_long_dir') as mock_shorten_dir:
                        print("Calling process_dir_or_filename('dir')...")
                        process_dir_or_filename('dir')

                        # Assert that the correct paths are processed
                        print("Checking if the correct paths were processed...")
                        self.assertEqual([
                            call(join('path', 'to', 'directory1'), config_values['regular_expression'], 10, True),
                            call(join('path', 'to', 'directory2'), config_values['regular_expression'], 10, True),
                            call(join('path', 'to', 'directory3'), config_values['regular_expression'], 10, True),
                        ], mock_shorten_dir.call_args_list)
                        print("Test passed!")


    def test_process_filename(self):
        """Test case: a file with a list of filenames is processed"""
        
        print("Running test_process_filename...")
        
        config_values = {
            'dictionary_path': 'dictionary.txt',
            'config_dir': 'path\\to\\config',
            'base_dir': os.path.join('path', 'to', 'base'),
            'output_dir': 'output_dir',
            'dir_scan_dir': 'dir_scan',
            'filename_scan_dir': 'filename_scan',
            'long_dir_path_scan_output': 'long_dir_path_scan',
            'long_filename_scan_output': 'long_filename_scan',
            'date_str': '20220101',
            'dir_length_threshold': 10,
            'filename_length_threshold': 15,
            'dry_run': True,
            'regular_expression': True
        }

        with patch('long_filepath_filename_shortener.CONFIG_VALUES', config_values):
            with patch('builtins.open', create=True) as mock_open:
                # Mocking the file content
                mock_open.return_value.__enter__.return_value = iter([
                    'mock_path1\n',
                    'mock_path2\n',
                    'mock_path3\n'
                ])

                # Mocking the glob.glob function
                with patch('glob.glob') as mock_glob:
                    mock_glob.return_value = iter([
                        join('path', 'to', 'file1.txt'),
                        join('path', 'to', 'file2.txt'),
                        join('path', 'to', 'file3.txt')
                    ])

                    # Mocking the shorten_long_filename function
                    with patch('long_filepath_filename_shortener.shorten_long_filename') as mock_shorten_filename:
                        print("Calling process_dir_or_filename('filename')...")
                        process_dir_or_filename('filename')

                        # Assert that the correct paths are processed
                        print("Checking if the correct paths were processed...")
                        self.assertEqual([
                            call('mock_path1', config_values['regular_expression'], 15, True),
                            call('mock_path2', config_values['regular_expression'], 15, True),
                            call('mock_path3', config_values['regular_expression'], 15, True)
                        ], mock_shorten_filename.call_args_list)
                        print("Test passed!")


    # def test_empty_file(self):
    #     print("Running test_empty_file...")
    #     with patch('long_filepath_filename_shortener.CONFIG_VALUES', self.config_values):
    #         with patch('builtins.open', create=True) as mock_open:
    #             mock_open.return_value.__enter__.return_value.readlines.return_value = []
    #             with patch('long_filepath_filename_shortener.shorten_long_dir') as mock_shorten_dir:
    #                 process_dir_or_filename('dir')
    #                 mock_shorten_dir.assert_not_called()
    #     print("Test passed!")

    # def test_non_existent_file(self):
    #     print("Running test_non_existent_file...")
    #     with patch('long_filepath_filename_shortener.CONFIG_VALUES', self.config_values):
    #         with patch('builtins.open', create=True, side_effect=FileNotFoundError):
    #             with self.assertRaises(FileNotFoundError):
    #                 process_dir_or_filename('dir')
    #     print("Test passed!")

    # def test_invalid_process_type(self):
    #     print("Running test_invalid_process_type...")
    #     with patch('long_filepath_filename_shortener.CONFIG_VALUES', self.config_values):
    #         with patch('builtins.open', create=True) as mock_open:
    #             mock_open.return_value.__enter__.return_value.readlines.return_value = ['/path/to/directory1']
    #             with self.assertRaises(ValueError):
    #                 process_dir_or_filename('invalid')
    #     print("Test passed!")

    # def test_file_reading_errors(self):
    #     print("Running test_file_reading_errors...")
    #     with patch('long_filepath_filename_shortener.CONFIG_VALUES', self.config_values):
    #         with patch('builtins.open', create=True, side_effect=IOError):
    #             with self.assertRaises(IOError):
    #                 process_dir_or_filename('dir')
    #     print("Test passed!")

    # def test_file_with_mixed_directories_and_filenames(self):
    #     print("Running test_file_with_mixed_directories_and_filenames...")
    #     with patch('long_filepath_filename_shortener.CONFIG_VALUES', self.config_values):
    #         with patch('builtins.open', create=True) as mock_open:
    #             mock_open.return_value.__enter__.return_value.readlines.return_value = [
    #                 '/path/to/directory1',
    #                 '/path/to/file1.txt'
    #             ]
    #             with patch('long_filepath_filename_shortener.shorten_long_dir') as mock_shorten_dir:
    #                 with patch('long_filepath_filename_shortener.shorten_long_filename') as mock_shorten_filename:
    #                     process_dir_or_filename('dir')
    #                     mock_shorten_dir.assert_called_once()
    #                     mock_shorten_filename.assert_not_called()
    #     print("Test passed!")

if __name__ == '__main__':
    unittest.main()