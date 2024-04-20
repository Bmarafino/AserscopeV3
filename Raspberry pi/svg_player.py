import matplotlib.pyplot as plt
from svgpathtools import svg2paths
from tkinter import filedialog
import tkinter as tk
import numpy as np
import random


class SVGPlotter:
    def __init__(self, svg_file, minDistance=40):
        self.svg_file = svg_file
        self.minDistance = minDistance
        self.points = []  # Stores transformed points with color and laser info
        self.load_and_process_svg()

    def transform_to_fit(self, point, min_dim, max_dim):
        # Transform a point from SVG dimensions to 4096 x 4096 dimensions
        scale = 4096 / (max_dim - min_dim)
        return (point - min_dim) * scale

    def check_distance(self, new_point, min_dist=40):
        # Check if new_point is at least min_dist away from all other points
        for point in self.points:
            if np.linalg.norm(np.array(point[:2]) - np.array(new_point[:2])) < min_dist:
                return False
        return True

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

        for path, attr in zip(paths, attributes):
            samples = [path.point(t / 1000.0) for t in range(1001)]
            x = [self.transform_to_fit(point.real, min_x, max_x) for point in samples]
            y = [
                4096 + self.transform_to_fit(-point.imag, min_y, max_y)
                for point in samples
            ]

            # Assign random color index 1, 3, or 4 to the stroke
            color_index = random.choice([1, 3, 4])

            # Append the first point with laser off before starting the stroke
            if x and y:
                first_point = (x[0], y[0], 0)  # Add with laser off
                self.points.append(first_point)

            for xi, yi in zip(x, y):
                new_point = (xi, yi, color_index)
                if self.check_distance(new_point, self.minDistance):
                    self.points.append(new_point)

    def get_points(self):
        # Return points data
        return self.points

    def plot_svg(self):
        # Plot points using matplotlib
        x_points = [p[0] for p in self.points]
        y_points = [p[1] for p in self.points]
        colors = [
            "red" if p[2] == 1 else "green" if p[2] == 3 else "blue"
            for p in self.points
        ]
        plt.scatter(x_points, y_points, c=colors, s=10)  # s is the size of the point
        plt.title("Points from SVG with Minimum Distance and Laser Color")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.show()


# Usage
# root = tk.Tk()
# root.withdraw()  # Hide the main window

# file_path = filedialog.askopenfilename()  # Ask user to select an SVG file
# if file_path:
#   plotter = SVGPlotter(file_path, 200)
#  plotter.plot_svg()

# root.mainloop()
