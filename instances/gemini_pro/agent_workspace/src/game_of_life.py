import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys

def read_initial_state(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        grid = np.array([[int(c) * 255 for c in line.strip().split()] for line in lines])
    return grid

def update(frameNum, img, grid, N):
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            total = int((grid[i, (j - 1) % N] + grid[i, (j + 1) % N] + 
                         grid[(i - 1) % N, j] + grid[(i + 1) % N, j] + 
                         grid[(i - 1) % N, (j - 1) % N] + grid[(i - 1) % N, (j + 1) % N] + 
                         grid[(i + 1) % N, (j - 1) % N] + grid[(i + 1) % N, (j + 1) % N]) / 255)
            if grid[i, j] == 255:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = 0
            else:
                if total == 3:
                    newGrid[i, j] = 255
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,

if __name__ == "__main__":
    N = 100
    if len(sys.argv) > 1:
        initial_state_file = sys.argv[1]
        grid = read_initial_state(initial_state_file)
        N = grid.shape[0]
    else:
        grid = np.zeros((N, N))

    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N), frames=10, interval=50, save_count=50)

    ani.save('src/game_of_life.gif', writer='pillow', fps=10)

    print("Game of Life simulation complete. Saved to src/game_of_life.gif")
