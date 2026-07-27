import pandas as pd

def analyze_data(file_path):
    try:
        data = pd.read_csv(file_path)
        # Perform data analysis here
        print(data.head())
    except Exception as e:
        print(f"An error occurred: {e}")