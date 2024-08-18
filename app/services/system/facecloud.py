import os

import requests
from dotenv import load_dotenv


load_dotenv()

FACE_CLOUD_API_URL = os.getenv('FACE_CLOUD_API_URL')
FACE_CLOUD_USERNAME = os.getenv('FACE_CLOUD_USERNAME')
FACE_CLOUD_PASSWORD = os.getenv('FACE_CLOUD_PASSWORD')


def get_facecloud_token():
    url = f"{FACE_CLOUD_API_URL}/login"
    response = requests.post(url,
                             json={"email": FACE_CLOUD_USERNAME, "password": FACE_CLOUD_PASSWORD})

    return response.json()["data"]['access_token']


async def detect_faces_api(file_bytes: bytes):
    url = f"{FACE_CLOUD_API_URL}/detect?demographics=True"
    bearer_token = get_facecloud_token()
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'image/jpeg',
    }
    response = requests.post(url, headers=headers, data=file_bytes)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}

