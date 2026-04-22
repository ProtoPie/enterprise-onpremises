import requests
import re
import os

# Configuration
REPO = "protopie/enterprise-onpremises"
# The official Docker Hub API base URL
API_BASE = "https://hub.docker.com" 

# Set this to prepend a mirror prefix to images in docker-compose.yml
# e.g., "docker.m.daocloud.io/"
IMAGE_PREFIX = "" 

FILES_TO_UPDATE = ["docker-compose.yml", "README.md"]
DOCS_DIR = "docs"

def version_key(tag):
    """Extract version numbers for semantic sorting."""
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', tag)
    if match:
        return [int(x) for x in match.groups()]
    return [0, 0, 0]

def get_latest_tags(proxy=None):
    """Fetch the latest semantic tags from Docker Hub."""
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    print(f"Fetching tags for {REPO} via Docker Hub API...")
    url = f"{API_BASE}/v2/repositories/{REPO}/tags/?page_size=100"
    
    response = requests.get(url, proxies=proxies, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    tags = [tag['name'] for tag in data.get('results', [])]
    
    # Filter for semantic versions only (e.g., web-1.2.3), excluding hash-suffixed tags
    web_tags = [t for t in tags if re.match(r'^web-\d+\.\d+\.\d+$', t)]
    api_tags = [t for t in tags if re.match(r'^api-\d+\.\d+\.\d+$', t)]
    
    if not web_tags or not api_tags:
        raise Exception(f"No valid semantic tags found for {REPO}")
        
    # Get the highest version based on semantic rules
    latest_web = sorted(web_tags, key=version_key)[-1]
    latest_api = sorted(api_tags, key=version_key)[-1]
    
    return latest_web, latest_api

def update_files(latest_web, latest_api):
    """Update version tags in the specified files."""
    files = FILES_TO_UPDATE[:]
    if os.path.exists(DOCS_DIR):
        for f in os.listdir(DOCS_DIR):
            if f.endswith(".md"):
                files.append(os.path.join(DOCS_DIR, f))
    
    # Target strings with optional mirror prefix
    target_web = f"{IMAGE_PREFIX}{latest_web}"
    target_api = f"{IMAGE_PREFIX}{latest_api}"
    
    # Regex: Match tags preceded by ':' but not followed by ' =>'
    # Handles existing mirror prefixes: e.g., :mirror.com/web-1.2.3
    web_pattern = re.compile(r'(?<=:)(?:[\w\.]+/)*web-\d+\.\d+\.\d+(?!\s*=>)')
    api_pattern = re.compile(r'(?<=:)(?:[\w\.]+/)*api-\d+\.\d+\.\d+(?!\s*=>)')
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        print(f"Updating {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = web_pattern.sub(target_web, content)
        new_content = api_pattern.sub(target_api, new_content)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully updated {file_path}")
        else:
            print(f"No changes needed for {file_path}")

if __name__ == "__main__":
    try:
        # Auto-detect proxy from environment variables
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or \
                os.environ.get("https_proxy") or os.environ.get("http_proxy")
        
        web_ver, api_ver = get_latest_tags(proxy=proxy)
        print(f"Latest versions found: {web_ver}, {api_ver}")
        update_files(web_ver, api_ver)
    except Exception as e:
        print(f"Error: {e}")
