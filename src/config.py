from dotenv import load_dotenv
import os

load_dotenv()

LLMOPS_API_KEY = os.getenv('LLMOPS_API_KEY')
LLMOPS_BASE_URL = os.getenv('LLMOPS_BASE_URL')

ATLASSIAN_URL = os.getenv('ATLASSIAN_URL')
ATLASSIAN_USERNAME = os.getenv('ATLASSIAN_USERNAME')
ATLASSIAN_PAT = os.getenv('ATLASSIAN_PAT')