import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import struct


class BufferVisualizer:
    def __init__(self, buffer, num_points):
        self.buffer = buffer
        self.num_points = num_points
        self.fig, self.ax = plt.subplots()
        self.sc = self.ax.scatter([], [])
        self.ax.set_xlim(0, 4096)  # Set the axis limits based on expected data range
        self.ax.set_ylim(0, 4096)
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Real-time Buffer Data Visualization")

    def update_graph(self, frame):
        # Fetch binary data from the buffer
        binary_data = self.buffer.getBinary(self.num_points)

        # Convert binary data to points
        points = self.unpack_binary_data(binary_data)

        # Update scatter plot
        if points:
            x, y = zip(*[(p[0], p[1]) for p in points])  # Safely unpack only x and y
            self.sc.set_offsets(np.c_[x, y])
        return (self.sc,)

    def unpack_binary_data(self, binary_data):
        points = []
        step = 5  # Since we know each point is represented by 5 bytes
        for i in range(0, len(binary_data), step):
            if i + step <= len(binary_data):
                x, y, _ = struct.unpack("<HHB", binary_data[i : i + step])
                points.append((x, y))
        return points

    def run_visualization(self):
        # Create an animation that continuously updates the plot
        animation = FuncAnimation(self.fig, self.update_graph, interval=100)
        plt.show()


# Assuming 'buffer_instance' is an instance of a Buffer class that provides the getBinary method
# buffer_instance = Buffer(...)  # You should initialize this appropriately
# visualizer = BufferVisualizer(buffer_instance, 50)
# visualizer.run_visualization()
