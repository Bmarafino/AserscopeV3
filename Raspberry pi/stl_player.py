import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
from matplotlib.cm import viridis
import numpy as np


class STLPlayer:
    def __init__(self, stl_file, frames_to_take):
        self.stl_file = stl_file
        self.frames_to_take = frames_to_take
        self.points = []
        self.load_mesh_and_process()
    
    def load_mesh_and_process(self):
        self.mesh = mesh.Mesh.from_file(
            self.stl_file
        )
        self.center = np.mean(self.mesh.points.reshape(-1, 9), axis=0).reshape(3, 3).mean(axis=0)
        self.x_range = [np.min(self.mesh.x), np.max(self.mesh.x)]
        self.y_range = [np.min(self.mesh.y), np.max(self.mesh.y)]
        self.z_range = [np.min(self.mesh.z), np.max(self.mesh.z)]

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim([self.x_range[0] - 30, self.x_range[1] + 30])
        self.ax.set_ylim([self.y_range[0] - 30, self.y_range[1] + 30])
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        self.lines = [self.ax.plot([], [], "-", lw=2)[0] for _ in range(len(self.mesh.vectors))]

        # Color normalization setup
        self.norm = Normalize(vmin=0, vmax=len(self.mesh.vectors))
    
    def init_lines(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines
    
    def update(self, frame):
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
        for i, (line, vector) in enumerate(zip(self.lines, self.mesh.vectors)):
            # Shift to center, rotate, shift back
            vector = vector - self.center
            rotated_vector = np.dot(vector, rotation_matrix) + self.center

            # Perspective projection
            distance = 300  # Distance from the camera
            perspective_scale = distance / (distance - rotated_vector[:, 2])
            xs = rotated_vector[:, 0] * perspective_scale
            ys = rotated_vector[:, 1] * perspective_scale

            line.set_data(xs, ys)
            line.set_color(viridis(self.norm(i)))  # Assign unique color

        return self.lines
    def animate(self):
        ani = FuncAnimation(
            self.fig, self.update, init_func=self.init_lines, frames=np.arange(0, 360, 2), interval=50, blit=True
    )
        plt.show()
    def get_frame_data(self):
        all_frames = []
        all_xs = []
        all_ys = []

        # Collect all rotated and projected x, y coordinates to determine min and max
        for frame in np.linspace(0, 360, self.frames_to_take, endpoint=False):
            angle = np.radians(frame)
            rotation_x = np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ])
            rotation_y = np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ])

            rotation_matrix = np.dot(rotation_x, rotation_y)

            for vector in self.mesh.vectors:
                vector = vector - self.center
                rotated_vector = np.dot(vector, rotation_matrix) + self.center
                distance = 300
                perspective_scale = distance / (distance - rotated_vector[:, 2])
                xs = rotated_vector[:, 0] * perspective_scale
                ys = rotated_vector[:, 1] * perspective_scale

                all_xs.extend(xs)
                all_ys.extend(ys)

        # Find the overall min and max
        min_x, max_x = min(all_xs), max(all_xs)
        min_y, max_y = min(all_ys), max(all_ys)

        # Define a function to normalize the coordinates
        def normalize(value, min_val, max_val):
            return int(((value - min_val) / (max_val - min_val)) * 4096)

        # Now create frames with normalized coordinates
        for frame in np.linspace(0, 360, self.frames_to_take, endpoint=False):
            angle = np.radians(frame)
            rotation_matrix = np.dot(rotation_x, rotation_y)
            point_count = 0

            for i, vector in enumerate(self.mesh.vectors):
                vector = vector - self.center
                rotated_vector = np.dot(vector, rotation_matrix) + self.center
                distance = 300
                perspective_scale = distance / (distance - rotated_vector[:, 2])
                xs = rotated_vector[:, 0] * perspective_scale
                ys = rotated_vector[:, 1] * perspective_scale

                # Normalize the coordinates
                xs = [normalize(x, min_x, max_x) for x in xs]
                ys = [normalize(y, min_y, max_y) for y in ys]

                # Assigning colors based on vertex index mod 3 and mapping to 1, 2, 4
                colors = {0: 1, 1: 2, 2: 4}
                color = colors[i % 3]  # Use modulus to cycle through 1, 2, 4 for the three vertices

                # Add the points to the all_frames list
                for x, y in zip(xs, ys):
                    if point_count >= 5000:
                        # Add the ending tuple (0, 0, 0)
                        all_frames.append((0, 0, 0))
                        point_count = 0
                    all_frames.append((x, y, color))
                    point_count += 1

            # Add the ending tuple (0, 0, 0) to mark the end of a frame
            all_frames.append((0, 0, 0))

        return all_frames



if __name__ == "__main__":
    p1 = STLPlayer("D:/zachm/Downloads/20mm_cube.STL", 40)
    p1.animate()
    frames = p1.get_frame_data()
    print(frames)
