# src/models/git_repo.py
import git
import json
import shutil
import os

class GitRepo:
    def __init__(self, config_file):
        with open(config_file) as json_file:
            data = json.load(json_file)
        self.repo_url = data['gitRepoUrl']
        self.local_dir = data['local_dir']

    def clone(self):
        # Delete the directory if it exists and is not empty
        if os.path.exists(self.local_dir) and os.listdir(self.local_dir):
            shutil.rmtree(self.local_dir)
        # Clone the repository and return the local path
        # This is a simple example and doesn't handle errors
        git.Repo.clone_from(self.repo_url, self.local_dir)

    def retrieve_code(self, file_path):
        # Retrieve the code from a file in the repository
        # This is a simple example and doesn't handle errors
        with open(f'{self.local_dir}/{file_path}') as file:
            return file.read()