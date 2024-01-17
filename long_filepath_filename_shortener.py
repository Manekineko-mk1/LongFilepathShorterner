import datetime
import os
import logging
import csv
import configparser
import re

from utilities import check_long_path_support, get_file_hash, write_to_file

date_str = datetime.now().strftime('%Y%m%d')

# Load the configuration from the .ini file
config = configparser.ConfigParser()
config.read('config.ini')
log_dir = config.get('DEFAULT', 'log_dir')
output_dir = config.get('DEFAULT', 'output_dir')

# Configure logging
logging.basicConfig(filename=f'{log_dir}/shortener_log_{date_str}.log', level=logging.DEBUG)

# TODO: Add files that failed to modify to a CSV file
def shorten_long_filename(file_path, dictionary_path, file_length):
    """Rename the file to a shorter name."""
    
    long_filename_modified_output = config.get('DEFAULT', 'long_filename_modified_output')
    long_filename_modified_error = config.get('DEFAULT', 'long_filename_modified_error')
    dictionary_path = config.get('DEFAULT', 'dictionary_path')
    
    try:
        # Rename the file to a shorter name
        new_file_name = os.path.join(os.path.dirname(file_path), "short_filename.txt")
        logging.info(f"Trying to shorten filename to: {new_file_name}")
        os.rename(file_path, new_file_name)
        logging.info(f"Renamed file to: {new_file_name}")
        
        # Record the modified file path in a CSV file
        with open(f'{output_dir}/{long_filename_modified_output}_{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_name])
        
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")

def shorten_long_filename_wip(file_path, dictionary_path, file_length):
    """Rename the file to a shorter name."""
    
    long_filename_modified_output = config.get('DEFAULT', 'long_filename_modified_output')
    long_filename_modified_error = config.get('DEFAULT', 'long_filename_modified_error')
    
    # Check if the dictionary file exists
    if not os.path.isfile(dictionary_path):
        logging.error(f"Dictionary file does not exist: {dictionary_path}")
        return
    
    # Load the dictionary file into a Python dictionary
    with open(dictionary_path, 'r') as f:
        reader = csv.reader(f)
        dictionary = {rows[0]:rows[1] for rows in reader}
    
    # Analyze the filename format
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    # Break down the filename into components based on the format
    if '_' in name or '-' in name:
        components = re.split('_|-', name)
    elif re.findall('[A-Z][^A-Z]*', name):
        components = re.findall('[A-Z][^A-Z]*', name)
    else:
        components = [name]
    
    # Convert the components using the dictionary
    new_components = [dictionary.get(component, component) for component in components]
    new_name = '-'.join(new_components) + ext
    
    # Check for file name conflict
    for i in range(10):
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        if not os.path.exists(new_file_path):
            break
        new_name = f"{new_name.rsplit('_', 1)[0]}_{i+1}{ext}"
    else:
        logging.error(f"Failed to rename file after 10 attempts: {file_path}")
        return
    
    # Rename the file
    try:
        os.rename(file_path, new_file_path)
        logging.info(f"Renamed file to: {new_file_path}")
        
        # Record the modified file path in a CSV file
        with open(f'{output_dir}/{long_filename_modified_output}_{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_path])
        
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")
        with open(f'{output_dir}/{long_filename_modified_error}_{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, str(e)])


# TODO: Check how to show the progress of the process: progress bar, percentage, etc.
# Things to consider:
# 1. How to handle files that are in use. Possible solution: Use a try-except block to catch the error and skip the file
# 2. How to handle files that are locked, for example, by anti-virus software. Possible solution: Use a try-except block to catch the error and skip the file
# 3. We should check if we can do in-place renaming, if yes, should we start from the end of the path or from the beginning of the path? 
# 3.1 If in-place renaming is possible, we should start from the end of the path, because:
#       3.1.1 the beginning of the path is more likely to be more meaningful
#       3.1.2 we maybe able to rename just a few directories to shorten the path, this will keep the path as original as possible
#       3.1.3 for large files in the range of a few hundred GBs, renaming will definitely preferable to copying.
# 5. How to handle if a file name collision occurs? Possible solution: Use a try-except block to catch the error and have a helper function to handle the collision.
def shorten_long_dir(dir_path, dictionary_path, dir_length):
    """Shorten the file path to keep only a certain number of directory levels."""
    
    # Load the configuration from the .ini file
    long_dir_path_scan_output = config.get('DEFAULT', 'long_dir_path_scan_output')

    try:
        new_dir_path = ''
        # logging.info(f"Trying to shorten file path to: {new_file_path}")
        # logging.info(f"Renamed file path to: {new_file_path}")
        
        # Record the modified file path in a CSV file
        with open(f'{output_dir}/{long_dir_path_scan_output}__{date_str}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([dir_path, new_dir_path])
        
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")


def check_file_hash_and_attributes(file_path, new_file_path):
    """Check the hash value and file attributes of the original and copied files."""
    logging.info(f"Checking file hash and attributes for {file_path} and {new_file_path}")
    original_file_hash = get_file_hash(file_path)
    copied_file_hash = get_file_hash(new_file_path)
    
    logging.info(f"Original file hash: {original_file_hash}")
    logging.info(f"Copied file hash: {copied_file_hash}")
    
    logging.info(f"Checking file attributes for {file_path} and {new_file_path}")
    original_file_attributes = os.stat(file_path)
    copied_file_attributes = os.stat(new_file_path)
    
    logging.info(f"Original file attributes: {original_file_attributes}")
    logging.info(f"Copied file attributes: {copied_file_attributes}")

def handle_long_filename(file_path, filename_length, filename, long_filename_list_file):
    if len(os.path.basename(file_path)) >= filename_length:
        logging.info(f"Found long filename: {filename}")
        write_to_file(long_filename_list_file, file_path)

def handle_long_filepath(file_path, dir_length, long_file_path_list_file):
    if len(os.path.dirname(file_path)) >= dir_length:
        logging.info(f"Found long directories path: {file_path}")
        write_to_file(long_file_path_list_file, file_path)

def scan_long_paths_and_long_filename(base_dir, filename_length, dir_length):
    base_dir = os.path.abspath(base_dir)
    long_base_dir = "\\\\?\\" + base_dir
    
    # Load the configuration from the .ini file
    long_dir_path_scan_output = config.get('DEFAULT', 'long_dir_path_scan_output')
    long_filename_scan_output = config.get('DEFAULT', 'long_filename_scan_output')
    
    date_str = datetime.now().strftime('%Y%m%d')
    with open(f'{output_dir}/{long_dir_path_scan_output}_{date_str}.txt', 'w') as long_file_path_list_file, \
         open(f'{output_dir}/{long_filename_scan_output}_{date_str}.txt', 'w') as long_filename_list_file:
        
        for entry in os.scandir(long_base_dir):
            if entry.is_file():
                file_path = entry.path
                
                logging.info(f"File path: {file_path}")
                logging.info(f"Checking file: {entry.name}")
                logging.info(f"Filename length: {len(entry.name)}")
                
                file_path = handle_long_filename(file_path, filename_length, entry.name, long_filename_list_file)
                file_path = handle_long_filepath(file_path, dir_length, long_file_path_list_file)
                
            elif entry.is_dir():
                scan_long_paths_and_long_filename(entry.path, filename_length, dir_length)


def main():
    # Load the configuration from the .ini file
    base_dir = config.get('DEFAULT', 'base_dir')
    file_length = config.getint('DEFAULT', 'file_length')
    dir_length = config.getint('DEFAULT', 'dir_length')
    
    print(f"Base directory: {base_dir}")
    print(f"File length: {file_length}")
    print(f"Directory length: {dir_length}")
    
    # Scan base_dir for long paths and operate on them -- Run this after creating long paths and long files
    if check_long_path_support(base_dir) is True:
        logging.info("Long path support is enabled. Please disable it by set the registry key LongPathsEnabled to 0 to simulate long path errors.")
    else:
        logging.info("Long path support is disabled. Scanning for long paths and long filenames.")
        scan_long_paths_and_long_filename(base_dir, file_length)

if __name__ == "__main__":
    main()
