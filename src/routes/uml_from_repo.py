# uml_from_repo.py
import os
import fnmatch
import subprocess
import json
import git
import tempfile
import shutil
import logging
from logging import handlers  
from services.retrieve_code import clone_repo, retrieve_code
from utils.code_to_uml import generate_content
from services.etl_workflow import ETLWorkflow
from services.openai_api import OpenAIAPI

 
# Configure logging to write to a file
log_directory = 'logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'uml_from_repo.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def process_request(git_repo, github_access_token):
    output_directory = git_repo.local_dir  # Get the output directory from the GitRepo object
    repo_url = git_repo.repo_url  # 'master' is the default branch name
    temp_dir = None  # Initialize temp_dir outside the try block

    try:
        if not repo_url or not output_directory or not github_access_token:
            logger.error("Missing required parameters")
            return {"error": "Missing required parameters"}, 400

        try:
            temp_dir = tempfile.mkdtemp()
        except Exception as e:
            logger.error(f"Error during UML generation: {str(e)}", exc_info=True)
            return {"error": str(e)}, 500

        # Clone the repository if the directory does not exist
        if not os.path.exists(output_directory):
            logger.debug(f"Attempting to clone the repository from {repo_url} into {output_directory}.")
            repo = git.Repo.clone_from(repo_url, output_directory)
            logger.info(f"Repository cloned into {output_directory}")
        else:
            logger.debug(f"Output directory {output_directory} already exists. Attempting to create a repo instance.")
            repo = git.Repo(output_directory)
            logger.info(f"Repository instance created for {output_directory}")

        # Add detailed logging to check the repo instance
        logger.debug(f"Repo instance details: {repo.__dict__}")

        # Verify that the repository has been cloned and files exist
        if os.path.isdir(output_directory) and os.listdir(output_directory):
            logger.info(f"Repository files are present in {output_directory}")
        else:
            logger.error(f"No files found in {output_directory}. Cloning might have failed or the repository might be empty.")

        # Load the configurations from both files
        with open('src/routes/config.json', 'r') as config_file:
            config = json.load(config_file)
        with open('src/scripts/git_repo_config.json', 'r') as git_repo_config_file:
            git_repo_config = json.load(git_repo_config_file)

        # Merge the configurations
        combined_config = {**config, **git_repo_config}

        # Initialize OpenAIAPI and ETLWorkflow with the combined_config
        openai_api = OpenAIAPI()  # Ensure OpenAIAPI is properly initialized
        etl_workflow = ETLWorkflow(openai_api, combined_config)  # Pass the combined_config directly

        # Retrieve the code from the repository and generate UML diagrams
        included_files = {}
        for item in repo.tree().traverse():
            logger.debug(f"Traversing item: {item.path}")
            if item.type == 'blob':  # This means it's a file, not a directory
                for pattern in combined_config['include']:
                    if fnmatch.fnmatch(item.path, pattern):
                        file_path = os.path.join(output_directory, item.path)
                        title = os.path.basename(item.path)  # Use the base name of the file as the title
                        logger.debug(f"Matched file: {file_path} with pattern: {pattern}")
                        # Execute the ETL workflow for each file
                        puml_code = etl_workflow.execute(file_path, title)
                        if puml_code:
                            included_files[file_path] = puml_code
                            logger.debug(f"UML code generated for {file_path}: {puml_code}")
                        else:
                            logger.debug(f"No UML code generated for {file_path}.")
                        break  # No need to check the remaining patterns
                    else:
                        logger.debug(f"File {item.path} does not match pattern {pattern}.")
            else:
                logger.debug(f"Skipping directory: {item.path}")

        logger.debug(f"Type of included_files: {type(included_files)}")
        logger.debug(f"Value of included_files: {included_files}")

        # Save the UML diagram to a file
        logger.info(f"Saving UML diagram to {output_directory}")
        final_output_paths = generate_content(included_files, output_directory)  # This is now a list of file paths
        logger.info(f"Final output paths: {final_output_paths}")

        for path in final_output_paths:
            try:
                with open(path, 'w') as file:
                    file.write(included_files[os.path.splitext(path)[0]])
                logger.info(f"UML diagram successfully written to {path}")
            except Exception as e:
                logger.error(f"Failed to write UML diagram to {path}: {e}", exc_info=True)

        return {
            "message": "UML diagrams generated successfully",
            "details": {
                "Repository": repo_url,
                "Output Paths": final_output_paths  # This is now a list of file paths
            }
        }, 200

    except Exception as e:
        logger.error(f"Unhandled exception in process_request: {e}", exc_info=True)
        return {"error": str(e)}, 500

    finally:
        # Clean up the temporary directory
        if temp_dir is not None:
            try:
                logger.info("Cleaning up temporary directory")
                shutil.rmtree(temp_dir)
                logger.info(f"Temporary directory {temp_dir} cleaned up successfully.")
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory {temp_dir}: {e}", exc_info=True)
