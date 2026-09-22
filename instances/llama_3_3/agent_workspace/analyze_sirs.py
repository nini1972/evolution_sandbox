
import json
import matplotlib.pyplot as plt
import pandas as pd

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

def plot_sirs_data(file_path, title_suffix):
    with open(file_path, 'r') as f:
        data = json.load(f)

    history = data['history']
    df = pd.DataFrame(history)

    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['S'], label='Susceptible')
    plt.plot(df.index, df['I'], label='Infected')
    plt.plot(df.index, df['R'], label='Recovered')
    plt.xlabel('Time Steps')
    plt.ylabel('Number of Individuals')
    plt.title(f'SIRS Model on {title_suffix} Graph')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'sirs_plot_{title_suffix.lower().replace(" ", "_")}.png')
    plt.close()

if __name__ == "__main__":
    plot_sirs_data('sirs_history_erdos_renyi.json', 'Erdos-Renyi')
    plot_sirs_data('sirs_history_barabasi_albert.json', 'Barabasi-Albert')
