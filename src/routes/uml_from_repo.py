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

        # Check if the directory exists and remove it
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)

        # Clone the repository
        repo = git.Repo.clone_from(repo_url, output_directory)

        # Load the config
        with open('src/routes/config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize OpenAIAPI and ETLWorkflow
        openai_api = OpenAIAPI()  # Ensure OpenAIAPI is properly initialized
        etl_workflow = ETLWorkflow(openai_api, 'src/routes/config.json')  # Pass the path to the config file

        # Retrieve the code from the repository and generate UML diagrams
        included_files = {}
        for item in repo.tree().traverse():
            if item.type == 'blob':  # This means it's a file, not a directory
                for pattern in config['include']:
                    if fnmatch.fnmatch(item.path, pattern):
                        file_path = os.path.join(output_directory, item.path)
                        title = os.path.basename(item.path)  # Use the base name of the file as the title
                        # Execute the ETL workflow for each file
                        etl_workflow.execute(file_path, title)
                        break  # No need to check the remaining patterns

        logger.debug(f"Type of included_files: {type(included_files)}")
        logger.debug(f"Value of included_files: {included_files}")

        # Save the UML diagram to a file
        logger.info(f"Saving UML diagram to {output_directory}")
        final_output_paths = generate_content(included_files, output_directory)  # This is now a list of file paths
        logger.info(f"Final output paths: {final_output_paths}")

        for path in final_output_paths:
            logger.info(f"UML diagram saved at: {path}")  # Log the path where each UML diagram was saved

        return {
            "message": "UML diagrams generated successfully",
            "details": {
                "Repository": repo_url,
                "Output Paths": final_output_paths  # This is now a list of file paths
            }
        }, 200

    except Exception as e:
        logger.error(f"Error during UML generation: {str(e)}")
        return {"error": str(e)}, 500

    finally:
        # Clean up the temporary directory
        if temp_dir is not None:
            logger.info("Cleaning up temporary directory")
            shutil.rmtree(temp_dir)

