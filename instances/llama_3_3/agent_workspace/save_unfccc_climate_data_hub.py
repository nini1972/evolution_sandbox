import requests

response = requests.get("https://data.unfccc.int/")
print("Status code: ", response.status_code)

with open("unfccc_climate_data_hub.html", "wb") as file:
    file.write(response.content)
    print("UNFCCC Climate Data Hub webpage saved successfully!")
