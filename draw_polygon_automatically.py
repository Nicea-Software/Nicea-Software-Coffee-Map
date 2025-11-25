import math

from qgis.core import QgsProject, QgsRaster, QgsPointXY
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import Qt

def find_border_pixels(x, y, initial_pixel_value, raster_layer):
    if initial_pixel_value == 0:
        print("Initial pixel value cannot be zero.")
    else:
        while True:
            x += 25  # Move right
            y += 25  # Move down
            # Here you would typically check the pixel value at (x, y)
            # For demonstration, let's assume we have a function get_pixel_value(x, y)
            new_point = QgsPointXY(x, y)
            pixel_value = raster_layer.dataProvider().identify(new_point, QgsRaster.IdentifyFormatValue).results().get(1)

            if pixel_value != 0:
                print(f"Border pixel not at: {x}, {y} with value {pixel_value}")
                continue
            else:
                print(f"Found border pixel at: {x}, {y} with value {pixel_value}")
                return QgsPointXY(x, y)

# def create_shape_file_from_layer():


def start_drawing_polygon_from_point(start_point, raster_layer):
    current_x = start_point.x()
    current_y = start_point.y()
    angle = 0 
    while True:
        x = 15*math.cos(math.radians(angle)) + current_x
        y = 15*math.sin(math.radians(angle)) + current_y


class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, raster_layer):
        super().__init__(canvas)
        self.canvas = canvas
        self.map_layer = raster_layer
        self.canvasClicked.connect(self.handle_click)


    def handle_click(self, point, button):
        if button == Qt.LeftButton:
            # while True:
            #     layer_name = input("Enter raster layer name: ").strip()
            #     if not layer_name:
            #         print("No name entered. Please try again.")
            #         continue
            

            # 'point' is a QgsPointXY in map coordinates
            results = self.map_layer.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
            if results.isValid():
                pixel_value = results.results().get(1)  # band 1
                border_point = find_border_pixels(point.x(), point.y(), pixel_value, self.map_layer)


                print(f"Clicked at: {point.x()}, {point.y()}")
            else:
                print("No valid pixel value found at this location.")





# Usage in QGIS Python console:
canvas = iface.mapCanvas()
map_layers = QgsProject.instance().mapLayersByName('Ethopia_Map_modified')
map_layer = map_layers[0]

point_tool = PointTool(canvas, map_layer)
# canvas.setMapTool(point_tool)

# Example of identifying a point programmatically:
# pt = QgsPointXY(38.0, 9.0)  # replace with real coordinates in map CRS
# nearby_pixels = map_layer.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue)
# print(nearby_pixels.results())