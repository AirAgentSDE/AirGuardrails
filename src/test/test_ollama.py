import sys
import os
from ..app.gradio_chatbot import ApiClient

client = ApiClient()
response = client.request_ollama("你好")
print(response["message"].get("content", "Ollama返回了意外的响应格式"))
