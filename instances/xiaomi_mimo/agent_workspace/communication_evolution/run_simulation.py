"""Run the communication evolution simulation"""
import sys
sys.path.insert(0, 'communication_evolution')
from sim_core import *

def run_sim():
    world = World()
    agents = [Agent() for _ in range(POP_SIZE)]
    predators = [Predator() for _ in range(PRED_POP)]
    history = []

    for gen in range(NGEN):
        world.time = gen
        world.regenerate()
        signals_this_gen = []

        for a in agents:
            if not a.alive:
                continue
            a.perceive(world, predators)
            sig = a.gen_signal()
            signals_this_gen.append({'id': id(a), 'sig': sig.tolist(),
                                     'danger': a.danger_level, 'food': a.food_nearby,
                                     'x': a.x, 'y': a.y})

        for a in agents:
            if not a.alive:
                continue
            nearby = []
            for s in signals_this_gen:
                if s['id'] == id(a):
                    continue
                d = np.sqrt((a.x-s['x'])**2+(a.y-s['y'])**2)
                if d < a.perception:
                    nearby.append((np.array(s['sig']), d))
            bmod = a.respond(nearby)
            a.move(bmod, world, predators)

        for a in agents:
            if a.alive:
                a.try_forage(world)

        for a in agents:
            if a.alive:
                a.metabolize()

        new_agents = []
        for a in agents:
            if a.can_reproduce() and len(agents)+len(new_agents) < MAX_AGENTS:
                if random.random() < 0.3:
                    new_agents.append(a.reproduce())
        agents.extend(new_agents)
        agents = [a for a in agents if a.alive]

        killed_list = []
        for p in predators:
            if p.alive:
                p.move_toward(agents)
                k = p.hunt(agents)
                if k:
                    killed_list.append(k)
                    world.total_kills += 1

        new_preds = []
        for p in predators:
            if p.alive and p.energy > 80 and len(predators)+len(new_preds) < 8:
                if random.random() < 0.2:
                    c = Predator(p.x+random.gauss(0,3), p.y+random.gauss(0,3))
                    c.energy = p.energy*0.4
                    p.energy *= 0.5
                    new_preds.append(c)
        predators.extend(new_preds)
        predators = [p for p in predators if p.alive]

        n_alive = len(agents)
        n_pred = len([p for p in predators if p.alive])
        avg_e = np.mean([a.energy for a in agents]) if agents else 0

        danger_sigs = []
        food_sigs = []
        if signals_this_gen and len(signals_this_gen) > 2:
            sigs = np.array([s['sig'] for s in signals_this_gen])
            dangers = np.array([s['danger'] for s in signals_this_gen])
            foods = np.array([s['food'] for s in signals_this_gen])
            for ch in range(N_SIGNAL_CHANNELS):
                sig_std = np.std(sigs[:,ch])
                danger_std = np.std(dangers)
                food_std = np.std(foods)
                if sig_std > 1e-8 and danger_std > 1e-8:
                    dc = float(np.corrcoef(dangers, sigs[:,ch])[0,1])
                else:
                    dc = 0
                if sig_std > 1e-8 and food_std > 1e-8:
                    fc = float(np.corrcoef(foods, sigs[:,ch])[0,1])
                else:
                    fc = 0
                if np.isnan(dc): dc = 0
                if np.isnan(fc): fc = 0
                danger_sigs.append(round(dc, 4))
                food_sigs.append(round(fc, 4))

        avg_danger_sig = np.mean([abs(x) for x in danger_sigs]) if danger_sigs else 0
        avg_food_sig = np.mean([abs(x) for x in food_sigs]) if food_sigs else 0

        history.append({
            'gen': gen+1, 'agents': n_alive, 'predators': n_pred,
            'avg_energy': round(float(avg_e), 2),
            'danger_signal_corr': danger_sigs,
            'food_signal_corr': food_sigs,
            'danger_sig_strength': round(float(avg_danger_sig), 4),
            'food_sig_strength': round(float(avg_food_sig), 4),
            'kills': len(killed_list),
        })

        if (gen+1) % 50 == 0:
            print(f"Gen {gen+1:3d}: Agents={n_alive:3d} Pred={n_pred} "
                  f"DangerSig={avg_danger_sig:.3f} FoodSig={avg_food_sig:.3f} "
                  f"Kills={len(killed_list)}")

    return history, agents, predators, world

print("Starting simulation...")
history, agents, predators, world = run_sim()

with open('communication_evolution/history_comm.json', 'w') as f:
    json.dump(history, f)
print("Simulation complete. History saved.")
