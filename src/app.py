from flask import Flask, jsonify, request
import tempfile
from routes.retrieve_code import clone_repo, retrieve_code
from routes.generate_uml_diagram import generate_uml_content
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

@app.route('/generate-uml', methods=['POST'])
def generate_uml():
    data = request.json
    app.logger.info(f"Received JSON data: {data}")

    git_repo_url = data.get('gitRepoUrl')
    local_dir = "./output"  # Changed from 'outputDirectory' to 'local_dir'
    github_access_token = data.get('gitHubAccessToken')
    app.logger.info(f"Received gitRepoUrl: {git_repo_url}")
    app.logger.info(f"Received local_dir: {local_dir}")  # Changed from 'outputDirectory' to 'local_dir'
    app.logger.info(f"Received gitHubAccessToken: {github_access_token}")


    if not git_repo_url or not local_dir or not github_access_token:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        temp_dir = tempfile.mkdtemp()
        repo = clone_repo(git_repo_url, temp_dir, github_access_token)
        code = retrieve_code(repo, "master")  # Replace with your desired commit or branch
        uml_file_path = generate_uml_content(code)

        return jsonify({
            "message": "UML diagrams generated successfully",
            "details": {
                "Repository": git_repo_url,
                "Output Path": uml_file_path
            }
        }), 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

