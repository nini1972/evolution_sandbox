#!/usr/bin/env python3
import numpy as np
import json
from ecosystem import Ecosystem
from visualize import plot_ecosystem_history

def run_simulation(generations=200, initial_population=50, max_resources=100):
    print('Initializing ecosystem...')
    eco = Ecosystem(initial_population, max_resources)
    
    print(f'Running simulation for {generations} generations...')
    for gen in range(generations):
        eco.competition_round()
        eco.reproduction_phase()
        eco.record_history()
        
        if gen % 20 == 0:
            alive = sum(1 for o in eco.organisms if o.alive)
            print(f'Gen {gen}: Population={alive}, Resources={eco.resources.amount:.1f}')
    
    print('Simulation complete!')
    return eco.history

if __name__ == '__main__':
    history = run_simulation()
    
    print('Generating visualization...')
    plot_ecosystem_history(history, 'ecosystem_evolution.png')
    
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=2)
    print('History saved to history.json')