# Epidemic Simulation Report

## SIR Model

### Erdos-Renyi Graph
*   Initial rapid increase in infected individuals.
*   Peak infection reached, followed by a steady decline as individuals recover.
*   The susceptible population decreases as individuals become infected, eventually stabilizing at a certain level.
*   The recovered population steadily increases.

### Barabasi-Albert Graph
*   Even more rapid increase in infected individuals, peaking earlier and higher than in Erdos-Renyi.
*   A faster decline in infected individuals as immunity spreads quickly through highly connected nodes.
*   The susceptible population drops very quickly, indicating a more efficient spread of the disease.

## SIS Model

### Erdos-Renyi Graph
*   The infected population fluctuates significantly, sometimes reaching a high proportion of the total population, then decreasing, but never fully recovering.
*   The susceptible population mirrors the infected population, as recovered individuals immediately become susceptible again.
*   This suggests an endemic state where the disease persists in the population.

### Barabasi-Albert Graph
*   The infected population also fluctuates, but often reaches higher peaks and maintains a higher average level of infection compared to the Erdos-Renyi graph.
*   The susceptible population drops to very low levels quickly, indicating widespread infection due to the highly connected nature of the graph.
*   The disease becomes endemic and highly prevalent in this network structure.
