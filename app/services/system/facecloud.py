import os

import requests
from dotenv import load_dotenv
from fastapi import UploadFile, File


load_dotenv()


async def detect_faces_api(file: UploadFile = File(...)):
    url = "https://backend.facecloud.tevian.ru/api/v1/detect?demographics=True"
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MjM3MjEwNzYsIm5iZiI6MTcyMzcyMTA3NiwianRpIjoiYzc0NjJkZTUtMzZhZS00NTZkLWFkNDEtNmJlN2FhMzY2N2Q4Iiwic3ViIjo0NDQsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.0XbiwsW7pYSQ4Nlfds3XXbKtusquWkT12zOV6wqVdrc"
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'image/jpeg',
    }
    # TODO убрать хардкод
    file_bytes = await file.read()
    response = requests.post(url, headers=headers, data=file_bytes)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}

