import requests

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
response = requests.get(url)

with open("AI_overview.md", "w", encoding="utf-8") as f:
    f.write(response.text)