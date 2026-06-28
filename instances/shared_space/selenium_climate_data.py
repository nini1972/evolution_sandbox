# Climate Data Extraction using Selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Set up Chrome options
options = Options()
options.add_argument('--headless')

# Initialize the webdriver
driver = webdriver.Chrome(options=options)

driver.get("https://unfccc.int/")

time.sleep(5)

# Get the HTML content
html = driver.page_source

driver.quit()

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

# Find the climate data elements
climate_data_elements = soup.find_all(['section', 'div'])

# Extract the climate data
climate_data = []
for element in climate_data_elements:
    climate_data.append(element.text.strip())

# Create a pandas DataFrame
df = pd.DataFrame(climate_data, columns=['Climate Data'])

# Save the DataFrame to a CSV file
df.to_csv('../../shared_space/climate_data.csv', index=False)