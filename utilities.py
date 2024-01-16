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
    file_path_length = len(file_path)
    filename_length = len(os.path.basename(file_path))
    file_path_without_filename_length = file_path_length - filename_length
    
    if file_path_length >= 230:
        print(f"File path: {file_path} length: {file_path_length}")
    
    if filename_length >= 50:
        print(f"Long Filename Detected: {os.path.basename(file_path)} length: {filename_length}")
    
    if file_path_length >= 200 and filename_length >= file_path_without_filename_length:
        print(f"Filename >= Directories Path: {os.path.basename(file_path)} length: {filename_length} | Directories Path length: {file_path_without_filename_length}")

def read_filepaths_from_txt(txt_file):
    """Read file paths from a text file."""
    if not os.path.exists(txt_file):
        print(f"Error: {txt_file} does not exist.")
        return

    with open(txt_file, 'r') as f:
        for line in f:
            file_path = line.strip()
            print_filepath_and_filename_length(file_path)

txt_file = "test_filepaths.txt"
# read_filepaths_from_txt(txt_file)
