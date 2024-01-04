import os

def create_long_filename_file(base_dir, file_length):
    """Create a file with a name longer than the specified length."""
    long_filename = "long_filename_test_" + "a" * (file_length - len(base_dir) - 4)  # 4 for '.txt' and buffer
    long_path = os.path.join(base_dir, long_filename + ".txt")
    with open(long_path, 'w') as f:
        f.write("Test file for long filename.")
    return long_path

def create_long_path_file(base_dir, file_length):
    """Create a file with a path longer than the specified length."""
    long_dir = "long_sub_dir_test" + "\\a" * (file_length - len(base_dir) - 6)  # 6 for '\a.txt' and buffer
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

def is_path_long(path, threshold):
    """Check if the path length exceeds the threshold."""
    return len(path) > threshold

def test_file_operations(file_path):
    """Perform rename, move, and delete operations on the file. 
    Should encounter [WinError 3] The system cannot find the path specified error if LongPathsEnabled is set to 0."""
    try:
        # Rename
        new_path = file_path.replace(".txt", "_renamed.txt")
        os.rename(file_path, new_path)
        print(f"Renamed: {new_path}")

        # Move (just changing the file name for simplicity)
        move_path = new_path.replace("_renamed.txt", "_moved.txt")
        os.rename(new_path, move_path)
        print(f"Moved to: {move_path}")

        # Delete
        os.remove(file_path)
        print(f"Deleted: {file_path}")

    except Exception as e:
        print(f"Error during operations on {file_path}: {e}")

def scan_and_operate_long_paths(base_dir, file_length):
    """Scan for long paths in base_dir and perform operations on them."""
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if is_path_long(file_path, file_length):
                print(f"Found long path: {file_path}")
                test_file_operations(file_path)

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

    #     # Test operations on the file
    #     # test_file_operations(long_file_path)
    # else:
    #     print("Long path support is disabled.")

    # Scan base_dir for long paths and operate on them -- Run this after creating long paths and long files
    scan_and_operate_long_paths(base_dir, file_length)

if __name__ == "__main__":
    main()

