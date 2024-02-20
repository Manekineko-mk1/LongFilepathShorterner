import argparse
import datetime
import glob
import os
import logging
import csv
import configparser
import re

from utilities import check_long_path_support, write_to_csv, write_to_file
from datetime import datetime

def get_int_config_value(config, key, default):
    """ Get an integer configuration value. """
    try:
        return int(config.get('DEFAULT', key))
    except ValueError:
        logging.warning(f"Invalid '{key}' value. Using default value of {default}.")
        return default
    except TypeError:
        logging.error(f"Missing '{key}' value. Using default value of {default}.")
        return default

# Global variables
def read_config_values():
    """ Read the configuration values from the config.ini file. """
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    config_values = {
        'base_dir': config.get('DEFAULT', 'base_dir'),
        'config_dir': config.get('DEFAULT', 'config_dir'),
        'log_dir': config.get('DEFAULT', 'log_dir'),
        'output_dir': config.get('DEFAULT', 'output_dir'),
        'dir_scan_dir': config.get('DEFAULT', 'dir_scan_dir'),
        'filename_scan_dir': config.get('DEFAULT', 'filename_scan_dir'),
        'filename_length_threshold': get_int_config_value(config, 'filename_length_threshold', 200),
        'dir_length_threshold': get_int_config_value(config, 'dir_length_threshold', 200),
        'scan_entry_threshold': get_int_config_value(config, 'scan_entry_threshold', 1000),
        'number_of_retry': get_int_config_value(config, 'number_of_retry', 5),
        'dictionary_path': config.get('DEFAULT', 'dictionary_path'),        
        'long_dir_path_scan_output': config.get('DEFAULT', 'long_dir_path_scan_output'),
        'long_filename_scan_output': config.get('DEFAULT', 'long_filename_scan_output'),
        'long_filename_modified_output': config.get('DEFAULT', 'long_filename_modified_output'),
        'long_filename_modified_error': config.get('DEFAULT', 'long_filename_modified_error'),
        'long_dir_path_modified_output': config.get('DEFAULT', 'long_dir_path_modified_output'),
        'long_dir_path_modified_error': config.get('DEFAULT', 'long_dir_path_modified_error'),
        'dry_run': config.get('DEFAULT', 'dry_run'),
        'dry_run_dir': config.get('DEFAULT', 'dry_run_dir'),
        'date_str': datetime.now().strftime('%Y%m%d')
    }
    
    config_values['dry_run'] = True if config_values['dry_run'].lower() in ['true', '1', 'yes'] else False

    return config_values

CONFIG_VALUES = read_config_values()

def configure_logging(log_dir):
    """ Configure logging. """
    date_str = CONFIG_VALUES.get('date_str')
    logging.basicConfig(filename=f'{log_dir}/shortener_log_{date_str}.log', level=logging.DEBUG)
    logging.info("Starting the long path and long filename shortener script...")

configure_logging(CONFIG_VALUES.get('log_dir'))

def check_and_create_dirs(config_values):
    # Get the output directory from the config values
    output_dir = config_values['output_dir']

    # List of directories to check/create
    dirs_to_check = ['dir_scan_dir', 'filename_scan_dir', 'dry_run_dir']

    for dir_key in dirs_to_check:
        # Get the full path of the directory
        dir_path = os.path.join(output_dir, config_values[dir_key])

        # Check if the directory exists
        if not os.path.exists(dir_path):
            logging.info(f"Essential directory does not exist: {dir_path}. Creating it...")
            try:
                # If the directory doesn't exist, create it
                os.makedirs(dir_path)
                logging.info(f"Created directory: {dir_path}")
            except Exception as e:
                logging.error(f"Failed to create directory {dir_path}: {e}")

check_and_create_dirs(CONFIG_VALUES)

def load_dictionary(dictionary_path):
    """
    Loads a dictionary from a CSV file.

    This function reads a CSV file where each row contains two columns: a key and a value. 
    It creates a dictionary where the keys are the values from the first column and the values are the values from the second column.
    If the specified file does not exist or is empty, it logs an error and raises an exception.
    """
    if not os.path.isfile(dictionary_path):
        logging.error(f"Dictionary file does not exist: {dictionary_path}.")
        raise FileNotFoundError(f"Dictionary file does not exist: {dictionary_path}")
    
    try:
        with open(dictionary_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            dictionary_conversion_pairs = {rows[0].strip():rows[1].strip() for rows in reader}
    except Exception as e:
        logging.error(f"Failed to load dictionary: {str(e)}")
        print(f"Failed to load dictionary: {str(e)}. Proceeding with an empty dictionary.")
        dictionary = {}
        return dictionary
    
    if not dictionary_conversion_pairs:
        logging.error(f"ERROR: Dictionary file is empty: {dictionary_path}")
        raise ValueError(f"ERROR: Dictionary file is empty: {dictionary_path}")
    
    return dictionary_conversion_pairs


def break_down_filename(name):
    """
    Breaks down the filename into components based on delimiters or camelCase.

    This function splits a filename into components based on underscores (_) or hyphens (-), or breaks it down into separate words if it's in camelCase.
    If the filename does not contain any of these delimiters and is not in camelCase, it returns a list containing the filename as a single component.
    
    Example: 'myCamelCaseFile' -> ['my', 'Camel', 'Case', 'File']
    Example: 'my-file_name' -> ['my', 'file', 'name']
    """    
    # Search for the position of the file extension, if it exists
    extension_match = re.search(r'\.\w+$', name)
    if extension_match:
        # If an extension is found, split the name at the start of the extension
        base_name = name[:extension_match.start()]
        extension = [name[extension_match.start():]]  # Include the dot with the extension
    else:
        base_name = name
        extension = []

    # Split at underscore, hyphen, and preserve digit-based decimals
    parts = re.split(r'(?<!\d)[_.](?!\d)|(?<=\d)[_.](?!\d)|[-_]', base_name)

    # Split camelCase in each part and avoid splitting in digit sequences
    def split_camel_case(s):
        return re.sub('([a-z])([A-Z])', r'\1 \2', s).split()

    parts = [split_camel_case(part) for part in parts]
    parts = [item for sublist in parts for item in sublist]  # Flatten the list

    # Append extension if present
    if extension:
        parts += extension

    return parts

def break_down_dir(name):
    """
    Breaks down the dir into components based on delimiters or camelCase.

    This function splits a folder name into components based on underscores (_) or hyphens (-), or breaks it down into separate words if it's in camelCase.
    If the filename does not contain any of these delimiters and is not in camelCase, it returns a list containing the filename as a single component.
    
    Example: 'myCamelCaseFile' -> ['my', 'Camel', 'Case', 'File']
    Example: 'my-file_name' -> ['my', 'file', 'name']
    """    

    # Split at underscore, hyphen, and preserve digit-based decimals
    #parts = re.split(r'(?<!\d)[_.](?!\d)|(?<=\d)[_.](?!\d)|[-_]', name)
    
    # Split at underscore, hyphen, and preserve digit-based decimals and dot between strings
    parts = re.split(r'(?<!\d)[_.](?!\d)(?<!\w)[_.](?!\w)|(?<=\d)[_.](?!\d)|[-_]', name)

    # Split camelCase in each part and avoid splitting in digit sequences
    def split_camel_case(s):
        return re.sub('([a-z])([A-Z])', r'\1 \2', s).split()

    parts = [split_camel_case(part) for part in parts]
    parts = [item for sublist in parts for item in sublist]  # Flatten the list

    return parts

def convert_components(components, dictionary):
    """
    Converts components of a filename using a provided dictionary.

    This function iterates over a list of components and replaces each component with its corresponding value in the dictionary, if it exists. 
    If a component does not exist in the dictionary, it is left unchanged. 
    If the components or dictionary are None, the function handles it gracefully.
    """
    
    if components is None:
        return None
    if dictionary is None:
        return components
    
    return [dictionary.get(component, component) for component in components]


def check_for_naming_conflict(file_path, new_name):
    """
    Checks for naming conflicts when renaming a file.

    This function attempts to rename a file to `new_name` up to a specified number of times (default is 5). 
    If a file with the new name already exists, it appends a number to the end of the name and tries again. 
    If it still can't rename the file after the specified number of attempts, it logs an error and returns None.
    """
    name, ext = os.path.splitext(new_name)
    
    for i in range(CONFIG_VALUES.get('number_of_retry')):
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        logging.info(f"Checking for naming conflict: {new_name}")
        print(f"Checking for naming conflict: {new_name}")
        
        if not os.path.exists(new_file_path):
            logging.info(f"No naming conflict found for file: {file_path} | New name: {new_name}")
            print(f"No naming conflict found for file: {file_path} | New name: {new_name}")
            return new_file_path
        else:
            new_name = f"{name.rsplit('_', 1)[0]}_{i+1}{ext}"
            logging.info(f"Naming conflict found for file: {file_path} | New name: {new_name}. Trying again...")
            print(f"Naming conflict found for file: {file_path} | New name: {new_name}. Trying again...")
    
    logging.error(f"Failed to rename file after 10 attempts: {file_path}")
    return None


def rename_filename(file_path, new_file_path):
    """
    Renames a file and logs the operation.

    This function attempts to rename a file from `file_path` to `new_file_path`. 
    If the operation is successful, it logs the new file path and writes the old and new file paths to a CSV file. 
    If the operation fails due to the file not being found or a permission error, it logs the error and writes the old file path and the error to a CSV file.
    """
    
    long_filename_modified_output = CONFIG_VALUES.get('long_filename_modified_output')
    long_filename_modified_error = CONFIG_VALUES.get('long_filename_modified_error')
    date_str = CONFIG_VALUES.get('date_str')
    output_dir = CONFIG_VALUES.get('output_dir')
    
    logging.info(f"Attempting to rename filename from: {file_path} to {new_file_path}")
    print(f"Attempting to rename filename from: {file_path} to {new_file_path}")
    
    try:
        os.rename(file_path, new_file_path)
        logging.info(f"Filename rename successed. Renamed filename from: {file_path} to {new_file_path}")
        print(f"Filename rename successed. Renamed filename from: {file_path} to {new_file_path}")
        
        with open(f'{output_dir}/{long_filename_modified_output}_{date_str}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_path])
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")
        with open(f'{output_dir}/{long_filename_modified_error}_{date_str}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, str(e)])


def shorten_long_filename(file_path, dictionary_path, filename_length_threshold, dry_run):
    """
    Renames a file to a shorter name based on a provided dictionary.

    This function breaks down the filename into components, converts the components using a dictionary, 
    and then joins the components back together to form a new filename. 
    If a naming conflict occurs, it tries to resolve the conflict by appending a number to the filename. 
    If the new filename is still too long after conversion, it logs an error and does not rename the file.
    """
    logging.info(f"Processing file: {file_path} | Dry Run: {dry_run} | Filename length threshold: {filename_length_threshold}")
    print(f"Processing file: {file_path} | Dry Run: {dry_run} | Filename length threshold: {filename_length_threshold}")
    
    dictionary = load_dictionary(dictionary_path)

    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    components = break_down_filename(filename)
    new_components = convert_components(components, dictionary)
    
    logging.info(f"Filename components: {components}")
    print(f"Filename components: {components}")
    
    logging.info(f"New filename components: {new_components}")
    print(f"New filename components: {new_components}")
    
    new_name = '-'.join(new_components[:-1]) + ext
    
    if len(new_name) > filename_length_threshold:
        logging.error(f"New filename is over threshold: {new_name} | New filename length: {len(new_name)} | Threshold: {filename_length_threshold}")
        # return None
    
    new_file_path = check_for_naming_conflict(file_path, new_name)
    if new_file_path is None:
        logging.error(f"Could not resolve naming conflict for file: {file_path}. Skipping...")
        return None
    
    if dry_run:
        long_filename_modified_output = CONFIG_VALUES.get('long_filename_modified_output')
        simulate_rename(file_path, new_file_path, long_filename_modified_output)        
    else:        
        rename_filename(file_path, new_file_path)


def simulate_rename(old_dir_path, new_dir_path, output_file_path):
    dry_run_dir = CONFIG_VALUES.get('dry_run_dir')    
    output_dir = CONFIG_VALUES.get('output_dir')
    date_str = CONFIG_VALUES.get('date_str')
    
    #logging.info(f"dry_run_dir: {dry_run_dir} | output_file_path: {output_file_path} | output_dir: {output_dir} | date_str: {date_str}")
    logging.info(f"Dry Run: Simulating rename of '{old_dir_path}' to '{new_dir_path}'")
    write_to_csv(f'{output_dir}/{dry_run_dir}/dry_run_{output_file_path}_{date_str}.csv', [old_dir_path, new_dir_path])


def shorten_long_dir(dir_path, dictionary_path, dir_length_threshold, dry_run):
    """
    Renames a directory to a shorter name based on a provided dictionary.

    This function breaks down the directory path into components, converts the components using a dictionary, 
    and then joins the components back together to form a new directory path. 
    If a naming conflict occurs, it tries to resolve the conflict by appending a number to the directory name. 
    If the new directory path is still too long after conversion, it logs an error and does not rename the directory.
    """
    dir_path = os.path.dirname(dir_path)
    
    logging.info(f"Processing directory shorten process on: {dir_path} | dir_length: {len(dir_path)} | dir_length_threshold: {dir_length_threshold}")
    print(f"Processing directory shorten process on: {dir_path} | dir_length: {len(dir_path)} | dir_length_threshold: {dir_length_threshold}")
    
    # Check if directory is already within the threshold
    if len(dir_path) <= dir_length_threshold:
        return dir_path
    
    dictionary = load_dictionary(dictionary_path)
    dir_components = [break_down_filename(component) for component in dir_path.split(os.sep)]
    # new_dir_components = convert_components(dir_components, dictionary)
    new_dir_components = [convert_components(component, dictionary) for component in dir_components]
    
    org_dir_path_components = dir_path.split(os.sep)
    
    print(f"Directory components: {dir_components}")
    logging.info(f"Directory components: {dir_components}")
    
    print(f"New directory components: {new_dir_components}")
    logging.info(f"New directory components: {new_dir_components}")
    
    # Check if the renamed path will be within the threshold
    # new_path = os.sep.join('-'.join(component) for component in new_dir_components)
    # if len(new_path) > dir_length_threshold:
    #     print(f"New directory path is still too long: {new_path} | New directory length: {len(new_path)} | Threshold: {dir_length_threshold}")
    #     logging.error(f"New directory path is still too long: {new_path} | New directory length: {len(new_path)} | Threshold: {dir_length_threshold}")
        # return None

    # Start from the end of the path and work towards the root
    for i in range(len(new_dir_components) - 1, 6, -1):
        # Skip if the original and new directory components are the same
        if dir_components[i] == new_dir_components[i]:
            print(f"No change for sub-folder: {os.sep.join(org_dir_path_components[:i+1])}  | Moving one level up and continue the check ...")
            logging.info(f"No change for sub-folder: {os.sep.join(org_dir_path_components[:i+1])} | Moving one level up and continue the check ...")
            continue
        
        #old_dir_path = os.sep.join(['-'.join(component) for component in dir_components[:i+1]])
        old_dir_path = os.sep.join(org_dir_path_components[:i+1])
        #new_dir_path = os.sep.join(['-'.join(component) for component in dir_components[:i]] + ['-'.join(component) for component in new_dir_components[i]])
        new_dir_path = os.sep.join(org_dir_path_components[:i] + ['-'.join(new_dir_components[i])])
        
        print(f"Attempting to rename: {old_dir_path} to {new_dir_path}")
        
        # Skip if the old and new directory names are the same
        if old_dir_path == new_dir_path:
            logging.info(f"Old and new directory names are the same: {old_dir_path} - No need to rename, skipping...")
            continue
        
        # Try to rename
        if dry_run:
            long_dir_path_modified_output = CONFIG_VALUES.get('long_dir_path_modified_output')
            simulate_rename(old_dir_path, new_dir_path, long_dir_path_modified_output)
        else:
            new_dir_path = rename_dir(old_dir_path, new_dir_path)
        
        if len(new_dir_path) <= dir_length_threshold:
            logging.info(f"Completed shorten process on: {dir_path} | New folder path: {new_dir_path} | New folder length: {len(new_dir_path)}")
            print(f"Completed shorten process on: {dir_path} | New folder path: {new_dir_path} | New folder length: {len(new_dir_path)}")
            break
        
    return new_dir_path


def rename_dir(old_dir_path, new_dir_path):
    """
    Renames a directory.

    This function renames a directory from `old_dir_path` to `new_dir_path`. 
    If a directory with the new name already exists, it appends a number to the new name to avoid a naming conflict.
    """
    
    long_dir_path_modified_output = CONFIG_VALUES.get('long_dir_path_modified_output')
    long_dir_path_modified_error = CONFIG_VALUES.get('long_dir_path_modified_error')
    output_dir = CONFIG_VALUES.get('output_dir')
    date_str = CONFIG_VALUES.get('date_str')
    number_of_retry = CONFIG_VALUES.get('number_of_retry')
    
    try:
        os.rename(old_dir_path, new_dir_path)
        logging.info(f"Renamed folder from '{old_dir_path}' to '{new_dir_path}'")
        write_to_csv(f'{output_dir}/{long_dir_path_modified_output}_{date_str}.csv', [old_dir_path, new_dir_path])
        return new_dir_path
    except FileExistsError as e:
        logging.warning(f"Directory already exists: {new_dir_path}")
        
        # A directory with the new name already exists, so append a number to the new name
        for i in range(1, number_of_retry + 1):
            try: 
                new_dir_path_retry = f"{new_dir_path}_{i}"
                os.rename(old_dir_path, new_dir_path_retry)
                
                logging.info(f"Renamed '{old_dir_path}' to '{new_dir_path_retry}'")
                print(f"Renamed '{old_dir_path}' to '{new_dir_path}'")
                write_to_csv(f'{output_dir}/{long_dir_path_modified_output}_{date_str}.csv', [old_dir_path, new_dir_path_retry])
                return new_dir_path_retry
            except FileExistsError:
                continue
                
        logging.error(f"Failed to rename '{old_dir_path}' to '{new_dir_path}' after {number_of_retry} attempts")
        write_to_csv(f'{output_dir}/{long_dir_path_modified_error}_{date_str}.csv', [new_dir_path, "Failed to rename after multiple attempts"])
    except (OSError, PermissionError, Exception) as e:
            logging.error(f"Failed to rename '{old_dir_path}' to '{new_dir_path}': {e}")
            print(f"Failed to rename '{old_dir_path}' to '{new_dir_path}': {e}")
            
            write_to_csv(f'{output_dir}/{long_dir_path_modified_error}_{date_str}.csv', [new_dir_path, str(e)])
            return None


def handle_long_filename(file_path, long_filename_list_file):
    """ Checks if a filename exceeds a specified length and logs it if it does. """
    filename_length_threshold = CONFIG_VALUES.get('filename_length_threshold')
    
    if len(os.path.basename(file_path)) >= filename_length_threshold:
        logging.info(f"Found long filename: {os.path.basename(file_path)}")
        write_to_file(long_filename_list_file, file_path)


def handle_long_dir_path(file_path, long_file_path_list_file):
    """ Checks if a nested directory path is exceeds a specified length and logs it if it does. """
    
    print(f"Checking file path: {file_path}")
    print(f"Dirname: {os.path.dirname(file_path)}")
    print(f"Dirname length: {len(os.path.dirname(file_path))}")
    
    dir_length_threshold = CONFIG_VALUES.get('dir_length_threshold')
    
    if len(os.path.dirname(file_path)) >= dir_length_threshold:
        logging.info(f"Found long directories path: {file_path} | Length: {len(os.path.dirname(file_path))} | Threshold: {dir_length_threshold}")
        write_to_file(long_file_path_list_file, file_path)


def scan_long_paths_and_long_filename(base_dir, counters):
    """
    Scans a directory for files with long paths or filenames.

    This function recursively scans all files in a directory and its subdirectories. 
    If it finds a file with a path length >= `dir_length_threshold` or a filename length >= to `filename_length_threshold`, 
    it logs the file and writes its path to a specified file.
    """
    base_dir = os.path.abspath(base_dir)
    print(f"Scanning base directory: {base_dir}")
    
    if base_dir.startswith('\\') is False:
        long_base_dir = "\\\\?\\" + base_dir
        print(f"Modified base directory: {long_base_dir}")
    else:
        long_base_dir = base_dir
        
    filename_length_threshold = CONFIG_VALUES.get('filename_length_threshold')
    dir_length_threshold = CONFIG_VALUES.get('dir_length_threshold')
    scan_entry_threshold = CONFIG_VALUES.get('scan_entry_threshold')
    output_dir = CONFIG_VALUES.get('output_dir')
    filename_scan_dir = CONFIG_VALUES.get('filename_scan_dir')
    long_filename_scan_output = CONFIG_VALUES.get('long_filename_scan_output')
    dir_scan_dir = CONFIG_VALUES.get('dir_scan_dir')
    long_dir_path_scan_output = CONFIG_VALUES.get('long_dir_path_scan_output')
    date_str = CONFIG_VALUES.get('date_str')

    for entry in os.scandir(long_base_dir):
        if entry.is_file():
            file_path = entry.path
                
            # logging.info(f"File path: {file_path}")
            # logging.info(f"Checking file: {entry.name}")
            # logging.info(f"Filename length: {len(entry.name)}")
                
            if len(os.path.basename(file_path)) >= filename_length_threshold:
                if counters['filename_counter'] >= scan_entry_threshold:
                    counters['filename_file_part'] += 1
                    counters['filename_counter'] = 0
                counters['filename_counter'] += 1
                with open(f'{output_dir}/{filename_scan_dir}/{long_filename_scan_output}_{date_str}_part{counters["filename_file_part"]}.txt', 'a', encoding='utf-8') as long_filename_list_file:
                    logging.info(f"Found long filename: {os.path.basename(file_path)}")
                    write_to_file(long_filename_list_file, file_path)

            if len(os.path.dirname(file_path)) >= dir_length_threshold:
                if counters['dir_counter'] >= scan_entry_threshold:
                    counters['dir_file_part'] += 1
                    counters['dir_counter'] = 0
                counters['dir_counter'] += 1
                with open(f'{output_dir}/{dir_scan_dir}/{long_dir_path_scan_output}_{date_str}_part{counters["dir_file_part"]}.txt', 'a', encoding='utf-8') as long_file_path_list_file:
                    logging.info(f"Found long directories path: {file_path} | Length: {len(os.path.dirname(file_path))} | Threshold: {dir_length_threshold}")
                    write_to_file(long_file_path_list_file, file_path)
                
        elif entry.is_dir():
            scan_long_paths_and_long_filename(entry.path, counters)


def process_scan():
    """
    Process the scan for long paths and long filenames.

    This function checks if long path support is enabled. If it is enabled, it logs a message to disable it.
    If long path support is disabled, it scans for long paths and long filenames using the BASE_DIR as the starting point.
    """
    base_dir = CONFIG_VALUES.get('base_dir')
    
    counters = {'dir_counter': 0, 'filename_counter': 0, 'dir_file_part': 1, 'filename_file_part': 1}
    scan_long_paths_and_long_filename(base_dir, counters)
    
    # if check_long_path_support(base_dir) is True:
    #     logging.info("Long path support is enabled. Please disable it by setting the registry key LongPathsEnabled to 0 to simulate long path errors.")
    # else:
    #     logging.info("Long path support is disabled. Scanning for long paths and long filenames.")
    #     counters = {'dir_counter': 0, 'filename_counter': 0, 'dir_file_part': 1, 'filename_file_part': 1}
    #     scan_long_paths_and_long_filename(base_dir, counters)


def process_dir_or_filename(process_type):
    """
    Process directory or filename based on the given process_type.
    This is the entry point for the shortening process.
    """
    config_dir = CONFIG_VALUES.get('config_dir')
    dictionary_path = os.path.join(config_dir, CONFIG_VALUES.get('dictionary_path'))
    output_dir = CONFIG_VALUES.get('output_dir')
    dir_scan_dir = CONFIG_VALUES.get('dir_scan_dir')
    filename_scan_dir = CONFIG_VALUES.get('filename_scan_dir')
    long_dir_path_scan_output = CONFIG_VALUES.get('long_dir_path_scan_output')
    long_filename_scan_output = CONFIG_VALUES.get('long_filename_scan_output')
    date_str = CONFIG_VALUES.get('date_str')
    dry_run = CONFIG_VALUES.get('dry_run')
    
    scan_dir = (dir_scan_dir if process_type == 'dir' else filename_scan_dir)
    file_pattern = f"{long_dir_path_scan_output if process_type == 'dir' else long_filename_scan_output}_{date_str}_part*"
    
    print(f"Scan directory: {scan_dir} | Dictionary path: {dictionary_path}")
    print(f"Processing type: {process_type} | Dry Run: {dry_run} | File pattern: {file_pattern}")
    print(f"os.path.join(scan_dir, file_pattern) => {os.path.join(output_dir, scan_dir, file_pattern)}")
    print(f"Glob glob result: {glob.glob(os.path.join(output_dir, scan_dir, file_pattern))}")

    for file_path in glob.glob(os.path.join(output_dir, scan_dir, file_pattern)):
        try:
            with open(file_path, 'r') as f:                
                for line in f:
                    path = line.strip()
                    logging.info(f"\nProcess Type: {process_type} |  Processing path: {path}")
                    if process_type == 'dir':
                        dir_length_threshold = CONFIG_VALUES.get('dir_length_threshold')
                        shorten_long_dir(path, dictionary_path, dir_length_threshold, dry_run)
                    else:
                        filename_length_threshold = CONFIG_VALUES.get('filename_length_threshold')
                        shorten_long_filename(path, dictionary_path, filename_length_threshold, dry_run)
        except OSError or Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Shorten long file names or directory paths.')
    parser.add_argument('-p', '--process', choices=['dir', 'filename', 'scan'], default='dir', help='Specify whether to process directories, filenames, or perform a scan.')
    args = parser.parse_args()

    print(f"Base directory: {CONFIG_VALUES.get('base_dir')}")
    print(f"Filename length threshold: {CONFIG_VALUES.get('filename_length_threshold')}")
    print(f"Directory length threshold: {CONFIG_VALUES.get('dir_length_threshold')}")
    
    if args.process == 'scan':
        process_scan()
    else:
        process_dir_or_filename(args.process)


if __name__ == "__main__":
    main()
