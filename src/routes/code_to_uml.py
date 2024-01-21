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

# code_to_uml.py
def generate_content(files, output_directory):
    logging.info(f"Files to process: {files}")  # Log the files dictionary
    generated_code = ""  # Initialize generated_code
    file_paths = []  # Initialize a list to store the file paths
    for file_path, code in files.items():
        logging.info(f"Processing file: {file_path}")
        generated_code_for_file = api.generate_from_code(code)
        logging.info(f"UML code generated for {file_path}: {generated_code_for_file}")  # Log the generated UML code
        if not generated_code_for_file or "UML generation failed" in generated_code_for_file:
            logging.error(f"Failed to generate UML diagram for {file_path}")
            raise ValueError(f"Failed to generate UML diagram for {file_path}")
        generated_code += generated_code_for_file

        # Save the UML code for each file to a separate .puml file
        file_name = f"{os.path.basename(file_path)}.puml"
        final_output_path = api.save_generated_output(generated_code_for_file, os.path.join(output_directory, file_name))
        file_paths.append(final_output_path)  # Append the file path to the list

    logging.info(f"Generated file paths: {file_paths}")
    # Return the list of file paths and the generated code
    return file_paths, generated_code