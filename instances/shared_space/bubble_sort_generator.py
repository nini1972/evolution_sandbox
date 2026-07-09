import json
import random

def bubble_sort_with_history(arr):
    n = len(arr)
    history = []
    arr_copy = list(arr)

    history.append(list(arr_copy)) # Initial state

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr_copy[j] > arr_copy[j+1]:
                arr_copy[j], arr_copy[j+1] = arr_copy[j+1], arr_copy[j]
                swapped = True
                history.append(list(arr_copy)) # Record state after each swap
        if not swapped:
            break # If no two elements were swapped by inner loop, array is sorted
    return history

if __name__ == "__main__":
    # Generate a random list of numbers
    SIZE = 50 # Number of elements to sort
    MAX_VALUE = 100 # Maximum value for elements
    random_list = [random.randint(1, MAX_VALUE) for _ in range(SIZE)]

    # Perform bubble sort and record history
    sort_history = bubble_sort_with_history(random_list)

    output_data = {
        "initial_list": random_list,
        "sort_history": sort_history
    }

    with open("bubble_sort_data.json", "w") as f:
        json.dump(output_data, f, indent=4)
