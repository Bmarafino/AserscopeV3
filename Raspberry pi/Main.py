from bufferClass import Buffer
from ilda_class_player import ILDAReader
from ImageEdgeClass import ImageProcessor
from svg_player import SVGPlotter
from buffervisulaiser import BufferVisualizer
from svg2ild import SvgProcessor


mainBuffer = Buffer()
# print(ImageProcessor("/Users/bmarafino/Downloads/IMG_9945.jpg").get_points()[:100])
# print(ImageProcessor("/Users/bmarafino/Downloads/udel2.png").get_points()[:100])
# #print(ILDAReader("/Users/bmarafino/Downloads/bandsag.ild").get_points())


# png = ImageProcessor("/Users/bmarafino/Downloads/delawarelogo.png").get_points()

# mainBuffer.add("svg", png, plays=10)

# SVGPlotter("/Users/bmarafino/Documents/test.svg", 200).plot_svg()
# SVGPlotter("/Users/bmarafino/Downloads/building-svgrepo-com.svg", 100).plot_svg()
pointsObj = SvgProcessor("/Users/bmarafino/Documents/sendover/udel.svg").get_points()
# pointsObj = SVGPlotter("/Users/bmarafino/Downloads/apple.svg", 300).get_points()
mainBuffer.add("svg", pointsObj, plays=10)

# # mainBuffer.add(
#     "ild",
#     ILDAReader("/Users/bmarafino/Downloads/Stairway.ild").get_points(),
#     plays=1,
# )


# Assuming you have an instance of Buffer named `buffer_instance`
buffer_visualizer = BufferVisualizer(mainBuffer, len(pointsObj))
buffer_visualizer.plot_static_frame()


# print("sent 500");
