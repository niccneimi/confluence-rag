import requests
import urllib3
import json
import ast
import os

from src.config import ATLASSIAN_URL, ATLASSIAN_PAT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_page_ids(parent_id, base_url, api_token, visited=None):
    if visited is None:
        visited = set()
    
    if parent_id in visited:
        return visited
    
    visited.add(parent_id)
    url = f"{base_url}/rest/api/content/{parent_id}/child/page"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            for child in data.get('results', []):
                get_all_page_ids(child['id'], base_url, api_token, visited)
    except requests.exceptions.RequestException:
        pass
    
    return list(visited)
 
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
    # parent_page_id = 948835021
    # page_ids = get_all_page_ids(parent_page_id, ATLASSIAN_URL, ATLASSIAN_PAT)
    # with open('qa_page_ids.txt', 'w') as f:
    #     f.write(str(page_ids))
    with open('qa_page_ids.txt', 'r') as f:
        content = f.read()

    page_ids = ast.literal_eval(content)    
    
    for page_id in page_ids:
        confluense_page = get_confluence_page(page_id, ATLASSIAN_URL, ATLASSIAN_PAT)
        confluense_page_name = f"{confluense_page['title'].replace(' ', '_').replace('/', '_')}.json"
        if confluense_page_name not in os.listdir('data/raw/QA'):
            with open(f"data/raw/QA/{confluense_page_name}", 'w', encoding='utf-8') as file:
                json.dump(confluense_page, file, ensure_ascii=False, indent=4)