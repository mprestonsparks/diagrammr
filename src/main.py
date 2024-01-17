from git import Repo
import os

def clone_repository(repo_url, local_dir):
    Repo.clone_from(repo_url, local_dir)

def explore_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):  # Assuming Python files
                yield os.path.join(root, file)

# Example Usage
repo_url = 'your_repo_url'
local_dir = 'path_to_local_directory'
clone_repository(repo_url, local_dir)
files = list(explore_files_in_directory(local_dir))

# Path: src/file_reader.py
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Example Usage for the first file
file_content = read_file_content(files[0])


