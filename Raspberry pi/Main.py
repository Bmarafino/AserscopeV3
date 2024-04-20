from bufferClass import Buffer
from ilda_class_player import ILDAReader
from ImageEdgeClass import ImageProcessor
from svg_player import SVGPlotter
from buffervisulaiser import BufferVisualizer


mainBuffer = Buffer()
print(ImageProcessor("/Users/bmarafino/Downloads/IMG_9945.jpg").get_points()[:100])
# print(ImageProcessor("/Users/bmarafino/Downloads/udel2.png").get_points()[:100])
# #print(ILDAReader("/Users/bmarafino/Downloads/bandsag.ild").get_points())

mainBuffer.add(
    "jpeg",
    ImageProcessor("/Users/bmarafino/Downloads/IMG_9945.jpg").get_points(),
    plays=10,
)
mainBuffer.add(
    "png",
    ImageProcessor("/Users/bmarafino/Downloads/udel2.png").get_points(),
    plays=10,
)
# mainBuffer.add("svg", SVGPlotter("", 300).get_points(), plays=100)
mainBuffer.add(
    "ild", ILDAReader("/Users/bmarafino/Downloads/bandsag.ild").get_points(), plays=1
)


# Assuming you have an instance of Buffer named `buffer_instance`
buffer_visualizer = BufferVisualizer(mainBuffer, 2000)
buffer_visualizer.run_visualization()
