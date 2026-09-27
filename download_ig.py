import requests
import json
url = 'https://api.cobalt.tools/api/json'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
data = {
    'url': 'https://www.instagram.com/reel/DdROLEmupO4/',
    'vCodec': 'h264',
    'isAudioOnly': False
}
r = requests.post(url, headers=headers, json=data)
print(r.text)
