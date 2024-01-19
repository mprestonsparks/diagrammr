import json
import os
import logging
from openai_api import OpenAIAPI

class UMLGenerator:
    def __init__(self, config_file):
        self.api = OpenAIAPI()
        self.OUTPUT_DIRECTORY = "src/output" 
        # Load the configuration
        with open(config_file) as file:
            self.config = json.load(file)

    def generate_uml_diagrams(self, file_list):
        uml_contents = []
        for file in file_list:
            if self._should_skip_file(file):
                continue
            logging.info(f"Generating UML for file: {file}")
            with open(file, 'r') as f:
                file_content = f.read()
            uml_content = self.api.generate_uml_diagram(file_content)
            if uml_content != "UML generation failed":
                uml_contents.append(uml_content)
            else:
                logging.error(f"UML generation failed for file: {file}")
        return uml_contents

    def save_uml_diagrams(self, uml_contents, file_names):
        for uml_content, file_name in zip(uml_contents, file_names):
            logging.info(f"Saving UML diagram for file: {file_name}")
            self.api.save_uml_diagram(uml_content, file_name)

    def _should_skip_file(self, file):
        python_files_only = self.config.get('python_files_only', False)
        ignore_files = self.config.get('ignore_files', [])
        ignore_extensions = self.config.get('ignore_extensions', [])
        return (file in ignore_files or 
                (python_files_only and not file.endswith('.py')) or 
                any(file.endswith(ext) for ext in ignore_extensions))

    def _generate_uml_diagram(self, file):
        logging.info(f"Generating UML diagram for file: {file}")
        return self.api.generate_uml_diagram(file)