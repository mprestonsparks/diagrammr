import os
import subprocess
import json
import git
import tempfile
import shutil
import openai
import logging
from logging import handlers  
from openai_api import OpenAIAPI 
from routes.retrieve_code import retrieve_code

# Create an instance of the OpenAI API
api = OpenAIAPI()

# Configure logging to write to a file
log_filename = 'uml_generation.log'
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

# Assume OPENAI_API_KEY is set in the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_uml_request(data):
    git_repo_url = data.get('gitRepoUrl')
    output_directory = "./output"
    github_access_token = data.get('gitHubAccessToken')
    if not git_repo_url or not output_directory or not github_access_token:
        logging.error("Missing required parameters")
        return {"error": "Missing required parameters"}, 400

    try:
        temp_dir = tempfile.mkdtemp()

        # Clone the repository
        logging.info(f"Cloning repository: {git_repo_url}")
        repo = git.Repo.clone_from(git_repo_url, temp_dir, github_access_token)
        
        # Load the config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Create a new object with the files to include
        files_to_include = {}
        for file in repo.tree():
            if file.path in config['include']:
                with open(file.abspath, 'r') as f:
                    files_to_include[file.path] = f.read()

        logging.debug(f"Type of files_to_include: {type(files_to_include)}")  # Debugging statement
        logging.debug(f"Value of files_to_include: {files_to_include}")  # Debugging statement

        uml_code = generate_uml_content(files_to_include)

        # Save the UML diagram to a file
        logging.info(f"Saving UML diagram to {output_directory}")
        final_output_path = api.save_uml_diagram(uml_code, output_directory)
        logging.info(f"UML diagram saved at: {final_output_path}")  # Log the path where the UML diagram was saved


        return {
            "message": "UML diagrams generated successfully",
            "details": {
                "Repository": git_repo_url,
                "Output Path": final_output_path
            }
        }, 200

    except Exception as e:
        logging.error(f"Error during UML generation: {str(e)}")
        return {"error": str(e)}, 500

    finally:
        # Clean up the temporary directory
        logging.info("Cleaning up temporary directory")
        shutil.rmtree(temp_dir)


def generate_uml_content(files):
    uml_code = ""
    for file_path, code in files.items():
        # Call OpenAI API to generate UML diagram for each file
        logging.info(f"Calling OpenAI API to generate UML diagram for {file_path}")
        uml_code_for_file = api.generate_uml_diagram(code)
        logging.info(f"Received UML code for {file_path}: {uml_code_for_file}")  # Log the UML code received for each file
        if not uml_code_for_file or "UML generation failed" in uml_code_for_file:
            logging.error(f"Failed to generate UML diagram for {file_path}")
            raise ValueError(f"Failed to generate UML diagram for {file_path}")
        uml_code += uml_code_for_file
    return uml_code