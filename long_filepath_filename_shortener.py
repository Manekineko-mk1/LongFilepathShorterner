import os
import hashlib
import shutil

from utilities import check_long_path_support

# TODO: Add logging throughout the script
# TODO: Add a feature that will output a list of files that were not renamed due to errors, output type: csv
# TODO: Add a feature that will output a list of files and file path that were shortened, output type: csv

def shorten_long_filename(file_path):
    """Rename the file to a shorter name."""
    
    try:
        # Rename the file to a shorter name
        new_file_path = os.path.join(os.path.dirname(file_path), "short_filename.txt")
        print(f"Trying to shortened filename to: {new_file_path}")
        os.rename(file_path, new_file_path)
        print(f"Renamed file to: {new_file_path}")
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error renaming file: {e}")
        return file_path  # Return the original file path if renaming failed
    
    return new_file_path

def shorten_long_path(file_path, num_directories_to_keep):
    """Shorten the file path to keep only a certain number of directory levels."""

    try:
        # Split the path into its components
        path_components = file_path.split(os.sep)
        
        # Keep only the desired number of directory levels, starting from the 3rd element
        new_path_components = path_components[3:3 + num_directories_to_keep]
        
        # Append the original file to the new path components
        new_path_components.append(path_components[-1])  # -1 to get the last element, which is the file
        
        # Join the components back together to form the new path
        new_file_path = os.sep.join(new_path_components)
        print(f"Trying to shortened file path to: {new_file_path}")
        
        # Rename the file
        # os.rename(file_path, new_file_path) # this will move the file to the new path
        shutil.copy2(file_path, new_file_path)  # this will copy the file to the new path
        print(f"Renamed file path to: {new_file_path}")
        
        # Check the hash value and file attributes of the original and copied files
        print(f"Checking file hash and attributes for {file_path} and {new_file_path}")
        original_file_hash = get_file_hash(file_path)
        copied_file_hash = get_file_hash(new_file_path)
        
        print(f"Original file hash: {original_file_hash}")
        print(f"Copied file hash: {copied_file_hash}")
        
        print(f"Checking file attributes for {file_path} and {new_file_path}")
        original_file_attributes = os.stat(file_path)
        copied_file_attributes = os.stat(new_file_path)
        
        print(f"Original file attributes: {original_file_attributes}")
        print(f"Copied file attributes: {copied_file_attributes}")
        
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error renaming file: {e}")
        return file_path  # Return the original file path if renaming failed
    
    return new_file_path

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
            
            print(f"File path: {file_path}")
            print(f"Checking file: {name}")
            print(f"Filename length: {len(name)}")
            
            # Check if the file path contains a long filename, and not just a long path
            if len(os.path.basename(file_path)) > 200:
                print(f"Found long file name: {name}")
                file_path = shorten_long_filename(file_path)
    
            # Check if the file path contains a long path, and not just a long filename
            if len(os.path.dirname(file_path)) > 255:
                print(f"Found long directories path: {file_path}")
                file_path = shorten_long_path(file_path, 7)
            
def get_file_hash(file_path):
    """Compute the SHA256 hash of a file."""
    
    print(f"Computing hash for file: {file_path}")

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
        print("Long path support is enabled. Please disable it by set the registry key LongPathsEnabled to 0 to simulate long path errors.")
    else:
        print("Long path support is disabled. Scanning for long paths and long filenames.")
        scan_long_paths_and_long_filename(base_dir, file_length)

if __name__ == "__main__":
    main()

