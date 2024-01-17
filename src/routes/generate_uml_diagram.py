import os
import subprocess
import tempfile
import shutil
import openai
import logging
from logging import handlers  # Import the handlers module
from openai import generate_uml_diagram as openai_generate_uml_diagram, save_uml_diagram as openai_save_uml_diagram
from routes.retrieve_code import clone_repo, retrieve_code

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
    output_directory = data.get('outputDirectory')
    github_access_token = data.get('gitHubAccessToken')
    if not git_repo_url or not output_directory or not github_access_token:
        logging.error("Missing required parameters")
        return {"error": "Missing required parameters"}, 400

    try:
        temp_dir = tempfile.mkdtemp()

        # Clone the repository
        logging.info(f"Cloning repository: {git_repo_url}")
        repo = clone_repo(git_repo_url, temp_dir, github_access_token)
        
        # Retrieve the code from the repository (specify commit or branch as needed)
        logging.info("Retrieving code from repository")
        code = retrieve_code(repo, "master")  # Replace with your desired commit or branch
        
        # Generate the UML diagram using the OpenAI API
        logging.info("Generating UML diagram")
        uml_code = generate_uml_content(code)

        # Save the UML diagram to a file
        logging.info(f"Saving UML diagram to {output_directory}")
        final_output_path = openai_save_uml_diagram(uml_code, output_directory)

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

def generate_uml_content(code):
    # Call OpenAI API to generate UML diagram
    logging.info("Calling OpenAI API to generate UML diagram")
    uml_code = openai_generate_uml_diagram(code, openai.api_key)
    # Check if UML diagram was generated successfully
    if not uml_code or "UML generation failed" in uml_code:
        logging.error("Failed to generate UML diagram")
        raise ValueError("Failed to generate UML diagram")
    return uml_code
