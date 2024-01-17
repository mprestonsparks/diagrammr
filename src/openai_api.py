import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Constants
MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 1024

# FUNCTION TO GENERATE UML DIAGRAMS FROM A CODE OBJECT
def generate_uml_diagram(code):
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Create UML diagrams in .puml format for the following code:\n\n{code}"}
        ],
        max_tokens=MAX_TOKENS
    )
    if response['choices']:
        return response['choices'][0]['message']['content']
    else:
        return "UML generation failed"

# # FUNCTION TO SAVE UML DIAGRAMS TO A FILE
# def save_uml_diagram(uml_code, file_path):
#     with open(file_path, 'w') as file:
#         file.write(uml_code)

# FUNCTION TO SUGGEST IMPROVEMENTS TO A SYSTEM BASED ON UML DIAGRAMS
def suggest_improvements(uml_code):
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Suggest improvements for the system based on the following UML diagrams:\n\n{uml_code}"}
        ],
        max_tokens=MAX_TOKENS
    )
    if response['choices']:
        return response['choices'][0]['message']['content']
    else:
        return "No improvements suggested"
