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

## SEIR Model

### Erdos-Renyi Graph
*   Introduction of an 'Exposed' (E) compartment, leading to a delay between infection and infectiousness.
*   The 'E' population rises and falls before the 'I' population peaks.
*   The overall curve for 'I' and 'R' populations resembles the SIR model, but with a slight delay due to the 'E' state.

### Barabasi-Albert Graph
*   The 'Exposed' and 'Infected' populations rise and fall very rapidly, characteristic of the fast spread on scale-free networks.
*   The susceptible population is quickly depleted.
*   The delay introduced by the 'E' state is present but the overall dynamics are still dominated by the network structure, leading to a rapid epidemic.

## SIRS Model

### Erdos-Renyi Graph
*   The 'Recovered' population can return to the 'Susceptible' state, leading to recurring waves of infection.
*   The 'Infected' population might not die out completely, potentially leading to endemic behavior with oscillations.
*   The 'Susceptible' population can increase again after an initial drop, providing new hosts for the disease.

### Barabasi-Albert Graph
*   Similar to the Erdos-Renyi graph, but with more pronounced fluctuations and higher peak infections.
*   The disease persists more easily due to the combination of waning immunity and the highly connected nature of the network, leading to sustained endemicity.
*   The cycles of infection and recovery are more rapid and intense.
