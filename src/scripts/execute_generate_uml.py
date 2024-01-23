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


# Configure logging
logging.basicConfig(filename='execute_generate_uml.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Configuration file path
config_file_path = os.path.join(current_dir, 'config.json')

# Read configuration from the JSON file
with open(config_file_path, 'r') as config_file:
    config_data = json.load(config_file)

# Retrieve the GitHub access token from environment variables
github_token = os.getenv('GITHUB_PAT')

# Endpoint URL
url = 'http://127.0.0.1:5000/generate-uml'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Update the GitHub access token, local directory, and configFile in the config data
config_data['gitHubAccessToken'] = github_token
config_data['local_dir'] = os.path.join(current_dir, '../..', 'output')
config_data['configFile'] = config_file_path  

# Log the JSON data being sent in the request
logging.info(f'Sending JSON data to {url}:')
logging.info(json.dumps(config_data, indent=2))

try:
    # Make the POST request
    response = requests.post(url, headers=headers, json=config_data)

    # Log the response from the server
    logging.info(f'Response from server ({url}):')
    logging.info(f'Status Code: {response.status_code}')
    logging.info(f'Response Text: {response.text}')

    # Print the response from the server
    print(response.text)

    # Save the response to a file in the output directory
    output_dir = os.path.join(current_dir, '../..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'response.json'), 'w') as output_file:
        json.dump(response.json(), output_file, indent=2)

except Exception as e:
    # Log any exceptions that occur
    logging.error(f'Error occurred: {str(e)}')