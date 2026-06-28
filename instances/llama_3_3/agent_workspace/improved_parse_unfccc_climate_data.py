# Initial implementation storing data to shared directory
import os
from bs4 import BeautifulSoup
import requests
import pandas as pd

url = "https://data.unfccc.int/"
text = requests.get(url).text
soup = BeautifulSoup(text, 'html.parser')
sections = soup.find_all([
    # Specify the HTML tags that contain climate data
    "section", "div"
])
data = []

# Example loop - this would need to be optimized
for section in sections:
    # Extract climate data
    climate_data = section.text.strip()
    data.append([climate_data])

df = pd.DataFrame(data)
df.to_csv("../../shared_space/climate_data.csv", index=False)