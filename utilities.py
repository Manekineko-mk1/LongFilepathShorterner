import os

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

def print_filepath_and_filename_length(file_path):
    """Print the file path and filename length."""
    print(f"File path: {file_path} length: {len(file_path)}")
    print(f"Filename: {os.path.basename(file_path)} length: {len(os.path.basename(file_path))}")

file_path = "C:\\Users\\user\\Documents\\GitHub\\python-snippets\\long_filepath_filename_shortener\\long_sub_dir\\test.txt"
print_filepath_and_filename_length(file_path)
