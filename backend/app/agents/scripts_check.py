"""this file is strictly aimed at checking the avilable models for the api key we hold
    in bash terminal: cd to backend/agents/
    run : python scripts_check.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

# This WORKS despite Pylance warnings
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models = genai.list_models()

for model in models:
    print(model.name, "->", model.supported_generation_methods)
