from datetime import datetime
import requests
import shutil
import os
from requests.auth import HTTPDigestAuth

def savePicture(weight):

    url1 = 'http://10.3.0.11:80/ISAPI/Streaming/channels/101/picture'
    url2 = 'http://10.3.0.11:80/ISAPI/Streaming/channels/701/picture'
    url3 = 'http://10.3.0.11:80/ISAPI/Streaming/channels/401/picture'

    response1 = requests.get(url1, auth=HTTPDigestAuth('AgentDispecink', 'Koukam2023!'))
    response2 = requests.get(url2, auth=HTTPDigestAuth('AgentDispecink', 'Koukam2023!'))
    response3 = requests.get(url3, auth=HTTPDigestAuth('AgentDispecink', 'Koukam2023!'))

    now = datetime.now()
    nowStr = (now.strftime("%d-%m-%Y_%H-%M-w") + str(weight) + "t")
    #nowStr.replace(".", "_")
    url = "C:/Users/CV/Documents/GitHub/picamera/pictures/{}/".format(nowStr)
    os.makedirs(os.path.dirname(url), exist_ok=True)
    print(url)
    if response1.status_code == 200:
        with open(url + "front.jpg", 'wb') as f:
            f.write(response1.content)
    del response1

    if response2.status_code == 200:
        with open(url + "top.jpg", 'wb') as f:
            f.write(response2.content)
    del response2
    if response3.status_code == 200:
        with open(url + "weight.jpg", 'wb') as f:
            f.write(response3.content)
    del response3