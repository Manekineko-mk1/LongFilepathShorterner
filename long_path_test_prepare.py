import os
from utilities import check_long_path_support

def create_long_filename_file(base_dir, file_length):
    """Test Function - Create a file with a name longer than the specified length."""
    long_filename = "long_filename_test_" + "a" * (file_length - len(base_dir) - 4)  # 4 for '.txt' and buffer
    long_path = os.path.join(base_dir, long_filename + ".txt")
    with open(long_path, 'w') as f:
        f.write("Test file for long filename.")
    return long_path


def create_long_path_file(base_dir, file_length):
    """Test Function - Create a file with a path longer than the specified length."""
    long_dir = "long_sub_dir_test" + "\\a" * (file_length - len(base_dir) - 6)  # 6 for '\a.txt' and buffer
    long_path = os.path.join(base_dir, long_dir, "a.txt")
    os.makedirs(os.path.dirname(long_path), exist_ok=True)
    with open(long_path, 'w') as f:
        f.write("Test file for long path.")
    
    long_base_dir = "\\\\?\\" + base_dir
    
    # Create a test file at each subdirectory
    subdirectories = long_dir.split("\\")
    for i in range(1, len(subdirectories)):
        subdirectory_path = os.path.join(long_base_dir, "\\".join(subdirectories[:i]))
        test_file_path = os.path.join(subdirectory_path, f"test_file_level_{i}.txt")
        with open(test_file_path, 'w') as f:
            f.write(f"Test file at subdirectory level {i}.")

    return long_path


def main():
    base_dir = "C:\\Users\\jesse\\Desktop\\LongPathTest"  # Change as per your base directory
    file_length = 260  # Example length, adjust as needed
    
    # Check if long paths are supported -- Run this first
    if check_long_path_support(base_dir) is True:
        # Create a long path file and test operations
        long_file_path = create_long_path_file(base_dir, file_length)
        long_file_name = create_long_filename_file(base_dir, file_length)
        print(f"Created long file path file at: {long_file_path}")
        print(f"Created long file name file at: {long_file_name}")
    else:
        print("Long path support is disabled. Set the registry key LongPathsEnabled to 1 to enable it.")

if __name__ == "__main__":
    main()

