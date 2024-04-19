import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import random


class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = self.load_image()
        if self.image is not None:
            self.edges = self.convert_to_edges()
            self.contours = self.find_contours(self.edges)
            self.reduced_contours = self.filter_and_reduce_contours(self.contours)
            self.scaled_contours = self.scale_contours(self.reduced_contours)
        else:
            self.edges = None
            self.contours = None
            self.reduced_contours = None
            self.scaled_contours = None

    def load_image(self):
        try:
            return Image.open(self.image_path)
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None

    def convert_to_edges(self):
        if self.image is None:
            return None
        try:
            gray_image = self.image.convert("L")
            gray_array = np.array(gray_image)
            edges = cv2.Canny(gray_array, 100, 200)
            kernel = np.ones((5, 5), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            edges = cv2.erode(edges, kernel, iterations=1)
            return edges
        except Exception as e:
            print(f"Error during edge conversion: {e}")
            return None

    def find_contours(self, edges):
        if edges is None:
            return []
        return cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]

    def filter_and_reduce_contours(self, contours, max_points=50000):
        if not contours:
            return []

        total_points = sum(len(contour) for contour in contours)
        if total_points <= max_points:
            return contours

        scale_factor = max_points / total_points
        new_contours = []
        for contour in contours:
            reduced_size = int(len(contour) * scale_factor)
            if reduced_size > 1:
                x = np.linspace(0, len(contour) - 1, num=reduced_size)
                interp_x = np.interp(x, np.arange(len(contour)), contour[:, 0, 0])
                interp_y = np.interp(x, np.arange(len(contour)), contour[:, 0, 1])
                new_contour = (
                    np.column_stack((interp_x, interp_y)).astype(int).reshape(-1, 1, 2)
                )
                new_contours.append(new_contour)
            elif len(contour) > 0:
                new_contours.append(contour)
        return new_contours

    def scale_contours(self, contours, scale_to=(0, 4096)):
        if not contours:
            return []

        all_points = np.vstack(
            [contour.squeeze() for contour in contours if contour.size > 0]
        )
        if all_points.size == 0:
            print("No points available to scale.")
            return []

        x_min, x_max = np.min(all_points[:, 0]), np.max(all_points[:, 0])
        y_min, y_max = np.min(all_points[:, 1]), np.max(all_points[:, 1])

        scaled_contours = []
        for contour in contours:
            scaled_x = np.interp(contour[:, 0, 0], (x_min, x_max), scale_to)
            scaled_y = np.interp(contour[:, 0, 1], (y_min, y_max), scale_to)
            scaled_contour = (
                np.column_stack((scaled_x, scaled_y)).astype(int).reshape(-1, 1, 2)
            )
            scaled_contours.append(scaled_contour)
        return scaled_contours

    def plot_contours(self):
        if not self.scaled_contours:
            print("No contours to plot.")
            return
        plt.figure(figsize=(10, 6))
        for contour in self.scaled_contours:
            plt.plot(contour[:, 0, 0], contour[:, 0, 1], linewidth=1)
        plt.show()

    def print_contour_points_and_count(self):

        total_points = 0
        all_points = []
        for contour in self.scaled_contours:
            for point in contour:
                x, y = point[0]
                all_points.append((x, y))
                print(f"Point: ({x}, {y})")
        total_points = len(all_points)
        print(f"Total number of points: {total_points}")
        return all_points, total_points

    def get_points(self):
        all_points = []
        for contour in self.scaled_contours:
            color = random.choice([1, 3, 4])
            all_points.append((contour[0][0][0], 4090 - contour[0][0][1], 0))
            for point in contour:
                x, y = point[0]
                all_points.append((x, 4090 - y, color))
        return all_points


image = ImageProcessor("/Users/bmarafino/Downloads/udel2.png")
image.plot_contours()
image.get_points()
print(image.get_points()[:100])
