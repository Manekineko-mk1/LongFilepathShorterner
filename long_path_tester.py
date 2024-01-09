import os
import hashlib
import shutil

def create_long_filename_file(base_dir, file_length):
    """Test Function - Create a file with a name longer than the specified length."""
    long_filename = "long_filename_test_" + "a" * (file_length - len(base_dir) - 4)  # 4 for '.txt' and buffer
    long_path = os.path.join(base_dir, long_filename + ".txt")
    with open(long_path, 'w') as f:
        f.write("Test file for long filename.")
    return long_path

def create_long_path_file(base_dir, file_length):
    """Test Function - Create a file with a path longer than the specified length."""
    long_dir = "long_sub_dir_test" + "\\a" * (file_length - len(base_dir) - 6)  # 12 for '\a.txt' and buffer
    long_path = os.path.join(base_dir, long_dir, "a.txt")
    os.makedirs(os.path.dirname(long_path), exist_ok=True)
    with open(long_path, 'w') as f:
        f.write("Test file for long path.")
    return long_path

def check_long_path_support(base_dir):
    """Check if the system supports long file paths (> 256 characters)."""
    test_dir = "long_sub_dir_test" + "\\a" * 200  # Create a long directory name
    test_path = os.path.join(base_dir, test_dir, "test.txt")
    try:
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        with open(test_path, 'w') as f:
            f.write("Long path test.")
        os.remove(test_path)
        os.removedirs(os.path.dirname(test_path))
        print("System supports long paths (> 256 characters).")
        return True
    except OSError as e:
        print("System does not support long paths (> 256 characters).")
        return False

def is_path_long(file_path, file_length_threshold):
    """Check if the path length exceeds the threshold."""
    
    # Remove the UNC prefix if present
    normalized_path = file_path.replace("\\\\?\\", "")
    return len(normalized_path) > file_length_threshold

def test_and_fix_long_file_paths(file_path):
    """
    1. Check if the file path contains a long filename, and not just a long path            
    2. If true (i.e., filename length < 256 && file path >= 256), then rename it to a shorter one 
    3. Check if the file path contains a long path, and not just a long filename
    4. If true, shorten file path
    """
    
    # Check if the file path contains a long filename, and not just a long path
    if len(os.path.basename(file_path)) > 255:
        file_path = rename_long_filename(file_path)
    
    # Check if the file path contains a long path, and not just a long filename
    if len(os.path.dirname(file_path)) > 255:
        file_path = shorten_long_path(file_path)
    
def rename_long_filename(file_path):
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


def scan_and_operate_long_paths(base_dir, file_length):
    """Scan for long paths and long filenames in base_dir and perform operations on them.
       Should get "[WinError 3] The system cannot find the path specified:" if used on long file paths or filenames.
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
                file_path = rename_long_filename(file_path)
    
            # Check if the file path contains a long path, and not just a long filename
            if len(os.path.dirname(file_path)) > 255:
                print(f"Found long directories path: {file_path}")
                file_path = shorten_long_path(file_path, 7)
            
def get_file_hash(file_path):
    """Compute the SHA256 hash of a file."""
    
    print(f"Computing hash for file: {file_path}")
    
    # Fix this function to work with long paths
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def main():
    base_dir = "C:\\Users\\jesse.tsang\\Desktop\\LongPathTest"  # Change as per your base directory
    file_length = 260  # Example length, adjust as needed
    
    # Check if long paths are supported -- Run this first
    # if check_long_path_support(base_dir) is True:
    #     # Create a long path file and test operations
    #     long_file_path = create_long_path_file(base_dir, file_length)
    #     long_file_name = create_long_filename_file(base_dir, file_length)
    #     print(f"Created long file path file at: {long_file_path}")
    #     print(f"Created long file name file at: {long_file_name}")
    # else:
    #     print("Long path support is disabled. Set the registry key LongPathsEnabled to 1 to enable it.")

    # Scan base_dir for long paths and operate on them -- Run this after creating long paths and long files
    if check_long_path_support(base_dir) is True:
        print("Long path support is enabled. Please disable it by set the registry key LongPathsEnabled to 0 to simulate long path errors.")
    else:
        print("Long path support is disabled. Scanning for long paths and long filenames.")
        scan_and_operate_long_paths(base_dir, file_length)

if __name__ == "__main__":
    main()

