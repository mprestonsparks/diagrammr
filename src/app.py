import os
import shutil
from flask import Flask, jsonify, request
from routes.uml_from_repo import process_request
from models.git_repo import GitRepo
import logging
 
# Configure logging to a file
logging.basicConfig(filename='server.log', level=logging.DEBUG)

# Configure logging to the console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify(message="Welcome to the UML Diagram Generator API")

def log_data(data):
    app.logger.info(f"Received JSON data: {data}")

def get_parameters(data):
    config = data.get('config')
    github_access_token = data.get('gitHubAccessToken')
    app.logger.info(f"get_parameters() received config")
    return config, github_access_token

def validate_parameters(config, github_access_token):
    if not github_access_token or not config:
        return jsonify({"error": "Missing required parameters"}), 400

def create_git_repo(config):
    git_repo = GitRepo(config)  # Pass config as an argument
    git_repo.clone_or_pull()  # Clone the repository
    return git_repo

def process_and_respond(git_repo, github_access_token):
    try:
        # Log the types and contents of git_repo and github_access_token
        app.logger.debug(f"Type of git_repo: {type(git_repo)}")
        app.logger.debug(f"Contents of git_repo: {git_repo.__dict__}")  # Assuming git_repo is an object with properties
        app.logger.debug(f"Type of github_access_token: {type(github_access_token)}")

        response, status_code = process_request(git_repo, github_access_token)  # Unpack the tuple
        return jsonify(response), status_code  # Return the JSON response and status code
    except Exception as e:
        # Log the exception with traceback
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/generate-uml', methods=['POST'])
def generate_uml():
    data = request.json
    log_data(data)

    config, github_access_token = get_parameters(data)
    if not config:
        return jsonify({"error": "Missing 'config' parameter"}), 400

    validation_response = validate_parameters(config, github_access_token)
    if validation_response:
        return validation_response

    git_repo = create_git_repo(config)  # Pass the config to the function
    return process_and_respond(git_repo, github_access_token)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', True), port=os.getenv('FLASK_PORT', 5000))
