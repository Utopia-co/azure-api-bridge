import os
import json
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )