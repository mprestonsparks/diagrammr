from services.openai_api import OpenAIAPI
from models.git_repo import GitRepo
import os
import json
import logging

logger = logging.getLogger(__name__)

class ETLWorkflow:
    def __init__(self, openai_api, git_repo_config):
        # Ensure the local_repo directory exists
        if not os.path.exists(git_repo_config['local_dir']):
            os.makedirs(git_repo_config['local_dir'])
        self.openai_api = openai_api
        self.git_repo = GitRepo(git_repo_config)
        self.git_repo.clone_or_pull()  # Clone the repository once during initialization

    def execute(self, file_path, title):
        # No need to clone for each file, as the repository is already cloned during initialization
        full_file_path = os.path.join(self.git_repo.local_dir, file_path)
        try:
            raw_code = self.get_code_from_repo(full_file_path)
            logger.debug(f"Retrieved code from {full_file_path}: {raw_code}")
            summary = self.get_summary_from_openai(raw_code)
            cleaned_summary = self.clean_response(summary)
            logger.debug(f"Cleaned summary: {cleaned_summary}")
            puml_code = self.get_puml_from_openai(cleaned_summary, title)
            logger.debug(f"Generated PUML code: {puml_code}")
            # Instead of saving the output here, return the generated PUML code
            return puml_code
        except Exception as e:
            logger.error(f"Error in ETL workflow execution for file {file_path}: {str(e)}", exc_info=True)
            raise

    def get_code_from_repo(self, full_file_path):
        # Assuming retrieve_code() now works with a path to the local file system
        return self.git_repo.retrieve_code(full_file_path)

    def get_summary_from_openai(self, raw_code):
        summary_prompt = f"Summarize the following code:\n\n{raw_code}"
        summary_response = self.openai_api.client.completions.create(
            model=self.openai_api.MODEL_NAME,
            prompt=summary_prompt,
            max_tokens=self.openai_api.MAX_TOKENS)
        return summary_response.choices[0].text

    def get_puml_from_openai(self, cleaned_summary, title):
        puml_prompt = f"Create a UML diagram in .puml format based on the following summary:\n\n{cleaned_summary}"
        puml_response = self.openai_api.client.completions.create(
            model=self.openai_api.MODEL_NAME,
            prompt=puml_prompt,
            max_tokens=self.openai_api.MAX_TOKENS)
        generated_code = puml_response.choices[0].text.strip()
        return f"@startuml\n" + f"title {title}\n" + generated_code + "\n@enduml\n"

    def clean_response(self, response):
        # Implement your cleaning logic here
        cleaned_response = response  # Placeholder
        return cleaned_response