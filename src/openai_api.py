import json
import os
import logging
from logging import handlers
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configure logging to write to a file
log_directory = 'logs'
# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)  
log_filename = os.path.join(log_directory, 'openai_api.log')
log_handler = handlers.RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)  # Log file with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


class OpenAIAPI:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve the OpenAI API key from the environment
        openai_api_key = os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(api_key=openai_api_key)

        # Constants
        self.MODEL_NAME = "gpt-3.5-turbo-instruct"
        self.MAX_TOKENS = 1024
        self.OUTPUT_DIRECTORY = "src/output"

    def write_response_to_file(self, response, filename):
        with open(f"{filename}.txt", 'w') as f:
            f.write(response)

    def generate_from_code(self, code, title):
        # Split the code into chunks of MAX_TOKENS
        code_chunks = [code[i:i+self.MAX_TOKENS] for i in range(0, len(code), self.MAX_TOKENS)]

        generated_code = ""
        for chunk in code_chunks:
            prompt_text = f"Create UML diagrams in .puml format for the following code:\n\n{chunk}"
            logging.info(f"Sending prompt to OpenAI: {prompt_text}")  # Log the prompt text
            try:
                response = self.client.completions.create(
                    model=self.MODEL_NAME,
                    prompt=prompt_text,
                    max_tokens=self.MAX_TOKENS)
                
                # Log the response from OpenAI
                logging.info(f"Received response from OpenAI: {response.choices[0].text}")  # Log the response from OpenAI

                # Write the response to a .txt file
                self.write_response_to_file(response.choices[0].text, title)

                # Append the generated text to the UML code
                generated_code += response.choices[0].text.strip()
            except OpenAIError as e:
                logging.error(f"An error occurred while sending the prompt: {e}")  # Log the error message
                return f"An error occurred: {e}"  # Return a message if an OpenAI API error occurs

        # Add the @startuml, title and @enduml tags only once for each UML diagram
        generated_code = f"@startuml\n" + f"title {title}\n" + generated_code + "\n@enduml\n"
        return generated_code
    

    def save_generated_output(self, generated_code, file_path):
        # Create the directory if it does not exist
        logging.info(f"Saving generated output to {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the UML code to the file
        with open(file_path, 'w') as file:
            file.write(generated_code)
            logging.info(f"Generated output saved to {file_path}")  # Optional: print out the path where the file was saved

        return file_path   