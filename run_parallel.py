import os
import time
import argparse
from engine import run_loop

def main():
    parser = argparse.ArgumentParser(description="Run multiple agent instances in alternating turns")
    parser.add_argument("--instances", type=str, default="gemini_flash,claude_sonnet_4_5", help="Comma-separated list of instance names")
    parser.add_argument("--ticks", type=int, default=3, help="Number of turns for each instance")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between turns")
    args = parser.parse_args()

    instances = [i.strip() for i in args.instances.split(",") if i.strip()]
    
    print(f"Starting parallel evolution sandbox for instances: {instances}")
    print(f"Running for {args.ticks} global ticks...")

    # Ensure all listed instances exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for instance in instances:
        instance_dir = os.path.join(base_dir, "instances", instance)
        if not os.path.exists(instance_dir):
            print(f"Error: Instance '{instance}' does not exist at {instance_dir}.")
            print(f"Please run 'python setup_instance.py --name {instance}' first.")
            return

    for tick in range(args.ticks):
        print(f"\n================================================================================")
        print(f"  GLOBAL TURN {tick + 1} / {args.ticks}")
        print(f"================================================================================")
        
        for instance in instances:
            print(f"\n>>> [Executing {instance}] <<<")
            
            # Run exactly 1 tick for the active instance
            run_loop(instance, ticks=1)
            
            # Cool down delay to avoid API rate limits
            time.sleep(args.delay)

    print("\n================================================================================")
    print("Parallel evolution complete.")
    print("Check individual instances' workspaces to see how they evolved:")
    for instance in instances:
        print(f" - instances/{instance}/agent_workspace/")
    print("================================================================================")

if __name__ == "__main__":
    main()
