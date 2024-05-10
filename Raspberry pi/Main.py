from bufferClass import Buffer
from ilda_class_player import ILDAReader
from ImageEdgeClass import ImageProcessor
from svg_player import SVGPlotter
from buffervisulaiser import BufferVisualizer
from svg2ild import SvgProcessor
from letterTranslation import *

def fix_text(input_text):
    input_text = input_text.upper()
    length_text = len(input_text)
    points = []
    for i in range(length_text):
        modifier = i * 4096
        for x in range(len(letter_dict[input_text[i]])):
            if x * 3 % length_text == 0:
                points.append(tuple([(letter_dict[input_text[i]][x][0] + modifier) // (length_text + 1), letter_dict[input_text[i]][x][1], i % 3 + 1 if letter_dict[input_text[i]][x][2] != 0 else 0]))
    return points

letter_dict = get_letter_dict()
mainBuffer = Buffer()
# print(ImageProcessor("/Users/bmarafino/Downloads/IMG_9945.jpg").get_points()[:100])
# print(ImageProcessor("/Users/bmarafino/Downloads/udel2.png").get_points()[:100])
# #print(ILDAReader("/Users/bmarafino/Downloads/bandsag.ild").get_points())


# png = ImageProcessor("/Users/bmarafino/Downloads/delawarelogo.png").get_points()

# mainBuffer.add("svg", png, plays=10)

input_text = "Decision Day 2025"

points = fix_text(input_text)

# SVGPlotter("/Users/bmarafino/Documents/test.svg", 200).plot_svg()
# SVGPlotter("/Users/bmarafino/Downloads/building-svgrepo-com.svg", 100).plot_svg()
pointsObj = SvgProcessor("C:/Users/zachm/A.svg").get_points()
print(pointsObj)
# pointsObj = SVGPlotter("/Users/bmarafino/Downloads/apple.svg", 300).get_points()
#mainBuffer.add("svg", pointsObj, plays=10)
mainBuffer.add("txt", points, plays=100)

# # mainBuffer.add(
#     "ild",
#     ILDAReader("/Users/bmarafino/Downloads/Stairway.ild").get_points(),
#     plays=1,
# )


# Assuming you have an instance of Buffer named `buffer_instance`
buffer_visualizer = BufferVisualizer(mainBuffer, len(letter_dict["C"]) + 1000) #This might need to be changed back but I was using it for testing letters
buffer_visualizer.plot_static_frame()


# print("sent 500");
