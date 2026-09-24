import imageio.v2 as imageio
import os

def create_gif_from_pngs(input_dir="gol_frames_png", output_filename="game_of_life_animation.gif", duration=0.1):
    """Creates a GIF from a series of PNG images."""
    png_files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.png')])

    if not png_files:
        print(f"No PNG files found in {input_dir}.")
        return

    print(f"Creating GIF from {len(png_files)} PNG files...")
    with imageio.get_writer(output_filename, mode='I', duration=duration) as writer:
        for filename in png_files:
            image = imageio.imread(filename)
            writer.append_data(image)
    print(f"GIF saved as {output_filename}")

if __name__ == "__main__":
    create_gif_from_pngs()
