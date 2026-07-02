"""
Conway's Game of Life Simulation

This script implements Conway's Game of Life, a cellular automaton devised by the British mathematician John Horton Conway in 1970.

The "game" is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input. One interacts with the Game of Life by creating an initial configuration and observing how it evolves.

Rules:
1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

The universe of the Game of Life is an infinite, two-dimensional orthogonal grid of square cells, each of which is in one of two possible states, live or dead, or "populated" or "unpopulated". Every cell interacts with its eight neighbours, which are the cells that are horizontally, vertically, or diagonally adjacent.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class GameOfLife:
    def __init__(self, size=(50, 50), init_pattern='random'):
        self.size = size
        self.board = self._initialize_board(init_pattern)

    def _initialize_board(self, pattern):
        if pattern == 'random':
            return np.random.choice([0, 1], size=self.size, p=[0.7, 0.3])
        elif pattern == 'glider':
            board = np.zeros(self.size, dtype=int)
            board[1, 2] = 1
            board[2, 3] = 1
            board[3, 1:4] = 1
            return board
        # Add more patterns here

    def _count_neighbors(self, row, col):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                neighbor_row, neighbor_col = (row + i) % self.size[0], (col + j) % self.size[1]
                count += self.board[neighbor_row, neighbor_col]
        return count

    def update(self):
        new_board = np.copy(self.board)
        for row in range(self.size[0]):
            for col in range(self.size[1]):
                neighbors = self._count_neighbors(row, col)
                if self.board[row, col] == 1:  # Live cell
                    if neighbors < 2 or neighbors > 3:
                        new_board[row, col] = 0  # Dies
                else:  # Dead cell
                    if neighbors == 3:
                        new_board[row, col] = 1  # Becomes alive
        self.board = new_board

    def run_animation(self, frames=200, interval=100):
        fig, ax = plt.subplots()
        img = ax.imshow(self.board, cmap='binary', interpolation='nearest')
        ax.set_xticks([])
        ax.set_yticks([])

        def animate(frame):
            self.update()
            img.set_array(self.board)
            return [img]

        ani = animation.FuncAnimation(fig, animate, frames=frames, interval=interval, blit=True)
        plt.show()

if __name__ == "__main__":
    game = GameOfLife(size=(100, 100), init_pattern='random')
    game.run_animation()
