import subprocess
import time
import os

def check_for_innovation(current_score):
    # If the system complexity peaks, trigger a refinement of the biomutator.
    if current_score > 5.0:
        print("Innovation detected! Refining biomutator..")
        with open('simulations/emergence_incubation/biomutator.py', 'a') as f:
            f.write("\n# Refinement from controller: Increased entropy injection.\n")
            f.write("grid = np.random.choice([0, 1], grid.shape, p=[0.9, 0.1]) | grid\n")
        return True
    return False

def run_loop():
    while True:
        subprocess.run(['python3', 'simulations/environment_layer/data_feeder.py'])
        subprocess.run(['python3', 'simulations/emergence_incubation/biomutator.py'])
        result = subprocess.run(['python3', 'analyzer/adaptation_tracker/score_evolution.py'], capture_output=True, text=True)
        
        # Parse score
        try:
            score = float(result.stdout.split(': ')[1])
            check_for_innovation(score)
        except:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    print("Master Controller Initiated with Self-Optimization Protocol.")
    # run_loop() 
