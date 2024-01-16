import os
import hashlib
import shutil
import logging
import csv

from utilities import check_long_path_support

# Configure logging
logging.basicConfig(filename='logs/shortener.log', level=logging.DEBUG)

# TODO: Add a feature that will output a list of files that were not renamed due to errors, output type: csv

def shorten_long_filename(file_path):
    """Rename the file to a shorter name."""
    
    try:
        # Rename the file to a shorter name
        new_file_path = os.path.join(os.path.dirname(file_path), "short_filename.txt")
        logging.info(f"Trying to shorten filename to: {new_file_path}")
        os.rename(file_path, new_file_path)
        logging.info(f"Renamed file to: {new_file_path}")
        
        # Record the modified file path in a CSV file
        with open('output/modified_paths.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_path])
        
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")
        return file_path  # Return the original file path if renaming failed
    
    return new_file_path

# TODO: Check if it is possible to do in-place renaming of the file path
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
def shorten_long_path(file_path, num_directories_to_keep):
    """Shorten the file path to keep only a certain number of directory levels."""

    try:
        new_file_path = create_new_path(file_path, num_directories_to_keep)
        logging.info(f"Trying to shorten file path to: {new_file_path}")
        
        copy_file_to_new_path(file_path, new_file_path)
        logging.info(f"Renamed file path to: {new_file_path}")
        
        check_file_hash_and_attributes(file_path, new_file_path)
        
        # Record the modified file path in a CSV file
        with open('output/modified_paths.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, new_file_path])
        
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error renaming file: {e}")
        return file_path  # Return the original file path if renaming failed
    
    return new_file_path

def create_new_path(file_path, num_directories_to_keep):
    """Create a new path with a limited number of directory levels."""
    path_components = file_path.split(os.sep)
    new_path_components = path_components[3:3 + num_directories_to_keep]
    new_path_components.append(path_components[-1])  # -1 to get the last element, which is the file
    new_file_path = os.sep.join(new_path_components)
    
    logging.info(f"Created new file path: {new_file_path}")
    
    return new_file_path

def copy_file_to_new_path(file_path, new_file_path):
    """Copy the file to the new path."""
    logging.info(f"Copying file from {file_path} to {new_file_path}")
    # os.rename(file_path, new_file_path) # this will move the file to the new path
    shutil.copy2(file_path, new_file_path)
    logging.info(f"File copied to {new_file_path}")

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

def scan_long_paths_and_long_filename(base_dir, file_length):
    """
    1. Check if the file path contains a long filename, and not just a long path            
    2. If true (i.e., filename length < 256 && file path >= 256), then rename it to a shorter one 
    3. Check if the file path contains a long path, and not just a long filename
    4. If true, shorten file path
    """
    
    # Ensure base_dir is an absolute path
    base_dir = os.path.abspath(base_dir)
    long_base_dir = "\\\\?\\" + base_dir  # This is UNC to allow long paths in Windows
    
    # Scan for long paths and long filenames
    for root, dirs, files in os.walk(long_base_dir):
        for name in files:
            # Construct the full file path
            file_path = os.path.join(root, name)
            
            logging.info(f"File path: {file_path}")
            logging.info(f"Checking file: {name}")
            logging.info(f"Filename length: {len(name)}")
            
            # Check if the file path contains a long filename, and not just a long path
            if len(os.path.basename(file_path)) > 200:
                logging.info(f"Found long file name: {name}")
                file_path = shorten_long_filename(file_path)
    
            # Check if the file path contains a long path, and not just a long filename
            if len(os.path.dirname(file_path)) > 255:
                logging.info(f"Found long directories path: {file_path}")
                file_path = shorten_long_path(file_path, 7)
            
def get_file_hash(file_path):
    """Compute the SHA256 hash of a file."""
    
    logging.info(f"Computing hash for file: {file_path}")

    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def main():
    base_dir = "C:\\Users\\jesse\\Desktop\\LongPathTest"  # Change as per your base directory
    file_length = 260  # Example length, adjust as needed
    
    # Scan base_dir for long paths and operate on them -- Run this after creating long paths and long files
    if check_long_path_support(base_dir) is True:
        logging.info("Long path support is enabled. Please disable it by set the registry key LongPathsEnabled to 0 to simulate long path errors.")
    else:
        logging.info("Long path support is disabled. Scanning for long paths and long filenames.")
        scan_long_paths_and_long_filename(base_dir, file_length)

if __name__ == "__main__":
    main()
