import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("MODEL_NAME", "gpt-4.1")