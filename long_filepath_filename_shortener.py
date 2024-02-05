import argparse
import datetime
import glob
import os
import logging
import csv
import configparser
import re
import sys

from utilities import check_long_path_support, write_to_csv, write_to_file
from datetime import datetime

# TODO
# 1. Batching output for the scan_long_paths_and_long_filename function
# 2. Create a function to simulate the shortening process on the long paths and long filenames
# 3. Add a function to handle initialization of the shortening process. 
# 3.1 User will start the shortening process by using the -p flag, -p dir or -p file
# 3.2 If the user uses the -p dir flag, the script will check for the long_dir_path_scan_output file and start the shortening process on the path listed in the file
# 3.3 If the user uses the -p file flag, the script will check for the long_filename_scan_output file and start the shortening process on the path listed in the file
# 3.4 If the user uses the -test flag together with either -p dir or -p file, then the script should call the simulation function 
#       to simulate the shortening process


def initConfigValues():
    """ Initialize the configuration values from the config.ini file. """
    global config, log_dir, date_str, BASE_DIR, OUTPUT_DIR, DIR_SCAN_DIR, FILENAME_SCAN_DIR
    global LONG_DIR_PATH_SCAN_OUTPUT, LONG_FILENAME_SCAN_OUTPUT, NUMBER_OF_RETRY
    global FILE_LENGTH_THRESHOLD, DIR_LENGTH_THRESHOLD, SCAN_ENTRY_THRESHOLD
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    log_dir = config.get('DEFAULT', 'log_dir')
    BASE_DIR = config.get('DEFAULT', 'base_dir')
    OUTPUT_DIR = config.get('DEFAULT', 'output_dir')
    DIR_SCAN_DIR = config.get('DEFAULT', 'dir_scan_dir')
    FILENAME_SCAN_DIR = config.get('DEFAULT', 'filename_scan_dir')
    
    date_str = datetime.now().strftime('%Y%m%d')
    
    LONG_DIR_PATH_SCAN_OUTPUT = config.get('DEFAULT', 'long_dir_path_scan_output')
    LONG_FILENAME_SCAN_OUTPUT = config.get('DEFAULT', 'long_filename_scan_output')
    
    try:
        NUMBER_OF_RETRY = int(config.get('DEFAULT', 'number_of_retry'))
    except (ValueError, TypeError):
        logging.warning(f"Invalid 'number_of_retry' value: {NUMBER_OF_RETRY}. Using default value of 5.")
        NUMBER_OF_RETRY = 5
    
    try:
        FILE_LENGTH_THRESHOLD = int(config.get('DEFAULT', 'file_length_threshold'))
    except (ValueError, TypeError):
        logging.warning(f"Invalid 'file_length_threshold' value: {FILE_LENGTH_THRESHOLD}. Using default value of 200.")
        FILE_LENGTH_THRESHOLD = 200
    
    try:
        DIR_LENGTH_THRESHOLD = int(config.get('DEFAULT', 'dir_length_threshold'))
    except (ValueError, TypeError):
        logging.warning(f"Invalid 'dir_length_threshold' value: {DIR_LENGTH_THRESHOLD}. Using default value of 200.")
        DIR_LENGTH_THRESHOLD = 200
    
    try:
        SCAN_ENTRY_THRESHOLD = int(config.get('DEFAULT', 'scan_entry_threshold'))
    except (ValueError, TypeError):
        logging.warning(f"Invalid 'scan_entry_threshold' value: {SCAN_ENTRY_THRESHOLD}. Using default value of 1000.")
        SCAN_ENTRY_THRESHOLD = 1000
    
    
    # Configure logging
    logging.basicConfig(filename=f'{log_dir}/shortener_log_{date_str}.log', level=logging.DEBUG)
    logging.info("Starting the long path and long filename shortener script...")
    logging.info(f"File length threshold: {FILE_LENGTH_THRESHOLD}")
    logging.info(f"Directory length threshold: {DIR_LENGTH_THRESHOLD}")
    logging.info(f"Number of retry: {NUMBER_OF_RETRY}")
    logging.info(f"Log directory: {log_dir}")
    logging.info(f"Output directory: {OUTPUT_DIR}")
    logging.info(f"Long directory path scan output: {LONG_DIR_PATH_SCAN_OUTPUT}")
    logging.info(f"Long filename scan output: {LONG_FILENAME_SCAN_OUTPUT}")


def load_dictionary(dictionary_path):
    """
    Loads a dictionary from a CSV file.

    This function reads a CSV file where each row contains two columns: a key and a value. 
    It creates a dictionary where the keys are the values from the first column and the values are the values from the second column.
    If the specified file does not exist or is empty, it logs an error and terminates the script.

    Parameters:
    dictionary_path (str): The path to the CSV file.

    Returns:
    dict: The dictionary loaded from the CSV file.

    Raises:
    SystemExit: If the file does not exist or is empty.
    """
    if not os.path.isfile(dictionary_path):
        logging.error(f"Dictionary file does not exist: {dictionary_path}. Terminating script.")
        sys.exit(1)
    
    with open(dictionary_path, 'r') as f:
        reader = csv.reader(f)
        dictionary = {rows[0]:rows[1] for rows in reader}
    
    if not dictionary:
        logging.error(f"Dictionary file is empty: {dictionary_path}")
        sys.exit(1)
    
    return dictionary


def break_down_filename(name):
    """
    Breaks down the filename into components based on delimiters or camelCase.

    This function splits a filename into components based on underscores (_) or hyphens (-), or breaks it down into separate words if it's in camelCase.
    If the filename does not contain any of these delimiters and is not in camelCase, it returns a list containing the filename as a single component.

    Parameters:
    name (str): The filename to break down.

    Returns:
    list: The components of the filename.
    """
    if '_' in name or '-' in name:
        return re.split('_|-', name)
    elif re.findall('[A-Z][^A-Z]*', name):
        return re.findall('[A-Z][^A-Z]*', name)
    else:
        return [name]


def convert_components(components, dictionary):
    """
    Converts components of a filename using a provided dictionary.

    This function iterates over a list of components and replaces each component with its corresponding value in the dictionary, if it exists. 
    If a component does not exist in the dictionary, it is left unchanged. 
    If the components or dictionary are None, the function handles it gracefully.

    Parameters:
    components (list): The list of components to convert.
    dictionary (dict): The dictionary to use for conversion.

    Returns:
    list: The list of converted components, or None if the input components was None.
    """
    
    if components is None:
        return None
    if dictionary is None:
        return components
    
    return [dictionary.get(component, component) for component in components]


def check_for_naming_conflict(file_path, new_name, ext):
    """
    Checks for naming conflicts when renaming a file.

    This function attempts to rename a file to `new_name` up to a specified number of times (default is 5). 
    If a file with the new name already exists, it appends a number to the end of the name and tries again. 
    If it still can't rename the file after the specified number of attempts, it logs an error and returns None.

    Parameters:
    file_path (str): The original path of the file to be renamed.
    new_name (str): The new name for the file, without the extension.
    ext (str): The file extension.

    Returns:
    str: The new file path if the file was successfully renamed, or None if it wasn't.
    """
    
    for i in range(NUMBER_OF_RETRY):
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        if not os.path.exists(new_file_path):
            return new_file_path
        new_name = f"{new_name.rsplit('_', 1)[0]}_{i+1}{ext}"
    
    logging.error(f"Failed to rename file after 10 attempts: {file_path}")
    return None


def rename_filename(file_path, new_file_path, output_dir):
    """
    Renames a file and logs the operation.

    This function attempts to rename a file from `file_path` to `new_file_path`. 
    If the operation is successful, it logs the new file path and writes the old and new file paths to a CSV file. 
    If the operation fails due to the file not being found or a permission error, it logs the error and writes the old file path and the error to a CSV file.

    Parameters:
    file_path (str): The original path of the file to be renamed.
    new_file_path (str): The new path for the file.
    output_dir (str): The directory where the CSV log files are stored.

    """
    
    long_filename_modified_output = config.get('DEFAULT', 'long_filename_modified_output')
    long_filename_modified_error = config.get('DEFAULT', 'long_filename_modified_error')
    
    try:
        os.rename(file_path, new_file_path)
        logging.info(f"Renamed file to: {new_file_path}")
        with open(f'{output_dir}/{long_filename_modified_output}_{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_path])
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")
        with open(f'{output_dir}/{long_filename_modified_error}_{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, str(e)])


def shorten_long_filename(file_path, dictionary_path, file_length_threshold):
    """
    Renames a file to a shorter name based on a provided dictionary.

    This function breaks down the filename into components, converts the components using a dictionary, 
    and then joins the components back together to form a new filename. 
    If a naming conflict occurs, it tries to resolve the conflict by appending a number to the filename. 
    If the new filename is still too long after conversion, it logs an error and does not rename the file.

    Parameters:
    file_path (str): The original path of the file to be renamed.
    dictionary_path (str): The path to the CSV file containing the dictionary for conversion.
    file_length (int): The maximum allowed length for the new filename.

    """
    logging.info(f"Processing file: {file_path}")
    
    dictionary = load_dictionary(dictionary_path)

    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    components = break_down_filename(name)
    new_components = convert_components(components, dictionary)
    new_name = '-'.join(new_components) + ext
    
    if len(new_name) > file_length_threshold:
        logging.error(f"New filename is too long: {new_name}")
        return None
    
    new_file_path = check_for_naming_conflict(file_path, new_name, ext)
    if new_file_path is None:
        logging.error(f"Could not resolve naming conflict for file: {file_path}")
        return None
    
    logging.info(f"Renaming file to: {new_file_path}")
    print(f"Renaming file to: {new_file_path}")
    rename_filename(file_path, new_file_path, OUTPUT_DIR)


def shorten_long_dir(dir_path, dictionary_path, dir_length_threshold, dry_run=True):
    """
    Renames a directory to a shorter name based on a provided dictionary.

    This function breaks down the directory path into components, converts the components using a dictionary, 
    and then joins the components back together to form a new directory path. 
    If a naming conflict occurs, it tries to resolve the conflict by appending a number to the directory name. 
    If the new directory path is still too long after conversion, it logs an error and does not rename the directory.

    Parameters:
    dir_path (str): The original path of the directory to be renamed.
    dictionary_path (str): The path to the CSV file containing the dictionary for conversion.
    dir_length (int): The maximum allowed length for the new directory path.

    """
    logging.info(f"Processing directory shorten process on: {dir_path} | dir_length_threshold: {dir_length_threshold}")
    print(f"Processing directory shorten process on: {dir_path} | dir_length: {len(dir_path)} | dir_length_threshold: {dir_length_threshold}")
    
    # Check if directory is already within the threshold
    if len(dir_path) <= dir_length_threshold:
        return dir_path
    
    dictionary = load_dictionary(dictionary_path)
    dir_components = dir_path.split(os.sep)
    new_dir_components = convert_components(dir_components, dictionary)
    
    # Check if the renamed path will be within the threshold
    new_path = os.sep.join(new_dir_components)
    if len(new_path) > dir_length_threshold:
        logging.error(f"Not possible to convert the folder path to the threshold!! Skipping the shorten process! | Original path: {dir_path} | Please consider updating the dictionary.")
        print(f"Not possible to convert the folder path to the threshold!! Skipping the shorten process!  | Original path: {dir_path} | Please consider updating the dictionary.")
        return None

    # Start from the end of the path and work towards the root
    for i in range(len(new_dir_components) - 1, 0, -1):
        old_dir_path = os.sep.join(dir_components[:i+1])
        new_dir_path = os.sep.join(dir_components[:i] + [new_dir_components[i]])
        
        # Skip if the old and new directory names are the same
        if old_dir_path == new_dir_path:
            print(f"Old and new directory names are the same: {old_dir_path} - No need to rename, skipping...")
            continue
        
        # Try to rename
        if dry_run:
            dry_run_dir = config.get('DEFAULT', 'dry_run_dir')
            long_dir_path_modified_output = config.get('DEFAULT', 'long_dir_path_modified_output')
            
            logging.info(f"Dry Run: Simulating rename of '{old_dir_path}' to '{new_dir_path}'")
            write_to_csv(f'{OUTPUT_DIR}/{dry_run_dir}/dry_run_{long_dir_path_modified_output}_{date_str}.csv', [old_dir_path, new_dir_path])
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

    Parameters:
    old_dir_path (str): The original path of the directory to be renamed.
    new_dir_path (str): The new path for the directory.
    """
    
    long_dir_path_modified_output = config.get('DEFAULT', 'long_dir_path_modified_output')
    long_dir_path_modified_error = config.get('DEFAULT', 'long_dir_path_modified_error')
    
    try:
        os.rename(old_dir_path, new_dir_path)
        logging.info(f"Renamed folder to: {new_dir_path}")
        write_to_csv(f'{OUTPUT_DIR}/{long_dir_path_modified_output}_{date_str}.csv', [old_dir_path, new_dir_path])
        return new_dir_path
    except FileExistsError as e:
        logging.warning(f"Directory already exists: {new_dir_path}")
        
        # A directory with the new name already exists, so append a number to the new name
        for i in range(1, NUMBER_OF_RETRY + 1):
            try: 
                new_dir_path_retry = f"{new_dir_path}_{i}"
                os.rename(old_dir_path, new_dir_path_retry)
                
                logging.info(f"Renamed '{old_dir_path}' to '{new_dir_path_retry}'")
                print(f"Renamed '{old_dir_path}' to '{new_dir_path}'")
                write_to_csv(f'{OUTPUT_DIR}/{long_dir_path_modified_output}_{date_str}.csv', [old_dir_path, new_dir_path_retry])
                return new_dir_path_retry
            except FileExistsError:
                continue
                
        logging.error(f"Failed to rename '{old_dir_path}' to '{new_dir_path}' after {NUMBER_OF_RETRY} attempts")
        write_to_csv(f'{OUTPUT_DIR}/{long_dir_path_modified_error}_{date_str}.csv', [new_dir_path, "Failed to rename after multiple attempts"])
    except (OSError, PermissionError, Exception) as e:
            logging.error(f"Failed to rename '{old_dir_path}' to '{new_dir_path}': {e}")
            print(f"Failed to rename '{old_dir_path}' to '{new_dir_path}': {e}")
            
            write_to_csv(f'{OUTPUT_DIR}/{long_dir_path_modified_error}_{date_str}.csv', [new_dir_path, str(e)])
            return None


def handle_long_filename(file_path, long_filename_list_file):
    """ Checks if a filename exceeds a specified length and logs it if it does. """
    if len(os.path.basename(file_path)) >= FILE_LENGTH_THRESHOLD:
        logging.info(f"Found long filename: {os.path.basename(file_path)}")
        write_to_file(long_filename_list_file, file_path)


def handle_long_dir_path(file_path, long_file_path_list_file):
    """ Checks if a nested directory path is exceeds a specified length and logs it if it does. """
    
    print(f"Checking file path: {file_path}")
    print(f"Dirname: {os.path.dirname(file_path)}")
    print(f"Dirname length: {len(os.path.dirname(file_path))}")
    
    if len(os.path.dirname(file_path)) >= DIR_LENGTH_THRESHOLD:
        logging.info(f"Found long directories path: {file_path}")
        write_to_file(long_file_path_list_file, file_path)


def scan_long_paths_and_long_filename(base_dir, counters):
    """
    Scans a directory for files with long paths or filenames.

    This function recursively scans all files in a directory and its subdirectories. 
    If it finds a file with a path length >= `dir_length_threshold` or a filename length >= to `file_length_threshold`, 
    it logs the file and writes its path to a specified file.

    Parameters:
    base_dir (str): The directory to scan.
    """
    base_dir = os.path.abspath(base_dir)
    print(f"Scanning base directory: {base_dir}")
    
    if base_dir.startswith('\\') is False:
        long_base_dir = "\\\\?\\" + base_dir
        print(f"Modified base directory: {long_base_dir}")
    else:
        long_base_dir = base_dir

    for entry in os.scandir(long_base_dir):
        if entry.is_file():
            file_path = entry.path
                
            logging.info(f"File path: {file_path}")
            logging.info(f"Checking file: {entry.name}")
            logging.info(f"Filename length: {len(entry.name)}")
                
            if len(os.path.basename(file_path)) >= FILE_LENGTH_THRESHOLD:
                if counters['filename_counter'] >= SCAN_ENTRY_THRESHOLD:
                    counters['filename_file_part'] += 1
                    counters['filename_counter'] = 0
                counters['filename_counter'] += 1
                with open(f'{OUTPUT_DIR}/{FILENAME_SCAN_DIR}/{LONG_FILENAME_SCAN_OUTPUT}_{date_str}_part{counters["filename_file_part"]}.txt', 'a') as long_filename_list_file:
                    logging.info(f"Found long filename: {os.path.basename(file_path)}")
                    write_to_file(long_filename_list_file, file_path)

            if len(os.path.dirname(file_path)) >= DIR_LENGTH_THRESHOLD:
                if counters['dir_counter'] >= SCAN_ENTRY_THRESHOLD:
                    counters['dir_file_part'] += 1
                    counters['dir_counter'] = 0
                counters['dir_counter'] += 1
                with open(f'{OUTPUT_DIR}/{DIR_SCAN_DIR}/{LONG_DIR_PATH_SCAN_OUTPUT}_{date_str}_part{counters["dir_file_part"]}.txt', 'a') as long_file_path_list_file:
                    logging.info(f"Found long directories path: {file_path}")
                    write_to_file(long_file_path_list_file, file_path)
                
        elif entry.is_dir():
            scan_long_paths_and_long_filename(entry.path, counters)


def process_scan():
    """
    Process the scan for long paths and long filenames.

    This function checks if long path support is enabled. If it is enabled, it logs a message to disable it.
    If long path support is disabled, it scans for long paths and long filenames using the BASE_DIR as the starting point.
    """
    if check_long_path_support(BASE_DIR) is True:
        logging.info("Long path support is enabled. Please disable it by setting the registry key LongPathsEnabled to 0 to simulate long path errors.")
    else:
        logging.info("Long path support is disabled. Scanning for long paths and long filenames.")
        counters = {'dir_counter': 0, 'filename_counter': 0, 'dir_file_part': 1, 'filename_file_part': 1}
        scan_long_paths_and_long_filename(BASE_DIR, counters)

def process_dir_or_filename(process_type):
    """
    Process directory or filename based on the given process_type.
    """
    config_dir = config.get('DEFAULT', 'config')
    dictionary_path = os.path.join(config_dir, config.get('DEFAULT', 'dictionary_path'))
    
    scan_dir = os.path.join(BASE_DIR, DIR_SCAN_DIR if process_type == 'dir' else FILENAME_SCAN_DIR)
    file_pattern = f"{LONG_DIR_PATH_SCAN_OUTPUT if process_type == 'dir' else LONG_FILENAME_SCAN_OUTPUT}_{date_str}_part*"

    for file_path in glob.glob(os.path.join(scan_dir, file_pattern)):
        with open(file_path, 'r') as f:
            for line in f:
                path = line.strip()
                if process_type == 'dir':
                    print(f"Processing directory: {path}")
                    shorten_long_dir(path, dictionary_path, len(path), dry_run=True)
                else:
                    print(f"Processing file: {path}")
                    shorten_long_filename(path, dictionary_path, len(path), dry_run=True)

def main():
    parser = argparse.ArgumentParser(description='Shorten long file names or directory paths.')
    parser.add_argument('-p', '--process', choices=['dir', 'filename', 'scan'], default='scan', help='Specify whether to process directories, filenames, or perform a scan.')
    args = parser.parse_args()

    initConfigValues()

    print(f"Base directory: {BASE_DIR}")
    print(f"File length threshold: {FILE_LENGTH_THRESHOLD}")
    print(f"Directory length threshold: {DIR_LENGTH_THRESHOLD}")
    
    if args.process == 'scan':
        process_scan()
    else:
        process_dir_or_filename(args.process)


if __name__ == "__main__":
    main()
