import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
from matplotlib.cm import viridis


def main():
    # Load the STL file
    your_mesh = mesh.Mesh.from_file(
        "/Users/bmarafino/Downloads/gracewindale_dragon-flat-butt.stl"
    )

    # Calculate the center of the mesh
    center = np.mean(your_mesh.points.reshape(-1, 9), axis=0).reshape(3, 3).mean(axis=0)

    # Calculate bounds for the plot
    x_range = [np.min(your_mesh.x), np.max(your_mesh.x)]
    y_range = [np.min(your_mesh.y), np.max(your_mesh.y)]
    z_range = [np.min(your_mesh.z), np.max(your_mesh.z)]

    # Define the figure and axis for animation
    fig, ax = plt.subplots()
    ax.set_xlim([x_range[0] - 30, x_range[1] + 30])
    ax.set_ylim([y_range[0] - 30, y_range[1] + 30])
    ax.set_aspect("equal")
    ax.axis("off")

    lines = [ax.plot([], [], "-", lw=2)[0] for _ in range(len(your_mesh.vectors))]

    # Color normalization setup
    norm = Normalize(vmin=0, vmax=len(your_mesh.vectors))

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        angle = np.radians(frame)
        rotation_x = np.array(
            [
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ]
        )
        rotation_y = np.array(
            [
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ]
        )

        rotation_matrix = np.dot(rotation_x, rotation_y)

        # Rotate and project each triangle in the mesh
        for i, (line, vector) in enumerate(zip(lines, your_mesh.vectors)):
            # Shift to center, rotate, shift back
            vector = vector - center
            rotated_vector = np.dot(vector, rotation_matrix) + center

            # Perspective projection
            distance = 300  # Distance from the camera
            perspective_scale = distance / (distance - rotated_vector[:, 2])
            xs = rotated_vector[:, 0] * perspective_scale
            ys = rotated_vector[:, 1] * perspective_scale

            line.set_data(xs, ys)
            line.set_color(viridis(norm(i)))  # Assign unique color

        return lines

    ani = FuncAnimation(
        fig, update, init_func=init, frames=np.arange(0, 360, 2), interval=50, blit=True
    )
    plt.show()


if __name__ == "__main__":
    main()
