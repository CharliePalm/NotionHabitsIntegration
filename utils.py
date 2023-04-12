
NOTION_BASE_URL = 'https://api.notion.com/v1/'
import json
import requests

def get_icon(obj) -> str | None:
    if obj and 'icon' in obj:
        return obj['icon']['emoji'] if 'emoji' in obj else obj['icon']['external']
    return None

class Bridge:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = self.get_headers()
        
    def get_headers(self):
        return {
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.api_key
        }
        
    def query(self, db_id, body):
        r = requests.post(NOTION_BASE_URL + 'databases/' + db_id + '/query', headers=self.headers, data=json.dumps(body))
        if r.status_code != 200:
            print('UTIL: error querying URL ' + NOTION_BASE_URL + 'databases/' + db_id + '/query' + ': ')
            raise Exception(r.json())
        return r
    
    def create_db_page(self, db_id, properties, icon, use_emoji = True):
        payload = {
            'parent': {
                'type': 'database_id',
                'database_id': db_id,
            },
            'properties': properties,
        }
        if icon:
            payload['icon'] = {
                'type': 'emoji' if use_emoji else 'external',
                'emoji' if use_emoji else 'external': icon,
            }
        response = requests.post(NOTION_BASE_URL + 'pages', headers=self.headers, data=json.dumps(payload))
        if response.status_code != 200:
            print('UTIL: error encountered creating page')
            print(response.json())
        return response
    
    def update_db_page(self, properties_to_update, id):
        payload = {
            'properties': properties_to_update,
        }
        response = requests.patch(NOTION_BASE_URL + 'pages/' + id, headers=self.headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(response.json())
            print('UTIL: error encountered updating page')
        return response