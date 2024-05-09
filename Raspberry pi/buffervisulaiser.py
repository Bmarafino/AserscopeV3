import matplotlib.pyplot as plt
import numpy as np
import struct


class BufferVisualizer:
    def __init__(self, buffer, num_points):
        self.buffer = buffer
        self.num_points = num_points
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 4096)
        self.ax.set_ylim(0, 4096)
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Real-time Buffer Data Visualization")

    def unpack_binary_data(self, binary_data):
        points = []
        colors = []
        step = 5
        for i in range(0, len(binary_data), step):
            if i + step <= len(binary_data):
                x, y, color_byte = struct.unpack("<HHB", binary_data[i : i + step])
                if color_byte == 4:
                    colors.append("red")  # Color 4 is red
                elif color_byte == 2:
                    colors.append("green")  # Color 2 is green
                elif color_byte == 1:
                    colors.append("blue")  # Color 1 is blue
                elif color_byte == 3:
                    colors.append("yellow")  # Color 3 is yellow (red + green)
                elif color_byte == 5:
                    colors.append("magenta")  # Color 5 is magenta (red + blue)
                elif color_byte == 6:
                    colors.append("cyan")  # Color 6 is cyan (green + blue)
                elif color_byte == 7:
                    colors.append("purple")  # Color 7 is white (red + green + blue)
                else:
                    colors.append("black")  # Color 0 is black

                points.append((x, y))
        return points, colors

    def plot_static_frame(self):
        binary_data = self.buffer.getBinary(self.num_points)
        points, colors = self.unpack_binary_data(binary_data)

        # Filter out points with None color
        valid_points = [(p, c) for p, c in zip(points, colors) if c]
        if valid_points:
            x, y = zip(*[p for p, c in valid_points])
            color = [c for p, c in valid_points]

            # Previous point storage for color segments
            px, py = None, None

            for xi, yi, ci in zip(x, y, color):
                if px is not None:
                    # Draw line from previous point to current point
                    self.ax.plot([px, xi], [py, yi], color=ci)
                # Update previous point
                px, py = xi, yi

            # Adding labels
            # for i, (xi, yi) in enumerate(zip(x, y)):
            #     self.ax.text(xi, yi, str(i), color="black", fontsize=12)

        plt.show()


# Example usage:
# buffer_instance = Buffer(...)  # Initialize appropriately
# visualizer = BufferVisualizer(buffer_instance, 50)
# visualizer.plot_static_frame()  # To show a static frame
