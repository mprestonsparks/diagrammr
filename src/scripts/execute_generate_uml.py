import json
import os
import requests
import tempfile
import logging
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

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

# Update the GitHub access token in the config data
config_data['gitHubAccessToken'] = github_token

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

except Exception as e:
    # Log any exceptions that occur
    logging.error(f'Error occurred: {str(e)}')
