from dotenv import load_dotenv
import os

load_dotenv()

LLMOPS_API_KEY = os.getenv('LLMOPS_API_KEY')
LLMOPS_BASE_URL = os.getenv('LLMOPS_BASE_URL')

ATLASSIAN_URL = os.getenv('ATLASSIAN_URL')
ATLASSIAN_USERNAME = os.getenv('ATLASSIAN_USERNAME')
ATLASSIAN_PAT = os.getenv('ATLASSIAN_PAT')

QDRANT_HOST = os.getenv('QDRANT_HOST')
QDRANT_PORT = os.getenv('QDRANT_PORT')
QDRANT_KEY = os.getenv("QDRANT_KEY")