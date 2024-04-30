import matplotlib.pyplot as plt
from svgpathtools import svg2paths
import tkinter as tk
from tkinter import filedialog
import numpy as np
import random


class SVGPlotter:
    def __init__(self, svg_file, numberOfsample):
        self.svg_file = svg_file
        self.numberOfSamples = numberOfsample
        self.points = []  # Stores transformed points with color and laser info
        self.total = 0
        self.load_and_process_svg()

    def transform_to_fit(self, point, min_dim, max_dim):
        # Transform a point from SVG dimensions to 4096 x 4096 dimensions
        scale = 4096 / (max_dim - min_dim)
        transformed_point = (point - min_dim) * scale
        # Clamp the coordinates to be within 0 to 4096
        return max(0, min(4096, transformed_point))

    def generate_points_with_fixed_spacing(self, A, B, laser, spacing):
        x1, y1 = A
        x2, y2 = B
        dx = x2 - x1
        dy = y2 - y1
        line_length = np.sqrt(dx**2 + dy**2)
        n = max(int(np.ceil(line_length / spacing)), 2)  # Ensure at least two points
        t = np.linspace(0, 1, n)
        x = x1 + t * dx
        y = y1 + t * dy
        points = np.column_stack((x, y, np.full_like(x, laser)))
        return points

    def load_and_process_svg(self):
        # Load SVG file, extract paths and attributes
        paths, attributes = svg2paths(self.svg_file)

        # Find bounds for rescaling
        min_x, max_x, min_y, max_y = (
            float("inf"),
            float("-inf"),
            float("inf"),
            float("-inf"),
        )

        for path in paths:
            for seg in path:
                bbox = seg.bbox()
                min_x, max_x = min(min_x, bbox[0]), max(max_x, bbox[1])
                min_y, max_y = min(min_y, bbox[2]), max(max_y, bbox[3])
            self.total = self.total + path.length()
            print("total" + str(self.total))

        for path in paths:
            # path = paths[0]
            tmpSamples = self.numberOfSamples * (path.length() / self.total)
            samples = [path.point(t / tmpSamples) for t in range(int(tmpSamples) + 1)]
            samples.append(path.point(1))
            samples.append(path.point(0))
            x = [self.transform_to_fit(point.real, min_x, max_x) for point in samples]
            y = [
                4096 - self.transform_to_fit(point.imag, min_y, max_y)
                for point in samples
            ]  # Fixed the transformation for Y
            self.points.append((x[0], y[0], 6))
            color_index = random.choice([1, 2, 4])
            # Assign random color index 1, 2, or 4 to the stroke
            for i in zip(x, y):
                self.points.append((i[0], i[1], color_index))
            # Append the first point with laser off before starting the stroke
            if x and y:
                first_point = (x[-1], y[-1], 6)  # Add with laser off
                self.points.append(first_point)

    def get_points(self):
        # Return points data
        return self.points

    def plot_svg(self):
        # Plot points using matplotlib
        x_points = [p[0] for p in self.points]
        y_points = [p[1] for p in self.points]
        colors = [
            (
                "red"
                if p[2] == 1
                else (
                    "green"
                    if p[2] == 2
                    else "blue" if p[2] == 4 else "orange" if p[2] == 6 else "yellow"
                )
            )
            for p in self.points
        ]
        plt.figure(
            figsize=(10, 8)
        )  # Optional: Adjust figure size for better visibility
        for i, (x, y, color) in enumerate(zip(x_points, y_points, colors)):
            plt.scatter(x, y, color=color, s=10)  # s is the size of the point
            plt.text(
                x, y, str(i + 1), color="black", fontsize=8
            )  # Adding text annotation

        plt.title("Points from SVG with Minimum Distance and Laser Color")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.show()


# Usage example (commented to prevent accidental execution)
# root = tk.Tk()
# root.withdraw()  # Hide the main window
# file_path = filedialog.askopenfilename()  # Ask user to select an SVG file
# if file_path:
#     plotter = SVGPlotter(file_path, 200)
#     plotter
