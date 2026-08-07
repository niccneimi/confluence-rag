import requests
import urllib3
import json

from src.config import ATLASSIAN_URL, ATLASSIAN_PAT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_confluence_page(page_id, base_url, api_token):
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.view,version,metadata"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    response = requests.get(
        url,
        headers=headers,
        verify=False
    )

    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    confluense_page = get_confluence_page(2286246210, ATLASSIAN_URL, ATLASSIAN_PAT)
    confluense_page_name = f"{confluense_page['title'].replace(' ', '_')}.json"
    with open(f"data/raw/{confluense_page_name}", 'w', encoding='utf-8') as file:
        json.dump(confluense_page, file, ensure_ascii=False, indent=4)