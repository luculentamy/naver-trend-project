import os
import requests
import json
from datetime import datetime, timedelta

client_id = os.environ.get("NAVER_CLIENT_ID")
client_secret = os.environ.get("NAVER_CLIENT_SECRET")

url = "https://openapi.naver.com/v1/datalab/search"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret,
    "Content-Type": "application/json"
}

today = datetime.today()
one_week_ago = today - timedelta(days=7)

data = {
    "startDate": one_week_ago.strftime("%Y-%m-%d"),
    "endDate": today.strftime("%Y-%m-%d"),
    "timeUnit": "date",
    "keywordGroups": [
        {
            "groupName": "ChatGPT",
            "keywords": ["ChatGPT"]
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())

print("CLIENT ID:", client_id)
print("CLIENT Secret:", client_secret)
