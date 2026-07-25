import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractalis_oneiricus_zoom_pan import FractalisOneiricus
from fractalis_oneiricus_julia_explorer import JuliaExplorer
from matplotlib.animation import FuncAnimation

def execute_script():
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    fractalis = FractalisOneiricus(fig, ax[0])
    julia_explorer = JuliaExplorer(fig, ax[1])
    
    plt.savefig('fractalis_oneiricus.png')

if __name__ == "__main__":
    execute_script()