import requests
from datetime import datetime, timedelta
import time

# Replace 'your_api_token' with your actual Readwise API token
API_TOKEN = 'your_api_token'

# Get all highlights from Readwise
def get_all_highlights():
    url = 'https://readwise.io/api/v2/highlights/'
    headers = {
        'Authorization': f'Token {API_TOKEN}',
    }
    highlights = []
    next_page = url

    while next_page:
        response = requests.get(next_page, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))  # default to 60 seconds if not provided
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue
        if response.status_code != 200:
            print(f"Failed to fetch highlights: {response.status_code}")
            print(response.json())
            break
        data = response.json()
        if 'results' not in data:
            print(f"Unexpected response format: {data}")
            break
        highlights.extend(data['results'])
        next_page = data['next']
    
    return highlights

# Delete a highlight by ID
def delete_highlight(highlight_id):
    url = f'https://readwise.io/api/v2/highlights/{highlight_id}/'
    headers = {
        'Authorization': f'Token {API_TOKEN}',
    }
    response = requests.delete(url, headers=headers)
    return response.status_code

# Filter and delete highlights older than a year
def delete_old_highlights():
    all_highlights = get_all_highlights()
    one_year_ago = datetime.now() - timedelta(days=365)

    for highlight in all_highlights:
        highlighted_at = highlight['highlighted_at']
        if highlighted_at is not None:
            highlight_date = datetime.strptime(highlighted_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            if highlight_date < one_year_ago:
                delete_status = delete_highlight(highlight['id'])
                if delete_status == 204:
                    print(f"Deleted highlight ID {highlight['id']}")
                else:
                    print(f"Failed to delete highlight ID {highlight['id']} with status code {delete_status}")

# Run the deletion process
delete_old_highlights()
