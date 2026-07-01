import random
import time

def inject_noise(data_stream):
    """Injects high entropy noise into a data stream."""
    return [x + random.uniform(-1, 1) for x in data_stream]

if __name__ == "__main__":
    # Simulate a baseline data structure
    base = [i for i in range(100)]
    noisy = inject_noise(base)
    
    with open("entropy_log.txt", "a") as f:
        f.write(f"Entropy Injected at {time.time()}: {noisy[:10]}...\n")
    print("Entropy injected.")
