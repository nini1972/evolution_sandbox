import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv("nyc_climate_data.csv")

# Convert date field to datetime
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Calculate and plot the monthly average high and low temperatures
monthly_avg_temp = df[['tmax', 'tmin']].resample('MS').mean()
plt.figure(figsize=(10, 5))
plt.plot(monthly_avg_temp.index, monthly_avg_temp['tmax'], marker='o', label='Max Temp (TMAX)')
plt.plot(monthly_avg_temp.index, monthly_avg_temp['tmin'], marker='s', label='Min Temp (TMIN)')
plt.title('Monthly Average High and Low Temperatures in NYC in 2024')
plt.xlabel('Month')
plt.ylabel('Temperature (F)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.savefig('monthly_avg_temp.png', dpi=150, bbox_inches='tight')
plt.close()

# Calculate and plot the total monthly precipitation
monthly_prcp = df['prcp'].resample('MS').sum()
plt.figure(figsize=(10, 5))
# Use string index labels to prevent period conversion errors in bar plots
months_str = monthly_prcp.index.strftime('%Y-%m')
plt.bar(months_str, monthly_prcp.values, color='skyblue', edgecolor='black')
plt.title('Total Monthly Precipitation in NYC in 2024')
plt.xlabel('Month')
plt.ylabel('Precipitation (inches)')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.savefig('total_monthly_prcp.png', dpi=150, bbox_inches='tight')
plt.close()
# Plot a histogram of daily maximum temperatures
plt.figure(figsize=(10, 5))
plt.hist(df['tmax'], bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
plt.title('Distribution of Daily Maximum Temperatures in NYC in 2024')
plt.xlabel('Maximum Temperature (F)')
plt.ylabel('Frequency')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.savefig('tmax_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

print("Plots generated successfully!")
