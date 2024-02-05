import hashlib
import logging
import os
import csv

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

def check_long_path_support(base_dir):
    """Check if the system supports long file paths (> 256 characters)."""
    test_dir = "long_sub_dir_test" + "\\a" * 260  # Create a long directory name
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

def write_to_csv(file_path, row):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def write_to_file(file, content):
    try:
        file.write(f"{content}\n")
    except IOError as e:
        logging.error(f"Error writing to file: {e}")

txt_file = "test_filepaths.txt"
# read_filepaths_from_txt(txt_file)
