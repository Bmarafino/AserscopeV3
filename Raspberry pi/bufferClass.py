import struct
from itertools import cycle, islice


class Buffer:
    def __init__(self):
        self.binaryBuffer = {}
        self.keys = []
        self.currentKeyIndex = 0
        self.playCount = 0
        self.curInd = 0

    def add(self, Name, TupleArray, plays):
        binary_data = self.create_binary(TupleArray)
        self.binaryBuffer[Name] = {"value": binary_data, "plays": plays}
        self.keys = list(self.binaryBuffer.keys())  # Refresh keys after adding

    def remove(self, Name):
        if Name in self.binaryBuffer:
            del self.binaryBuffer[Name]
            self.keys = list(self.binaryBuffer.keys())
            self.currentKeyIndex = 0 if self.keys else None
            self.curInd = 0

    def getBinary(self, num_points):
        result = bytearray()
        bytes_needed = num_points * 5
        while len(result) < bytes_needed:
            if not self.keys:
                break  # No data to process

            current_key = self.keys[self.currentKeyIndex]
            current_data = self.binaryBuffer[current_key]["value"]
            current_plays = self.binaryBuffer[current_key]["plays"]

            # Calculate remaining bytes and plays
            remaining_bytes = bytes_needed - len(result)
            plays_left = current_plays - self.playCount

            if plays_left > 0:
                # Determine how many bytes can be fetched this cycle
                data_to_fetch = min(
                    remaining_bytes, len(current_data) - self.curInd * 5
                )
                # Using islice to fetch data segment efficiently
                data_iter = islice(
                    current_data, self.curInd * 5, self.curInd * 5 + data_to_fetch
                )
                result.extend(data_iter)
                self.curInd += data_to_fetch // 5
                if self.curInd * 5 >= len(current_data):
                    self.curInd = 0
                    self.playCount += 1
            if self.playCount >= current_plays:
                # Move to the next key
                self.currentKeyIndex = (self.currentKeyIndex + 1) % len(self.keys)
                self.playCount = 0
                self.curInd = 0

        return bytes(result)

    def create_binary(self, item):
        binary_buffer = bytearray()
        for i in item:
            binary_buffer.extend(
                struct.pack(
                    "<HHB",
                    int(((i[0]) * (2000 / 4090)) + 1000),
                    int(((i[1]) * (2000 / 4090)) + 1000),
                    int(i[2]),
                )
            )

        return binary_buffer


# points1 = [(100, 150, 1), (200, 250, 2), (300, 350, 3)]
# points2 = [(400, 450, 4), (500, 550, 5), (600, 650, 6)]
# buffer.add("Sequence1", points1, plays=3)
# buffer.add("Sequence2", points2, plays=2)
