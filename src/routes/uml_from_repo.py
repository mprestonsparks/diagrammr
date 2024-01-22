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
from routes.retrieve_code import clone_repo, retrieve_code
from routes.code_to_uml import generate_content  # Import the function from code_to_uml.py


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

def process_request(data):
    git_repo_url = data.get('gitRepoUrl')
    output_directory = data.get('local_dir')  # Get the output directory from the request data
    github_access_token = data.get('gitHubAccessToken')
    branch_name = data.get('branchName', 'master')  # 'master' is the default branch name
    if not git_repo_url or not output_directory or not github_access_token or not branch_name:
        logger.error("Missing required parameters")  
        return {"error": "Missing required parameters"}, 400

    try:
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
        except Exception as e:
            logger.error(f"Error during UML generation: {str(e)}", exc_info=True)
            return {"error": str(e)}, 500
        finally:
            # Clean up the temporary directory
            if temp_dir is not None:
                logger.info("Cleaning up temporary directory")
                shutil.rmtree(temp_dir)

        # Clone the repository
        repo = clone_repo(git_repo_url, temp_dir, github_access_token)
         
        # Load the config
        with open('src/routes/config.json', 'r') as f:
            config = json.load(f)
        
        def traverse_directories(repo, temp_dir, config):
            included_files = {}
            for item in repo.tree().traverse():
                if item.type == 'blob':  # This means it's a file, not a directory
                    for pattern in config['include']:
                        if fnmatch.fnmatch(item.path, pattern):
                            with open(os.path.join(temp_dir, item.path), 'r') as f:
                                included_files[item.path] = f.read()
                            break  # No need to check the remaining patterns
            return included_files

        # Retrieve the code from the repository
        included_files = traverse_directories(repo, temp_dir, config)

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
                "Repository": git_repo_url,
                "Output Paths": final_output_paths  # This is now a list of file paths
            }
        }, 200

    except Exception as e:
        logger.error(f"Error during UML generation: {str(e)}")
        return {"error": str(e)}, 500

    finally:
        # Clean up the temporary directory
        logger.info("Cleaning up temporary directory")
        shutil.rmtree(temp_dir)

 