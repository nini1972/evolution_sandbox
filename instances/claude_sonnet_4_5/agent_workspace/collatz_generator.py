import pandas as pd

def generate_collatz_sequence(n):
    """
    Generates a Collatz sequence for a given starting number.
    Args:
        n (int): The starting positive integer.
    Returns:
        tuple: A tuple containing the Collatz sequence (list), stopping time (int),
               and maximum value (int).
    """
    if n <= 0:
        raise ValueError("Starting number must be a positive integer.")
    
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    
    stopping_time = len(sequence) - 1
    max_value = max(sequence)
    
    return sequence, stopping_time, max_value

def analyze_collatz_range(start, end):
    """
    Analyzes Collatz sequences for a range of starting numbers.
    Args:
        start (int): The starting number of the range (inclusive).
        end (int): The ending number of the range (inclusive).
    Returns:
        pd.DataFrame: A DataFrame containing the starting number, stopping time,
                      and maximum value for each number in the range.
    """
    data = []
    for i in range(start, end + 1):
        _, stopping_time, max_value = generate_collatz_sequence(i)
        data.append({'Starting Number': i, 'Stopping Time': stopping_time, 'Max Value': max_value})
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Example usage:
    starting_number = 6
    sequence, stopping_time, max_value = generate_collatz_sequence(starting_number)
    
    print(f"Collatz sequence for {starting_number}: {sequence}")
    print(f"Stopping time: {stopping_time}")
    print(f"Maximum value: {max_value}")

    print("\nAnalyzing Collatz sequences for numbers 1 to 100...")
    df_results = analyze_collatz_range(1, 100)
    print(df_results.head())
    
    output_filename = "collatz_analysis_1_to_100.csv"
    df_results.to_csv(output_filename, index=False)
    print(f"Results saved to {output_filename}")

    # For a larger range
    print("\nAnalyzing Collatz sequences for numbers 1 to 1000...")
    df_results_large = analyze_collatz_range(1, 1000)
    output_filename_large = "collatz_analysis_1_to_1000.csv"
    df_results_large.to_csv(output_filename_large, index=False)
    print(f"Results saved to {output_filename_large}")