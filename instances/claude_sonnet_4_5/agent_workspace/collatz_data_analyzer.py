import pandas as pd

def analyze_collatz_data(filepath):
    """
    Reads Collatz data from a CSV file and performs statistical analysis.
    Identifies numbers with unusually high stopping times or maximum values.
    Args:
        filepath (str): The path to the CSV file containing Collatz analysis data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    print(f"\n--- Analysis for {filepath} ---")

    # Statistical Analysis
    print("\n1. Statistical Summary for Stopping Time:")
    print(df['Stopping Time'].describe())

    print("\n2. Statistical Summary for Max Value:")
    print(df['Max Value'].describe())

    # Outlier Detection (Top 1%)
    top_percentile_stopping_time = df['Stopping Time'].quantile(0.99)
    outliers_stopping_time = df[df['Stopping Time'] >= top_percentile_stopping_time].sort_values(by='Stopping Time', ascending=False)
    print(f"\n3. Top 1% of Starting Numbers by Stopping Time (>= {top_percentile_stopping_time:.2f}):")
    print(outliers_stopping_time[['Starting Number', 'Stopping Time', 'Max Value']].head(10))

    top_percentile_max_value = df['Max Value'].quantile(0.99)
    outliers_max_value = df[df['Max Value'] >= top_percentile_max_value].sort_values(by='Max Value', ascending=False)
    print(f"\n4. Top 1% of Starting Numbers by Max Value (>= {top_percentile_max_value:.2f}):")
    print(outliers_max_value[['Starting Number', 'Stopping Time', 'Max Value']].head(10))


if __name__ == "__main__":
    data_file = "collatz_analysis_1_to_10000.csv"
    analyze_collatz_data(data_file)
