# LongFilepathShorterner
This script will discover filename or filepath that are longer than 256 character in length, then use various method to shortern it.

## Test Usage
1. Install Python 3.6.4
2. Clone the repo
3. Ensure the LongPathsEnabled is set to 1 in Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\
4. Run long_path_test_prepare.py
5. Set LongPathsEnabled is set to 0 to simulate target system registry (long file path NOT allowed)
6. To scan, in Command Prompt, type "python long_filepath_filename_shortener.py -p scan"
7. To shorten folders, in Command Prompt, type "python long_filepath_filename_shortener.py -p dir
8. To shorten filenames, in Command Prompt, type "python long_filepath_filename_shortener.py -p filename"
