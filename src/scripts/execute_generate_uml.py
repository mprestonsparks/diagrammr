import json
import os
import requests
import logging
from logging import handlers
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging to write to a file
log_directory = '../../logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'execute_generate_uml.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

# Current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Configuration file path
config_file_path = os.path.join(current_dir, '..', 'routes', 'config.json')

# Read configuration from the JSON file
with open(config_file_path, 'r') as config_file:
    config_data = json.load(config_file)

# Configuration file path for git_repo_config
git_repo_config_path = os.path.join(current_dir, 'git_repo_config.json')

# Read git repository configuration from the git_repo_config.json file
with open(git_repo_config_path, 'r') as git_repo_config_file:
    git_repo_data = json.load(git_repo_config_file)

# Retrieve the GitHub access token from environment variables
github_token = os.getenv('GITHUB_PAT')

# Update the config_data with the GitHub access token and gitRepoUrl
config_data['gitHubAccessToken'] = github_token
config_data['gitRepoUrl'] = git_repo_data['gitRepoUrl']  # Add this line to include gitRepoUrl

# Define payload with the data to send
payload = {
    'gitHubAccessToken': config_data['gitHubAccessToken'],
    'gitRepoUrl': config_data['gitRepoUrl'],
    # Add other necessary data from config_data or as required by your application
}

# Endpoint URL
url = 'http://127.0.0.1:5000/generate-uml'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Retrieve the local repository and output directory from the configuration
local_repo_dir = os.path.join(current_dir, config_data['local_dir'])
output_dir = os.path.join(current_dir, config_data['outputDirectory'])

# Ensure the local repository and output directories exist
os.makedirs(local_repo_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Log the JSON data being sent in the request
logger.info(f'Sending JSON data to {url}:')
logger.info(json.dumps(payload, indent=2))

try:
    # Make the POST request with the updated payload
    response = requests.post(url, headers=headers, json=payload)

    # Log the response from the server
    logger.info(f'Response from server ({url}):')
    logger.info(f'Status Code: {response.status_code}')
    logger.info(f'Response Text: {response.text}')

    # Print the response from the server
    print(response.text)

    # Save the response to a file in the output directory
    with open(os.path.join(output_dir, 'response.json'), 'w') as output_file:
        json.dump(response.json(), output_file, indent=2)

except Exception as e:
    # Log any exceptions that occur
    logger.error(f'Error occurred: {str(e)}')
