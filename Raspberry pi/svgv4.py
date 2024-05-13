# Read SVG into a list of path objects and list of dictionaries of attributes
from svgpathtools import svg2paths, wsvg

paths, attributes = svg2paths(
    "/Users/bmarafino/Documents/FilesPlay/icons8-apple-logo.svg"
)

# Update: You can now also extract the svg-attributes by setting
# return_svg_attributes=True, or with the convenience function svg2paths2
from svgpathtools import svg2paths2

paths, attributes, svg_attributes = svg2paths2(
    "/Users/bmarafino/Documents/drawing2.svg"
)

# Let's print out the first path object and the color it was in the SVG
# We'll see it is composed of two CubicBezier objects and, in the SVG file it
# came from, it was red
redpath = paths[2]
redpath_attribs = attributes[0]
print(redpath)
# print(redpath_attribs["stroke"])
