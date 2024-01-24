import os
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from long_filepath_filename_shortener import convert_components, load_dictionary


def test_convert_components():
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

test_convert_components()


def test_load_dictionary():
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
    except SystemExit as e:
        assert str(e) == "1"
        print("Test Case 2 Passed")
    except AssertionError:
        print("Test Case 2 Failed")

    # Test Case 3: Edge case with empty dictionary file
    with open('empty_dictionary.csv', 'w', newline='') as file:
        pass
    try:
        load_dictionary('empty_dictionary.csv')
    except SystemExit as e:
        assert str(e) == "1"
        print("Test Case 3 Passed")
    except AssertionError:
        print("Test Case 3 Failed")
    os.remove('empty_dictionary.csv')

test_load_dictionary()
