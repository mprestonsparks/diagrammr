# src/models/uml_diagram.py
import os
import logging
from logging import handlers

# Configure logging to write to a file
log_directory = 'logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'models_uml_diagram.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

class UMLDiagram:
    def __init__(self, code, title):
        self.code = code
        self.title = title
        self.uml_code = None

    def generate(self, openai_api):
        self.uml_code = openai_api.generate_from_code(self.code, self.title)

    def save(self, openai_api, file_path):
        if self.uml_code is not None:
            openai_api.save_generated_output(self.uml_code, file_path)