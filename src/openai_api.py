import json
import os
import logging
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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


    def generate_uml_diagram(self, code):
        # Split the code into chunks of MAX_TOKENS
        code_chunks = [code[i:i+self.MAX_TOKENS] for i in range(0, len(code), self.MAX_TOKENS)]

        uml_code = ""
        for chunk in code_chunks:
            prompt_text = f"Create UML diagrams in .puml format for the following code:\n\n{chunk}"
            logging.info(f"Sending prompt to OpenAI: {prompt_text}")  # Log the prompt text
            try:
                response = self.client.completions.create(
                    model=self.MODEL_NAME,
                    prompt=prompt_text,
                    max_tokens=self.MAX_TOKENS)
                
                # Log the response from OpenAI
                logging.info(f"Received response from OpenAI: {response.data}")  # Log the response from OpenAI

                # Check if response is a string and try to parse it into a dictionary
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                    except json.JSONDecodeError:
                        logging.error("Failed to parse response into a dictionary")
                        return "UML generation failed"

                if 'choices' in response:
                    uml_code += response['choices'][0]['text']  # Append the generated text to the UML code
                else:
                    return "UML generation failed"  # Return a message if no choice was found
            except OpenAIError as e:
                logging.error(f"An error occurred while sending the prompt: {e}")  # Log the error message
                return f"An error occurred: {e}"  # Return a message if an OpenAI API error occurs

        return uml_code
    

    def save_uml_diagram(self, uml_code, file_name):
        # Create the full file path
        file_path = os.path.join(self.OUTPUT_DIRECTORY, file_name)
        print(f'File path: {file_path}')

        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the UML code to the file
        with open(file_path, 'w') as file:
            file.write(uml_code)
            logging.info(f"UML diagram saved to {file_path}")  # Optional: print out the path where the file was saved