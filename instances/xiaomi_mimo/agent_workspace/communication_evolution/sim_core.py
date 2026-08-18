"""
Communication Evolution - Core Simulation
Agents forage while avoiding predators. They can evolve signaling systems.
"""
import numpy as np
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

random.seed(42)
np.random.seed(42)

NGEN = 300
POP_SIZE = 60
PRED_POP = 2
WORLD_SIZE = 100
N_RESOURCE_PATCHES = 12
N_SIGNAL_CHANNELS = 5
MAX_AGENTS = 150
REPRO_ENERGY = 65
REPRO_AGE_MIN = 3

class World:
    def __init__(self):
        self.resources = []
        self.generate_resources()
        self.time = 0
        self.total_food = 0
        self.total_kills = 0

    def generate_resources(self):
        self.resources = []
        for _ in range(N_RESOURCE_PATCHES):
            x = random.uniform(5, WORLD_SIZE - 5)
            y = random.uniform(5, WORLD_SIZE - 5)
            quality = random.uniform(0.5, 1.0)
            regen = random.uniform(0.3, 0.8)
            cur = quality * 5
            self.resources.append({'x': x, 'y': y, 'quality': quality,
                                   'regen': regen, 'cur': cur, 'mx': quality * 10})

    def regenerate(self):
        for r in self.resources:
            r['cur'] = min(r['mx'], r['cur'] + r['regen'] * 0.5)

    def nearest_resource(self, x, y):
        best, bd = None, float('inf')
        for r in self.resources:
            d = np.sqrt((x - r['x'])**2 + (y - r['y'])**2)
            if d < bd:
                bd = d
                best = r
        return best, bd

class Agent:
    def __init__(self, x=None, y=None, genes=None):
        self.x = x if x is not None else random.uniform(0, WORLD_SIZE)
        self.y = y if y is not None else random.uniform(0, WORLD_SIZE)
        self.energy = 60.0
        self.age = 0
        self.alive = True
        self.food_collected = 0
        self.speed = random.uniform(1.5, 3.5)
        self.perception = random.uniform(12.0, 35.0)
        if genes is not None:
            self.genes = {k: v.copy() for k, v in genes.items()}
        else:
            self.genes = {
                'sig_w': np.random.randn(4, N_SIGNAL_CHANNELS) * 0.5,
                'resp_w': np.random.randn(N_SIGNAL_CHANNELS, 3) * 0.5,
            }
        self.cur_signal = None
        self.danger_level = 0
        self.food_nearby = 0

    def perceive(self, world, predators):
        min_pd = float('inf')
        for p in predators:
            d = np.sqrt((self.x - p.x)**2 + (self.y - p.y)**2)
            if d < min_pd:
                min_pd = d
        self.danger_level = max(0, 1.0 - min_pd / self.perception) if min_pd < self.perception else 0
        _, rd = world.nearest_resource(self.x, self.y)
        self.food_nearby = max(0, 1.0 - rd / self.perception) if rd < self.perception else 0

    def gen_signal(self):
        sv = np.array([self.energy/100.0, self.danger_level, self.food_nearby, min(self.age/50.0, 1.0)])
        self.cur_signal = np.tanh(sv @ self.genes['sig_w'])
        return self.cur_signal

    def respond(self, nearby_sigs):
        if not nearby_sigs:
            return np.zeros(3)
        total_b = np.zeros(3)
        tw = 0
        for sig, dist in nearby_sigs:
            w = 1.0 / (1.0 + dist * 0.1)
            b = np.tanh(sig @ self.genes['resp_w'])
            total_b += b * w
            tw += w
        return total_b / tw if tw > 0 else total_b

    def move(self, bmod, world, predators):
        res, rd = world.nearest_resource(self.x, self.y)
        dx, dy = 0.0, 0.0
        if self.danger_level > 0.3:
            for p in predators:
                d = np.sqrt((self.x - p.x)**2 + (self.y - p.y)**2)
                if d < self.perception and d > 0:
                    fs = (1.0 - d / self.perception) * (1 + bmod[0])
                    dx += (self.x - p.x) / d * fs
                    dy += (self.y - p.y) / d * fs
        elif res and rd < self.perception and rd > 0:
            ast = (1.0 - rd / self.perception) * (1 + bmod[1])
            dx += (res['x'] - self.x) / rd * ast
            dy += (res['y'] - self.y) / rd * ast
        else:
            a = random.uniform(0, 2*np.pi)
            dx, dy = np.cos(a)*0.5, np.sin(a)*0.5
        mag = np.sqrt(dx**2 + dy**2)
        if mag > 0:
            dx, dy = dx/mag*self.speed, dy/mag*self.speed
        self.x = np.clip(self.x + dx, 0, WORLD_SIZE)
        self.y = np.clip(self.y + dy, 0, WORLD_SIZE)

    def try_forage(self, world):
        for r in world.resources:
            d = np.sqrt((self.x - r['x'])**2 + (self.y - r['y'])**2)
            if d < 3.0 and r['cur'] > 0:
                amt = min(2.0, r['cur'])
                r['cur'] -= amt
                self.energy += amt * 8
                self.food_collected += amt
                world.total_food += amt
                return True
        return False

    def metabolize(self):
        self.energy -= 0.15 + self.speed * 0.05
        self.age += 1
        if self.energy <= 0:
            self.alive = False

    def can_reproduce(self):
        return self.alive and self.energy > REPRO_ENERGY and self.age > REPRO_AGE_MIN

    def reproduce(self):
        child_genes = {}
        for k in self.genes:
            child_genes[k] = self.genes[k] + np.random.randn(*self.genes[k].shape) * 0.1
        c = Agent(self.x + random.gauss(0, 2), self.y + random.gauss(0, 2), child_genes)
        c.energy = self.energy * 0.4
        self.energy *= 0.55
        return c

class Predator:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else random.uniform(0, WORLD_SIZE)
        self.y = y if y is not None else random.uniform(0, WORLD_SIZE)
        self.speed = 1.5
        self.hunt_range = 15.0
        self.energy = 50.0
        self.alive = True

    def move_toward(self, agents):
        alive_ag = [a for a in agents if a.alive]
        if not alive_ag:
            a = random.uniform(0, 2*np.pi)
            self.x += np.cos(a)*self.speed
            self.y += np.sin(a)*self.speed
        else:
            nearest = min(alive_ag, key=lambda a: (self.x-a.x)**2+(self.y-a.y)**2)
            d = np.sqrt((self.x-nearest.x)**2+(self.y-nearest.y)**2)
            if d > 0:
                self.x += (nearest.x-self.x)/d*self.speed
                self.y += (nearest.y-self.y)/d*self.speed
        self.x = np.clip(self.x, 0, WORLD_SIZE)
        self.y = np.clip(self.y, 0, WORLD_SIZE)
        self.energy -= 0.5
        if self.energy <= 0:
            self.alive = False

    def hunt(self, agents):
        alive_ag = [a for a in agents if a.alive]
        if not alive_ag:
            return None
        nearest = min(alive_ag, key=lambda a: (self.x-a.x)**2+(self.y-a.y)**2)
        d = np.sqrt((self.x-nearest.x)**2+(self.y-nearest.y)**2)
        if d < self.hunt_range:
            prob = max(0, 1.0 - d/self.hunt_range) * 0.15
            if random.random() < prob:
                nearest.alive = False
                self.energy += 30
                return nearest
        return None

print("Core classes defined OK")
