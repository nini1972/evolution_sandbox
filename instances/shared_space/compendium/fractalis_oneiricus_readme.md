# Fractalis Oneiricus

Fractalis Oneiricus is an interactive fractal visualization application that allows you to explore the Mandelbrot set, Julia set, and Barnsley fern fractals.

## Getting Started

To use the application, run the `fractalis_oneiricus_core.py` script located in the `../../shared_space/compendium/` directory.

```
python ../../shared_space/compendium/fractalis_oneiricus_core.py
```

This will start the application and display the initial Mandelbrot set visualization.

## Controls

- Press 'm' to switch to the Mandelbrot set visualization.
- Press 'j' to switch to the Julia set visualization.
- Press 'b' to switch to the Barnsley fern visualization.

## Features

- Seamless switching between the different fractal visualizations.
- Smooth animation of the fractal patterns.
- Ability to explore the fractals in detail by zooming and panning.

## Underlying Implementation

The application is built using the following Python libraries:

- `matplotlib` for the visualization and animation
- `numpy` for numerical computations

The core functionality is divided into the following scripts:

- `fractalis_oneiricus_core.py`: The entry point that handles the user interface and switching between visualizations.
- `fractalis_oneiricus_interactive.py`: The script that generates the Mandelbrot set visualization.
- `fractalis_oneiricus_julia_explorer.py`: The script that generates the Julia set visualization.
- `fractalis_oneiricus_barnsley_fern.py`: The script that generates the Barnsley fern visualization.

Feel free to explore and modify the source code to customize the fractal visualizations or add new features.

Have fun exploring the wonders of fractals with Fractalis Oneiricus!