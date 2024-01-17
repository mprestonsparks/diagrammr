import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
# Constants
MODEL_NAME = "text-davinci-003"
MAX_TOKENS = 1024


# FUNCTION TO GENERATE UML DIAGRAMS FROM A CODE OBJECT
def generate_uml_diagram(code, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.Completion.create(
        model=MODEL_NAME,
        prompt=f"Create UML diagrams in .puml format for the following code:\n\n{code}",
        max_tokens=MAX_TOKENS
    )
    if response.choices:
        return response.choices[0].text
    else:
        return "UML generation failed"

# Example Usage
# uml_diagram = generate_uml_diagram(file_content, openai_api_key)


# FUNCTION TO SAVE UML DIAGRAMS TO A FILE
def save_uml_diagram(uml_code, file_path):
    with open(file_path, 'w') as file:
        file.write(uml_code)

# Example Usage
# save_uml_diagram(uml_diagram, 'output.puml')


# FUNCTION TO SUGGEST IMPROVEMENTS TO A SYSTEM BASED ON UML DIAGRAMS
def suggest_improvements(uml_code, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.Completion.create(
        model=MODEL_NAME,
        prompt=f"Suggest improvements for the system based on the following UML diagrams:\n\n{uml_code}",
        max_tokens=MAX_TOKENS
    )
    if response.choices:
        return response.choices[0].text
    else:
        return "No improvements suggested"

# Example Usage
# improvements = suggest_improvements(uml_diagram, openai_api_key)
