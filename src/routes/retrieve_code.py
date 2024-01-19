import git
import json
import os

def clone_repo(repo_url, temp_dir, access_token):
    try:
        # Modify the URL to include the access token
        if access_token:
            repo_url = repo_url.replace('https://', f'https://{access_token}@')
        repo = git.Repo.clone_from(repo_url, temp_dir)
        return repo
    except Exception as e:
        raise ValueError(f"Failed to clone repository: {str(e)}")

def retrieve_code(repo, branch_name):
    try:
        print(f"Attempting to checkout branch: {branch_name}")  # Diagnostic print statement
        repo.git.fetch()  # Fetch the latest updates from the remote
        repo.git.checkout(branch_name)
        
        # Load the config
        config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        ignore_list = config.get('ignore', [])
        include_list = config.get('include', [])

        # Create a new dictionary to store file paths and their corresponding code
        files_to_include = {}
        for file in repo.tree():
            if any(file.path.endswith(ext) for ext in include_list) and not any(ignored_file in file.path for ignored_file in ignore_list):
                try:
                    with open(file.abspath, 'r') as f:
                        files_to_include[file.path] = f.read()
                except FileNotFoundError:
                    print(f"Ignoring missing file: {file.path}")  # Diagnostic print statement

        return files_to_include
    except Exception as e:
        raise ValueError(f"Failed to retrieve code: {str(e)}")