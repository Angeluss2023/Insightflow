import requests

url = "https://deepseek-v3.p.rapidapi.com/chat"

headers = {
    "Content-Type": "application/json",
    "X-RapidAPI-Host": "deepseek-v3.p.rapidapi.com",
    "X-RapidAPI-Key": "ea163cdf23msh762ce0bafd319c5p17919fjsnd77c2ddf11de"
}

payload = {
    "messages": [
        {"role": "user", "content": "There are ten birds in a tree. A hunter shoots one. How many are left in the tree?"}
    ]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Éxito:", response.json())
else:
    print(f"Error {response.status_code}:", response.text)