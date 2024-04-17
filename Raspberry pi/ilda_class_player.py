import matplotlib.pyplot as plt
from svgpathtools import svg2paths
from tkinter import filedialog
import tkinter as tk
import numpy as np


def transform_to_fit(point, min_dim, max_dim):
    # Transform a point from SVG dimensions to 4096 x 4096 dimensions
    scale = 4096 / (max_dim - min_dim)
    return (point - min_dim) * scale


def check_distance(points, new_point, min_dist=40):
    # Check if new_point is at least min_dist away from all other points
    for point in points:
        if np.linalg.norm(np.array(point[:2]) - np.array(new_point[:2])) < min_dist:
            return False
    return True


def plot_svg(svg_file):
    # Load SVG file, extract paths and attributes
    paths, attributes = svg2paths(svg_file)

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

    points = []  # Store transformed points with color
    colors = []  # Store colors for plotting
    for path, attr in zip(paths, attributes):
        samples = [path.point(t / 1000.0) for t in range(1001)]
        x = [transform_to_fit(point.real, min_x, max_x) for point in samples]
        y = [-transform_to_fit(-point.imag, min_y, max_y) for point in samples]

        # Extract color (assuming stroke is used for color)
        color = attr["stroke"] if "stroke" in attr else "#000000"
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

        for xi, yi in zip(x, y):
            new_point = (xi, yi, 0, r, g, b)  # z-coordinate is 0 for 2D SVG
            if check_distance(points, new_point):
                points.append(new_point)
                colors.append(
                    (r / 255, g / 255, b / 255)
                )  # Normalize colors for matplotlib

    # Plot points
    x_points = [p[0] for p in points]
    y_points = [p[1] for p in points]
    plt.scatter(x_points, y_points, c=colors, s=10)  # s is the size of the point
    plt.title("Points from SVG with Minimum Distance")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.show()

    # Save points to a file or further process
    # Example: Save to CSV or print points
    print(points[:10])  # Print first 10 points for verification


# Set up the main application window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Call the function using a file dialog to select an SVG file
plot_svg(filedialog.askopenfilename())

# Start the Tkinter event loop
root.mainloop()
