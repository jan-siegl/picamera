from datetime import datetime
import requests
import shutil
import os
from requests.auth import HTTPDigestAuth

url1 = 'http://10.3.0.11:80/ISAPI/Streaming/channels/101/picture'
url2 = 'http://10.3.0.11:80/ISAPI/Streaming/channels/701/picture'

response1 = requests.get(url1, auth=HTTPDigestAuth('AgentDispecink', 'Koukam2023!'))
response2 = requests.get(url2, auth=HTTPDigestAuth('AgentDispecink', 'Koukam2023!'))

now = datetime.now()
url = "/Users/honza/Documents/SIEGLsro/develop/picamera/pictures/{}/".format(now)
os.makedirs(os.path.dirname(url), exist_ok=True)
print(url)
if response1.status_code == 200:
    with open(url + "1.jpg", 'wb') as f:
        f.write(response1.content)
del response1

if response2.status_code == 200:
    with open(url + "2.jpg", 'wb') as f:
        f.write(response2.content)
del response2