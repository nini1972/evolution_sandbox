import pandas as pd

def collatz_sequence(n):
    sequence = [n]
    max_value = n
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        if n > max_value:
            max_value = n
        steps += 1
    return sequence, steps, max_value

def analyze_range(start, end):
    results = []
    for i in range(start, end + 1):
        _, steps, max_value = collatz_sequence(i)
        results.append({'Starting Number': i, 'Stopping Time': steps, 'Max Value': max_value})
    return pd.DataFrame(results)

if __name__ == "__main__":
    start_num = 1
    end_num = 1000
    print(f"Analyzing Collatz sequences from {start_num} to {end_num}...")
    df = analyze_range(start_num, end_num)
    output_filename = f'collatz_analysis_{start_num}_to_{end_num}.csv'
    df.to_csv(output_filename, index=False)
    print(f"Analysis complete. Data saved to {output_filename}")
