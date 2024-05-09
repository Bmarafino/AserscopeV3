import matplotlib.pyplot as plt
from svgpathtools import svg2paths, Line, QuadraticBezier, CubicBezier
import tkinter as tk
from tkinter import filedialog
import numpy as np
import random
import xml.etree.ElementTree as ET
import cssutils


class SVGPlotter:
    def __init__(self, svg_file, numberOfsample):
        self.svg_file = svg_file
        self.numberOfSamples = numberOfsample
        self.points = []  # Stores transformed points with color and laser info
        self.total = 0
        self.load_and_process_svg()

    def hex_to_rgb(self, hex_color):
        # Remove the '#' if present
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        # Handle short (3-character) hex codes
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)

        # Convert to RGB tuple

        if len(hex_color) != 6:
            return 6
            raise ValueError(f"Expected a hex string of length 6, got '{hex_color}'")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def rgb_to_binary_rgb_int(self, rgb_color):
        try:
            """Map an RGB tuple to the closest binary RGB and return as an integer."""
            binary_rgb_map = {
                "000": (0, 0, 0),  # Black
                "001": (0, 0, 255),  # Blue
                "010": (0, 255, 0),  # Green
                "011": (0, 255, 255),  # Cyan
                "100": (255, 0, 0),  # Red
                "101": (255, 0, 255),  # Magenta
                "110": (255, 255, 0),  # Yellow
                "111": (255, 255, 255),  # White
            }

            def color_distance(c1, c2):
                """Calculate the Euclidean distance between two RGB colors."""
                return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

            # Convert hex to RGB
            original_rgb = self.hex_to_rgb(rgb_color)

            # Find the closest binary RGB color
            closest_binary = None
            min_distance = float("inf")
            for binary, rgb in binary_rgb_map.items():
                distance = color_distance(original_rgb, rgb)
                if distance < min_distance:
                    min_distance = distance
                    closest_binary = binary

            # Convert binary string '111', '110', etc., to an integer
            return int(closest_binary, 2)
        except:
            return 1

    def simple_style_parser(self, style_str):
        styles = {}
        if style_str:
            # Split the style string into individual properties
            items = style_str.split(";")
            for item in items:
                if ":" in item:
                    key, value = item.split(":")
                    styles[key.strip()] = value.strip()
        return styles

    def transform_to_fit(self, point, min_dim, max_dim):
        # Transform a point from SVG dimensions to 4096 x 4096 dimensions
        scale = 4096 / (max_dim - min_dim)
        transformed_point = (point - min_dim) * scale
        # Clamp the coordinates to be within 0 to 4096
        return max(0, min(4096, transformed_point))

    def interpolate_points_distance(self, start, end, distance):
        """Interpolate points along the line between start and end with a given distance between them."""
        dx, dy = end[0] - start[0], end[1] - start[1]
        line_length = np.sqrt(dx**2 + dy**2)
        if line_length < 30:
            return []
        num_points = max(int(line_length / distance), 1)  # Ensure at least one point
        x_vals = np.linspace(start[0], end[0], num_points + 1)
        y_vals = np.linspace(start[1], end[1], num_points + 1)
        return zip(x_vals, y_vals)

    def load_and_process_svg(self):
        paths, attributes = svg2paths(self.svg_file)
        tree = ET.parse(self.svg_file)
        root = tree.getroot()

        # Parse styles using cssutils
        styles = {}
        sheet = cssutils.parseString(ET.tostring(root).decode("utf-8"))
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for selector in rule.selectorList:
                    style = cssutils.css.CSSStyleDeclaration(cssText=rule.style.cssText)
                    styles[selector.selectorText] = {
                        "fill": style.getPropertyValue("fill"),
                        "stroke": style.getPropertyValue("stroke"),
                    }

        min_x, max_x, min_y, max_y = (
            float("inf"),
            float("-inf"),
            float("inf"),
            float("-inf"),
        )

        # Calculate bounds and transformation factors
        for path in paths:
            for segment in path:
                bbox = segment.bbox()
                min_x, max_x = min(min_x, bbox[0]), max(max_x, bbox[1])
                min_y, max_y = min(min_y, bbox[2]), max(max_y, bbox[3])
            self.total += path.length()
        mintot = min(min_x, min_y)
        maxtot = max(max_x, max_y)

        # Process each path, considering fill and stroke
        # Example usage within your SVG parsing loop
        for path, attr in zip(
            paths, root.findall(".//{http://www.w3.org/2000/svg}path")
        ):
            class_attr = attr.get("class", "")
            style_str = attr.get("style", "")
            parsed_styles = self.simple_style_parser(style_str)
            fill_color = parsed_styles.get("fill", None)
            stroke_color = parsed_styles.get("stroke", None)
            if fill_color == None and stroke_color == None:
                class_attr = attr.get("class", "")
                style_attr = attr.get("style", "")
                parsed_style = cssutils.parseStyle(style_attr)
                fill_color = parsed_style.getPropertyValue("fill")
                stroke_color = parsed_style.getPropertyValue("stroke")
            if fill_color == None and stroke_color == None:
                for class_name in class_attr.split():
                    if f".{class_name}" in styles:
                        class_style = styles[f".{class_name}"]
                        fill_color = class_style.get("fill", fill_color)
                        stroke_color = class_style.get("stroke", stroke_color)
                        break
            if fill_color == None and stroke_color == None:
                fill_color = "FF0000"
                stroke_color = "FF0000"
            print("colors:")
            print(fill_color)
            print(stroke_color)
            fillColor = max(
                self.rgb_to_binary_rgb_int(fill_color),
                self.rgb_to_binary_rgb_int(stroke_color),
            )
            print("New colors:")
            print(stroke_color)
            print(fillColor)
            if self.points:  # Interpolation for non-first path
                start_of_path = path[0].start
                start_x = self.transform_to_fit(start_of_path.real, mintot, maxtot)
                start_y = 4096 - self.transform_to_fit(
                    start_of_path.imag, mintot, maxtot
                )
                last_point_x, last_point_y, _ = self.points[-1]
                interpolated_points = self.interpolate_points_distance(
                    (last_point_x, last_point_y), (start_x, start_y), 50
                )
                for pt in interpolated_points:
                    self.points.append((pt[0], pt[1], 0))  # Pen up moves
            last_point = None
            # Process segments within each path
            for segment in path:
                t_values = np.linspace(
                    0,
                    1,
                    max(
                        int(self.numberOfSamples * (segment.length() / path.length())),
                        2,
                    ),
                )
                samples = [segment.point(t) for t in t_values]
                x = [
                    self.transform_to_fit(point.real, mintot, maxtot)
                    for point in samples
                ]
                y = [
                    4096 - self.transform_to_fit(point.imag, mintot, maxtot)
                    for point in samples
                ]
                if last_point and (
                    last_point.real != samples[0].real
                    or last_point.imag != samples[0].imag
                ):
                    # Interpolate pen up movement
                    interpolated_points = self.interpolate_points_distance(
                        (last_point_x, last_point_y), (x[0], y[0]), 50
                    )  # Distance set to 5 units
                    for pt in interpolated_points:
                        self.points.append((pt[0], pt[1], 0))  # Pen up moves

                for i in zip(x, y):
                    self.points.append((i[0], i[1], fillColor))  # Pen down

                last_point_x, last_point_y = x[-1], y[-1]
                last_point = samples[-1]
            # Ensure to end with a pen-up at the end of the path

            self.points.append((self.points[-1][0], self.points[-1][1], 0))
        self.points.append((self.points[-1][0], self.points[-1][1], 0))
        interpolated_points = self.interpolate_points_distance(
            (self.points[-1][0], self.points[-1][1]),
            (self.points[0][0], self.points[0][1]),
            50,
        )  # Distance set to 5 units
        for pt in interpolated_points:
            self.points.append((pt[0], pt[1], 0))  # Pen up moves

    # Supporting functions and classes would remain as before.

    # def load_and_process_svg(self):
    #     # Load SVG file, extract paths and attributes
    #     paths, attributes = c(self.svg_file)

    #     # Find bounds for rescaling
    #     min_x, max_x, min_y, max_y = (
    #         float("inf"),
    #         float("-inf"),
    #         float("inf"),
    #         float("-inf"),
    #     )

    #     for path in paths:
    #         for seg in path:
    #             bbox = seg.bbox()
    #             min_x, max_x = min(min_x, bbox[0]), max(max_x, bbox[1])
    #             min_y, max_y = min(min_y, bbox[2]), max(max_y, bbox[3])
    #         self.total = self.total + path.length()
    #         print("total" + str(self.total))

    #     for path in paths:
    #         # path = paths[0]
    #         tmpSamples = self.numberOfSamples * (path.length() / self.total)
    #         samples = [path.point(t / tmpSamples) for t in range(int(tmpSamples) + 1)]
    #         samples.append(path.point(1))
    #         samples.append(path.point(0))
    #         x = [self.transform_to_fit(point.real, min_x, max_x) for point in samples]
    #         y = [
    #             4096 - self.transform_to_fit(point.imag, min_y, max_y)
    #             for point in samples
    #         ]  # Fixed the transformation for Y
    #         self.points.append((x[0], y[0], 6))
    #         color_index = random.choice([1, 2, 4])
    #         # Assign random color index 1, 2, or 4 to the stroke
    #         for i in zip(x, y):
    #             self.points.append((i[0], i[1], color_index))
    #         # Append the first point with laser off before starting the stroke
    #         if x and y:
    #             first_point = (x[-1], y[-1], 6)  # Add with laser off
    #             self.points.append(first_point)

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
