import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractalis_oneiricus_zoom_pan import FractalisOneiricus
from matplotlib.animation import FuncAnimation

def execute_script():
    fig, ax = plt.subplots(figsize=(8, 6))
    fractalis = FractalisOneiricus(fig, ax)
    plt.savefig('fractalis_oneiricus.png')

if __name__ == "__main__":
    execute_script()