# import json
# from git import Repo
# import os
# import logging
# import subprocess

# # Specify the logs directory
# logs_dir = 'logs'

# # Check if the logs directory exists
# if not os.path.exists(logs_dir):
#     # If not, create the directory
#     os.makedirs(logs_dir)
# # Configure logging
# logging.basicConfig(filename=os.path.join(logs_dir, 'main.log'), level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Read config.json for repo_url and local_dir
# with open('src/scripts/config.json') as config_file:
#     config = json.load(config_file)

# repo_url = config['gitRepoUrl']
# local_dir = config['local_dir']  # Changed from 'outputDirectory' to 'local_dir'
# print(f'Local directory: {local_dir}')

# # Clear out the local_dir before cloning
# if os.path.exists(local_dir):
#     for root, dirs, files in os.walk(local_dir, topdown=False):
#         for name in files:
#             os.remove(os.path.join(root, name))
#         for name in dirs:
#             os.rmdir(os.path.join(root, name))

# def clone_repository(repo_url, local_dir):
#     Repo.clone_from(repo_url, local_dir)

# def explore_files_in_directory(directory):
#     python_files = []
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.endswith('.py'):  # Assuming Python files
#                 python_files.append(os.path.join(root, file))
#     return python_files

# # Check if the directory exists
# if not os.path.exists(local_dir):
#     # If not, create the directory
#     os.makedirs(local_dir)

# # Clone the repository and explore files
# def clone_repository(repo_url, local_dir):
#     if os.path.exists(local_dir) and os.listdir(local_dir):
#         raise Exception(f"Directory {local_dir} already exists and is not empty")
#     else:
#         Repo.clone_from(repo_url, local_dir)

# def read_file_content(file_path):
#     with open(file_path, 'r') as file:
#         return file.read()

# # Run execute_generate_uml.py
# try:
#     result = subprocess.run(["python3", "src/scripts/execute_generate_uml.py"], check=True)
#     if result.returncode == 0:
#         # Now that execute_generate_uml.py has run, the Python files should exist
#         files = explore_files_in_directory(local_dir)
#         print(f'Files: {files}')
#         file_content = read_file_content(files[0])
# except subprocess.CalledProcessError as e:
#     logging.error(f'Error occurred while running execute_generate_uml.py: {str(e)}')