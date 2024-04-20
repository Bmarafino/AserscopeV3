import tkinter as tk
from tkinter import filedialog
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from itertools import cycle, islice
import time


class ILDAReader:
    def __init__(self, filepath):
        self.ILDAFileParsed = []
        self.buffer = []
        self.binaryBuffer = bytearray()
        self.file_path = None
        self.set_file(filepath)

    def read_header(self, byte_data):
        # Ensure the byte_data is long enough to contain a header
        if len(byte_data) < 32:
            raise ValueError("Byte data is too short to contain a valid ILDA header")
        # Extract and decode the ILDA header
        ilda_header = byte_data[:4].decode("ascii", "ignore")
        # Extract the next 3 bytes, which should be zero
        reserved = byte_data[4:7]
        # Extract the 1-byte format code
        format_code = int.from_bytes(byte_data[7:8], byteorder="big")
        # Extract the next 8 bytes for the frame name and decode
        frame_name = byte_data[8:16].split(b"\x00", 1)[0].decode("ascii", "ignore")
        # Extract the next 8 bytes for the company name and decode
        company_name = byte_data[16:24].split(b"\x00", 1)[0].decode("ascii", "ignore")
        # Extract the 2-byte total points, should be interpreted as an integer
        total_points = int.from_bytes(byte_data[24:26], byteorder="big")
        # Extract the 2-byte frame number, also an integer
        frame_number = int.from_bytes(byte_data[26:28], byteorder="big")
        # Extract the 2-byte total frames, another integer
        total_frames = int.from_bytes(byte_data[28:30], byteorder="big")
        # Extract the 1-byte scanner head
        scanner_head = int.from_bytes(byte_data[30:31], byteorder="big")
        # Extract the 1-byte future use, which should be zero
        future_use = int.from_bytes(byte_data[31:32], byteorder="big")
        # Return a dictionary of the header values
        return {
            "ilda_header": ilda_header,
            "reserved": reserved,
            "format_code": format_code,
            "frame_name": frame_name,
            "company_name": company_name,
            "total_points": total_points,
            "frame_number": frame_number,
            "total_frames": total_frames,
            "scanner_head": scanner_head,
            "future_use": future_use,
        }

    def read_frames(self, file, data, header):
        header = self.read_header(header)
        pointInHeader = []
        match header["format_code"]:
            case 0:
                for i in range(header["total_points"]):
                    curdata = file.read(8)
                    currentPointstruct = struct.unpack(">hhhBB", curdata)
                    laser = 0
                    if not (int((1 << 6) & currentPointstruct[3])):
                        laser = 7
                    pointInHeader.append(
                        (currentPointstruct[0], currentPointstruct[1], laser)
                    )

                data.append({"header": header, "points": pointInHeader})
            case 1:
                for i in range(header["total_points"]):
                    curdata = file.read(6)
                    currentPointstruct = struct.unpack(">hhBB", curdata)

                    laser = 0
                    if int(1 << 6 & currentPointstruct[2]):
                        laser = 7
                        pointInHeader.append(
                            (currentPointstruct[0], currentPointstruct[1], laser)
                        )
                data.append({"header": header, "points": pointInHeader})

            case 2:
                print("color pallette frame?")
            case 3:
                print("format 3 isnt real")
            case 4:
                for i in range(header["total_points"]):
                    curdata = file.read(10)
                    currentPointstruct = struct.unpack(">hhhBBBBB", curdata)
                    red, green, blue = currentPointstruct[3:6]
                    blanking_bit = (currentPointstruct[3] & (1 << 6)) == 0

                    if blanking_bit:
                        laser = 0  # 000 in binary, but represented as an integer
                    else:
                        max_color = max(red, green, blue)
                        if max_color == red:
                            laser = 4  # 100 in binary, but represented as an integer
                        elif max_color == green:
                            laser = 2  # 010 in binary, but represented as an integer
                        else:
                            laser = 1  # 001 in binary, but represented as an integer

                    pointInHeader.append(
                        (currentPointstruct[0], currentPointstruct[1], laser)
                    )
                data.append({"header": header, "points": pointInHeader})
            case 5:
                for i in range(header["total_points"]):
                    curdata = file.read(8)
                    currentPointstruct = struct.unpack(">hhBBBBB", curdata)
                    red, green, blue = currentPointstruct[3:6]
                    blanking_bit = (currentPointstruct[2] & (1 << 6)) == 0

                    if blanking_bit:
                        laser = 0  # 000 in binary, but represented as an integer
                    else:
                        max_color = max(red, green, blue)
                        if max_color == red:
                            laser = 4  # 100 in binary, but represented as an integer
                        elif max_color == green:
                            laser = 2  # 010 in binary, but represented as an integer
                        else:
                            laser = 1  # 001 in binary, but represented as an integer

                    pointInHeader.append(
                        (currentPointstruct[0], currentPointstruct[1], laser)
                    )

                data.append({"header": header, "points": pointInHeader})

    def scale_points(self, points):
        scaled_points = []
        for point in points:
            x, y, laser = point
            # Scale X and Y from [-32000, 32000] to [0, 4096]
            scaled_x = int(((x + 32768) / 65535) * 4096)
            scaled_y = int(((y + 32768) / 65535) * 4096)
            scaled_points.append((scaled_x, scaled_y, laser))
        return scaled_points

    def scale_data_points(self):
        for frame in self.ILDAFileParsed:
            scaled_points = self.scale_points(frame["points"])
            frame["points"] = scaled_points

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

    def interpolate_fixed_spacing(self, spacing=10):
        for frame in self.ILDAFileParsed:
            interpolated_points = []
            points = frame["points"]
            for i in range(len(points) - 1):
                A = (points[i][0], points[i][1])
                B = (points[i + 1][0], points[i + 1][1])
                laser = points[i + 1][2]  # Use the laser value of point B
                interpolated_points.extend(
                    self.generate_points_with_fixed_spacing(A, B, laser, spacing)
                )
            # Add the last point of the frame
            interpolated_points.append(points[-1])
            frame["points"] = interpolated_points

    def split_segments(self, data):
        segments = []
        current_segment = []  # Initialize current_segment before the loop
        for point in data["points"]:
            if point[2] == 0:  # Check if the laser is off
                current_segment.append(point)
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = (
                        []
                    )  # Reinitialize current_segment for the next segment
        if current_segment:  # Add the last segment if it exists
            segments.append(current_segment)
        return segments

    def read_in_file_path(self):
        with open(self.file_path, "rb") as ILDA:
            ILDA.seek(0, 2)
            total_bytes = ILDA.tell()
            print("size")
            print(total_bytes)
            ILDA.seek(0, 0)
            while True:
                header = ILDA.read(32)
                if not header:
                    break  # End of file
                if header[24] == 0 and header[25] == 0:
                    break  # Bytes 25 and 26 are both 0, exit loop
                self.read_frames(ILDA, self.ILDAFileParsed, header)

    def create_buffer(self):
        for i in self.ILDAFileParsed:
            self.buffer.extend(i["points"])

    def create_binary(self):
        # Accumulate points into binary format
        for i in self.buffer:
            self.binaryBuffer += struct.pack("<HHB", int(i[0]), int(i[1]), int(i[2]))
        # Initialize the cyclic iterator over the binary buffer
        self.cyclic_iter = cycle(self.binaryBuffer)

    #   def getBinaryPoints(self, num_points):
    #       # Each point is represented by 5 bytes, as structured by '<HHB' (2 bytes + 2 bytes + 1 byte)
    #       chunk_size = num_points * 5
    #       return bytes(islice(self.cyclic_iter, chunk_size))

    def get_binary_buffer(self):
        return self.binaryBuffer

    def get_points(self):
        return self.buffer

    def set_file(self, file_path):
        self.file_path = file_path
        self.ILDAFileParsed = []
        self.buffer = []
        self.binaryBuffer = bytearray()
        self.read_in_file_path()
        self.scale_data_points()
        # self.interpolate_fixed_spacing(spacing)
        self.create_buffer()
        self.create_binary()

    def readFile():
        ilda_reader.scale_data_points()
        ilda_reader.interpolate_fixed_spacing(50)
        ilda_reader.create_buffer()
        ilda_reader.create_binary()

    def graph(self):
        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 10))

        # Set the limits of the plot (adjust these values as needed)
        ax.set_xlim(-32000, 32000)
        ax.set_ylim(-32000, 32000)

        # Update function to plot the generated points
        def update(frame):
            ax.clear()
            segments = self.split_segments(frame)  # Adjust spacing
            for segment in segments:
                x_coords = [int(point[0]) for point in segment]
                y_coords = [int(point[1]) for point in segment]
                ax.plot(x_coords, y_coords, marker=".", linestyle="-")
            ax.set_title("ILDA Points")
            ax.set_xlabel("X Coordinate")
            ax.set_ylabel("Y Coordinate")
            ax.set_xlim(0, 4096)
            ax.set_ylim(0, 4096)

        # Create the animation
        ani = FuncAnimation(
            fig, update, frames=self.ILDAFileParsed, interval=5, repeat=True
        )

        # Show the plot
        plt.show()


def send_spi_data(bufferSub):
    print("Sending data...")
    binary_buffer = bytearray()
    for point in random_points:
        binary_buffer += struct.pack("<HHB", *point)
    start_time = time.perf_counter()

    end_time = time.perf_counter()
