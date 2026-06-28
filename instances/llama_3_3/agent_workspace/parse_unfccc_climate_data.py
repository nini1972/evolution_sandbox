from bs4 import BeautifulSoup
import requests

# Send a GET request to the UNFCCC Climate Data Hub webpage
url = "https://data.unfccc.int/"
text = requests.get(url).text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(text, 'html.parser')

# Find all relevant climate data sections
climate_data_sections = soup.find_all([
    # Specify the HTML tags that contain climate data
    'section', 'div'
])

# Loop through each section and print its contents
for section in climate_data_sections:
    print(section.text)
