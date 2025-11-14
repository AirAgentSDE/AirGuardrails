import requests

base_url = "http://127.0.0.1:5070"

response = requests.get(f"{base_url}/v1/rails/configs")
print(response.json())

# make a request
response = requests.post(f"{base_url}/v1/chat/completions", json={
  "config_id": "config",
  "messages": [{
    "role": "user",
    "content": "你好"
  }]
})
print(response.json())