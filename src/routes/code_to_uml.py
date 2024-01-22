# code_to_uml.py
import os
from openai_api import OpenAIAPI 
import logging
from logging import handlers  

# Create an instance of the OpenAI API
api = OpenAIAPI()

# Configure logging to write to a file
log_directory = 'logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'code_to_uml.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def generate_content(files, output_directory):
    logging.info(f"Files to process: {files}")  # Log the files dictionary
    file_paths = []  # Initialize a list to store the file paths
    for file_path, code in files.items():
        # Skip if the file is empty
        if not code.strip():
            logging.info(f"Skipping empty file: {file_path}")
            continue
        logging.info(f"Processing file: {file_path}")
        response = api.generate_from_code(code, os.path.basename(file_path))
        # Extract the UML code from the response
        generated_code_for_file = extract_uml_code(response)
        if generated_code_for_file is None:
            logging.error(f"Failed to generate UML diagram for {file_path}")
            continue
        logging.info(f"UML code generated for {file_path}: {generated_code_for_file}")  # Log the generated UML code

        # Save the UML code for each file to a separate .puml file
        file_name = f"{os.path.basename(file_path)}.puml"
        final_output_path = api.save_generated_output(generated_code_for_file, os.path.join(output_directory, file_name))
        file_paths.append(final_output_path)  # Append the file path to the list

    logging.info(f"Generated file paths: {file_paths}")
    # Return the list of file paths
    return file_paths

def extract_uml_code(response):
    # Split the response into lines
    lines = response.split('\n')
    # Check if '@startuml' and '@enduml' are in the response
    if '@startuml' not in response or '@enduml' not in response:
        logging.error("Failed to extract UML code from the response. '@startuml' or '@enduml' not found.")
        return None
    # Find the start and end of the UML code
    start_index = lines.index('@startuml')
    end_index = lines.index('@enduml') if '@enduml' in lines else -1
    # Extract the UML code
    uml_code = '\n'.join(lines[start_index:end_index+1])
    return uml_code