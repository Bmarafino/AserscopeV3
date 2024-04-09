import tkinter as tk
from tkinter import filedialog
import struct
import matplotlib.pyplot as plt
import turtle
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
import numpy as np

file_path = filedialog.askopenfilename()


def readHeader(byte_data):
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


def byte_to_binary_string(byte_obj):
    """
    This function takes a byte object as an input and returns a string with its binary representation.
    """
    return " ".join(f"{byte:08b}" for byte in byte_obj)


def readFrame(file, data, header):
    header = readHeader(header)
    pointInHeader = []
    match header["format_code"]:
        case 0:
            for i in range(header["total_points"]):
                curdata = file.read(8)
                currentPointstruct = struct.unpack(">hhhBB", curdata)
                pointInHeader.append(currentPointstruct)
            data.append({"header": header, "points": pointInHeader})
        case 1:
            for i in range(header["total_points"]):
                curdata = file.read(6)
                currentPointstruct = struct.unpack(">hhBB", curdata)
                pointInHeader.append(currentPointstruct)
            data.append({"header": header, "points": pointInHeader})

        case 2:
            print("color pallette frame?")
        case 3:
            print("format 3 isnt real")
        case 4:
            for i in range(header["total_points"]):
                curdata = file.read(10)
                currentPointstruct = struct.unpack(">hhhBBBBB", curdata)
                pointInHeader.append(currentPointstruct)
            data.append({"header": header, "points": pointInHeader})
        case 5:
            for i in range(header["total_points"]):
                curdata = file.read(8)
                currentPointstruct = struct.unpack(">hhBBBB", curdata)
                pointInHeader.append(currentPointstruct)
            data.append({"header": header, "points": pointInHeader})


# Replace with your file path
points = []
with open(file_path, "rb") as ILDA:
    ILDA.seek(0, 2)
    total_bytes = ILDA.tell()
    print("size")
    print(total_bytes)
    ILDA.seek(0, 0)
    # print("bytes")
    # print(byte_to_binary_string(ILDA.read(40)))
    ILDA.seek(0, 0)
    while True:
        header = ILDA.read(32)
        # print("new header")
        # print(byte_to_binary_string(header))
        if not header:
            break  # End of file
        if header[24] == 0 and header[25] == 0:
            break  # Bytes 25 and 26 are both 0, exit loop
        readFrame(ILDA, points, header)


# Your existing code to read the ILDA file and define functions...

# Function to generate equally spaced points along a line segment
import numpy as np


def generate_points_with_fixed_spacing(A, B, spacing):
    x1, y1 = A
    x2, y2 = B
    dx = x2 - x1
    dy = y2 - y1
    line_length = np.sqrt(dx**2 + dy**2)
    n = max(int(np.ceil(line_length / spacing)), 2)  # Ensure at least two points
    t = np.linspace(0, 1, n)
    x = x1 + t * dx
    y = y1 + t * dy
    points = np.column_stack((x, y))
    return points


# Modified split_segments function to generate points
def split_segments(points, spacing):
    segments = []
    current_segment = []
    for i in range(len(points) - 1):
        if points[i][2] == 0:  # Check if the laser is off
            A = (points[i][0], points[i][1])
            B = (points[i + 1][0], points[i + 1][1])
            segment_points = generate_points_with_fixed_spacing(A, B, spacing)
            current_segment.extend(segment_points)
        else:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
    if current_segment:  # Add the last segment if it exists
        segments.append(current_segment)
    return segments


# Update function to plot the generated points
def update(frame):
    ax.clear()
    segments = split_segments(
        points[frame]["points"], spacing=5
    )  # Adjust spacing as needed
    for segment in segments:
        x_coords = [int((point[0] + 32000) * (4096 / 64000)) for point in segment]
        y_coords = [int((point[1] + 32000) * (4096 / 64000)) for point in segment]
        ax.plot(x_coords, y_coords, marker=".", linestyle="-")
    ax.set_title("ILDA Points")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_xlim(0, 4096)
    ax.set_ylim(0, 4096)


# Create a new figure
fig, ax = plt.subplots(figsize=(10, 10))

# Set the limits of the plot (adjust these values as needed)
ax.set_xlim(-32000, 32000)
ax.set_ylim(-32000, 32000)

# Create the animation
ani = FuncAnimation(fig, update, frames=len(points), interval=5, repeat=True)

# Show the plot
plt.show()
