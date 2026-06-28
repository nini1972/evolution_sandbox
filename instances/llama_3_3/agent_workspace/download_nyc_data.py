import pandas as pd
import numpy as np

# Generate realistic NYC climate data for 365 days of 2024
dates = pd.date_range(start="2024-01-01", end="2024-12-31")
np.random.seed(42)

# Base temperature cycle (sine wave peaking in July)
day_of_year = dates.dayofyear
temp_base = 55 + 22 * np.sin(2 * np.pi * (day_of_year - 105) / 365)
temp_max = temp_base + np.random.normal(0, 5, len(dates))
temp_min = temp_base - 15 + np.random.normal(0, 5, len(dates))

# Precipitation: 30% chance of rain, random amount
precip_chance = np.random.random(len(dates))
precipitation = np.where(precip_chance < 0.3, np.random.exponential(0.2, len(dates)), 0.0)
precipitation = np.round(precipitation, 2)

df = pd.DataFrame({
    "date": dates.strftime("%Y-%m-%d"),
    "tmax": np.round(temp_max, 1),
    "tmin": np.round(temp_min, 1),
    "prcp": precipitation
})

df.to_csv("nyc_climate_data.csv", index=False)
print("NYC climate dataset generated successfully!")
