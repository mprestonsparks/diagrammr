# src/models/git_repo.py
import git
import json
import shutil
import os

class GitRepo:
    def __init__(self, config):
        self.repo_url = config['gitRepoUrl']
        self.config = config

    def clone_or_pull(self):
        local_dir = self.config['local_dir']  # Retrieve local_dir from config when needed
        if os.path.exists(local_dir) and os.path.isdir(local_dir):
            try:
                repo = git.Repo(local_dir)
                origin = repo.remotes.origin
                origin.pull()
            except git.InvalidGitRepositoryError:
                shutil.rmtree(local_dir)
                git.Repo.clone_from(self.repo_url, local_dir)
        else:
            git.Repo.clone_from(self.repo_url, local_dir)

    def retrieve_code(self, file_path):
        local_dir = self.config['local_dir']  # Retrieve local_dir from config when needed
        try:
            full_file_path = os.path.join(local_dir, file_path)
            with open(full_file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise Exception(f"The file {file_path} was not found in the repository.")
        except Exception as e:
            raise Exception(f"An error occurred while retrieving the code: {e}")
