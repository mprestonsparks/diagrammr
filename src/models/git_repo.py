# src/models/git_repo.py
import git
import json
import shutil
import os
import logging

# Use a module-level logger
logger = logging.getLogger(__name__)

class GitRepo:
    def __init__(self, config):
        # Log the received config to ensure it's being passed correctly
        logger.debug(f"Initializing GitRepo with config: {config}")

        self.config = config
        self.repo_url = config['gitRepoUrl']
        self.local_dir = config['local_dir']

    def clone_or_pull(self):
        # Log the attempt to access the local_dir from config
        logger.debug("Attempting to clone or pull the repository.")

        try:
            local_dir = self.config['local_dir']  # Retrieve local_dir from config when needed
            logger.debug(f"Local directory for git operations: {local_dir}")
        except AttributeError as e:
            logger.error(f"AttributeError: {e}")
            raise

        if os.path.exists(local_dir) and os.path.isdir(local_dir):
            try:
                repo = git.Repo(local_dir)
                origin = repo.remotes.origin
                origin.pull()
                logger.debug("Successfully pulled the repository.")
            except git.InvalidGitRepositoryError as e:
                logger.error(f"InvalidGitRepositoryError: {e}")
                shutil.rmtree(local_dir)
                repo = git.Repo.clone_from(self.repo_url, local_dir)
                logger.debug("Successfully cloned the repository.")
        else:
            repo = git.Repo.clone_from(self.repo_url, local_dir)
            logger.debug("Successfully cloned the repository.")

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
