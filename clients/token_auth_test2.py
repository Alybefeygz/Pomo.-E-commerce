import requests
from pprint import pprint


#{'key': 'ee3f377698dc4bc77431164a085bbc434683154b'}

def client():

    token = 'Token 658eb6542a3da1ba27bc0b77e9415bcda0dea3e1'
    
    headers = {
        'Authorization': token,
    }
    response = requests.get(
        url = 'http://127.0.0.1:8000/api/kullanici-profilleri/',
        headers= headers,
  
    )
    
    print('Status Code:', response.status_code)
    
    response_data = response.json()
    pprint(response_data)
    
    
if __name__ == '__main__':
    client()