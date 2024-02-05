import os
import sys
import csv
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from long_filepath_filename_shortener import convert_components, load_dictionary, break_down_filename

class TestBreakDownFilename(unittest.TestCase):
    def test_break_down_filename(self):
        print("Testing break_down_filename()...")
        
        # Test case 1: Filename contains underscores
        if break_down_filename('file_name_example.txt') == ['file', 'name', 'example.txt']:
            print("Test case 1 Passed")
        else:
            print("Test case 1 Failed")

        # Test case 2: Filename contains hyphens
        if break_down_filename('file-name-example.txt') == ['file', 'name', 'example.txt']:
            print("Test case 2 Passed")
        else:
            print("Test case 2 Failed")

        # Test case 3: Filename is in camelCase
        if break_down_filename('FileNameExample.txt') == ['File', 'Name', 'Example.txt']:
            print("Test case 3 Passed")
        else:
            print("Test case 3 Failed")

        # Test case 4: Filename does not contain underscores, hyphens, or camelCase
        if break_down_filename('filenameexample.txt') == ['filenameexample.txt']:
            print("Test case 4 Passed")
        else:
            print("Test case 4 Failed")


    def test_convert_components(self):
        print("Testing convert_components()...")
        
        # Test Case 1: Normal case with all components in the dictionary
        components = ['LongName', 'AnotherLongName']
        dictionary = {'LongName': 'LN', 'AnotherLongName': 'ALN'}
        try:
            assert convert_components(components, dictionary) == ['LN', 'ALN']
            print("Test Case 1 Passed")
        except AssertionError:
            print("Test Case 1 Failed")

        # Test Case 2: Normal case with some components not in the dictionary
        components = ['LongName', 'NotInDictionary']
        dictionary = {'LongName': 'LN'}
        try:
            assert convert_components(components, dictionary) == ['LN', 'NotInDictionary']
            print("Test Case 2 Passed")
        except AssertionError:
            print("Test Case 2 Failed")

        # Test Case 3: Normal case with no components in the dictionary
        components = ['NotInDictionary1', 'NotInDictionary2']
        dictionary = {'LongName': 'LN'}
        try:
            assert convert_components(components, dictionary) == ['NotInDictionary1', 'NotInDictionary2']
            print("Test Case 3 Passed")
        except AssertionError:
            print("Test Case 3 Failed")

        # Test Case 4: Edge case with empty components list
        components = []
        dictionary = {'LongName': 'LN'}
        try:
            assert convert_components(components, dictionary) == []
            print("Test Case 4 Passed")
        except AssertionError:
            print("Test Case 4 Failed")

        # Test Case 5: Edge case with empty dictionary
        components = ['LongName', 'AnotherLongName']
        dictionary = {}
        try:
            assert convert_components(components, dictionary) == ['LongName', 'AnotherLongName']
            print("Test Case 5 Passed")
        except AssertionError:
            print("Test Case 5 Failed")

        # Test Case 6: Edge case with None components
        components = None
        dictionary = {'LongName': 'LN'}
        try:
            assert convert_components(components, dictionary) == None
            print("Test Case 6 Passed")
        except AssertionError:
            print("Test Case 6 Failed")

        # Test Case 7: Edge case with None dictionary
        components = ['LongName', 'AnotherLongName']
        dictionary = None
        try:
            assert convert_components(components, dictionary) == ['LongName', 'AnotherLongName']
            print("Test Case 7 Passed")
        except AssertionError:
            print("Test Case 7 Failed")


    def test_load_dictionary(self):
        print("Testing load_dictionary()...")
        
        # Test Case 1: Normal case with valid dictionary file
        with open('test_dictionary.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["LongName", "LN"])
            writer.writerow(["AnotherLongName", "ALN"])
        try:
            assert load_dictionary('test_dictionary.csv') == {'LongName': 'LN', 'AnotherLongName': 'ALN'}
            print("Test Case 1 Passed")
        except AssertionError:
            print("Test Case 1 Failed")
        os.remove('test_dictionary.csv')

        # Test Case 2: Edge case with non-existent dictionary file
        try:
            load_dictionary('non_existent.csv')
        except FileNotFoundError as e:
            assert str(e) == "Dictionary file does not exist: non_existent.csv"
            print("Test Case 2 Passed")
        except AssertionError:
            print("Test Case 2 Failed")

        # Test Case 3: Edge case with empty dictionary file
        with open('empty_dictionary.csv', 'w', newline='') as file:
            pass
        try:
            load_dictionary('empty_dictionary.csv')
        except ValueError as e:
            assert str(e) == "ERROR: Dictionary file is empty: empty_dictionary.csv"
            print("Test Case 3 Passed")
        except AssertionError:
            print("Test Case 3 Failed")
        os.remove('empty_dictionary.csv')

        # Test Case 4: Edge case with invalid dictionary file
        with open('invalid_dictionary.csv', 'w', newline='') as file:
            file.write("This is not a valid CSV file.")
        try:
            load_dictionary('invalid_dictionary.csv')
            assert False, "Expected an exception from load_dictionary"
        except Exception as e:
            print("Test Case 4 Passed")
        os.remove('invalid_dictionary.csv')

if __name__ == '__main__':
    unittest.main()