import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

def simulate_synchronization(G, K, theta0, omega, t_max, dt):
    t = np.arange(0, t_max, dt)
    theta = np.zeros((len(t), len(G.nodes)))
    theta[0] = theta0
    for i in range(1, len(t)):
        for j in range(len(G.nodes)):
            neighbors = list(G.neighbors(j))
            theta[i, j] = theta[i-1, j] + (omega[j] + K/len(neighbors)*np.sum(np.sin(theta[i-1, neighbors] - theta[i-1, j])))*dt
    return t, theta

G = nx.erdos_renyi_graph(100, 0.1)
K = 0.5
theta0 = np.random.uniform(0, 2*np.pi, len(G.nodes))
omega = np.random.normal(0, 1, len(G.nodes))
t_max = 10.0
dt = 0.01

t, theta = simulate_synchronization(G, K, theta0, omega, t_max, dt)

plt.figure(figsize=(10, 6))
plt.plot(t, np.mean(np.sin(theta), axis=1), label='Average sine')
plt.plot(t, np.mean(np.cos(theta), axis=1), label='Average cosine')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Average value')
plt.title('Synchronization in Complex Network')
plt.savefig('synchronization_complex_network_plot.png')