import requests

def detect_faces(img):
    url = "https://backend.facecloud.tevian.ru/api/v1/detect?demographics=True"
    response = requests.post()