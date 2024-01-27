import git
import json
import os
import logging
from logging import handlers


# Configure logging to write to a file
log_directory = 'logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'retrieve_code.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


def clone_repo(repo_url, temp_dir, access_token):
    try:
        # Modify the URL to include the access token
        if access_token:
            repo_url = repo_url.replace('https://', f'https://{access_token}@')
        logger.info(f"Cloning repository: {repo_url}")
        repo = git.Repo.clone_from(repo_url, temp_dir)
        logger.info(f"Successfully cloned repository: {repo_url}")
        return repo
    except Exception as e:
        logger.error(f"Failed to clone repository: {str(e)}")
        raise ValueError(f"Failed to clone repository: {str(e)}")

def retrieve_code(git_repo, branch_name):
    try:
        print(f"Attempting to checkout branch: {branch_name}")  # Diagnostic print statement
        logger.info(f"Attempting to checkout branch: {branch_name}")
        git_repo.clone_or_pull()  # Use the GitRepo method to ensure the repo is up to date
        logger.info(f"Successfully checked out branch: {branch_name}")
        
        # Load the config
        config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        ignore_list = config.get('ignore', [])
        include_list = config.get('include', [])

        # Create a new dictionary to store file paths and their corresponding code
        included_files = {}
        for file in git_repo.tree():
            if any(file.path.endswith(ext) for ext in include_list) and not any(ignored_file in file.path for ignored_file in ignore_list):
                try:
                    with open(file.abspath, 'r') as f:
                        included_files[file.path] = f.read()
                    logger.info(f"Included file: {file.path}")
                except FileNotFoundError:
                    print(f"Ignoring missing file: {file.path}")  # Diagnostic print statement
                    logger.warning(f"Ignoring missing file: {file.path}")

        return included_files
    except Exception as e:
        logger.error(f"Failed to retrieve code: {str(e)}")
        raise ValueError(f"Failed to retrieve code: {str(e)}")