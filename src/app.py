import os
import shutil
from flask import Flask, jsonify, request
from routes.uml_from_repo import process_request  # Import the function from uml_from_repo.py
from models.git_repo import GitRepo  # Import GitRepo
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
    config_file = data.get('configFile')
    github_access_token = data.get('gitHubAccessToken')
    app.logger.info(f"Received configFile: {config_file}")
    app.logger.info(f"Received gitHubAccessToken: {github_access_token}")
    return config_file, github_access_token

def validate_parameters(config_file, github_access_token):
    if not config_file or not github_access_token:
        return jsonify({"error": "Missing required parameters"}), 400

def create_git_repo(config_file):
    output_dir = "../../output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    git_repo = GitRepo(config_file)  # Create a GitRepo object
    git_repo.clone()  # Clone the repository
    return git_repo

def process_and_respond(git_repo, github_access_token):
    try:
        response = process_request(git_repo, github_access_token)  # Call the process_request function with the GitRepo object
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-uml', methods=['POST'])
def generate_uml():
    data = request.json
    log_data(data)

    config_file, github_access_token = get_parameters(data)
    validate_parameters(config_file, github_access_token)

    git_repo = create_git_repo(config_file)
    return process_and_respond(git_repo, github_access_token)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', True), port=os.getenv('FLASK_PORT', 5000))
