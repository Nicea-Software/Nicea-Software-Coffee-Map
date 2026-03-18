import math
import processing

from qgis.core import QgsProject, QgsRaster, QgsPointXY, QgsGeometry, QgsVectorLayer, QgsFeature
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.PyQt.QtCore import Qt



def get_pixel_value_at_point(raster_layer, point):
    results = raster_layer.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
    if results.isValid():
        # print(str(results.results()))
        return results.results().get(1)  # band 1
    return None 

def find_border_pixels(x, y, initial_pixel_value, search_distance, raster_layer):
    if initial_pixel_value == 0:
        print("initial border point can't be black")
    else:
        print("searching for border pixel...")
        while True:
            x += search_distance  # Move right
            y += search_distance  # Move down
            # Here you would typically check the pixel value at (x, y)
            # For demonstration, let's assume we have a function get_pixel_value(x, y)
            new_point = QgsPointXY(x, y)
            pixel_value = get_pixel_value_at_point(raster_layer, new_point)

            if pixel_value != 0:
                # print(f"Border pixel not at: {x}, {y} with value {pixel_value}")
                continue
            else:
                print(f"Found border pixel at: {x}, {y} with value {pixel_value}")
                return QgsPointXY(x, y)

def smooth_line(input_layer):
    parameters = {
        'INPUT': input_layer,
        'Iterations': 2,
        'OFFSET': 0.3,
        'MAX_ANGLE': 180,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    }
    smoothed_layer = processing.run("native:smoothgeometry", parameters)['OUTPUT']
    return smoothed_layer


def create_polyline_layer(layer_name, crs_string="EPSG:4326"):
    """
    Creates a new temporary memory layer for polylines.
    """
    # Define the layer's data source URI: type="memory", geometryType="LineString"
    uri = f"LineString?crs={crs_string}"
    layer = QgsVectorLayer(uri, layer_name, "memory")
    if not layer.isValid():
        return None
    return layer


def find_outside_border_point(current_point, raster_layer, search_distance):
    current_x = current_point.x()
    current_y = current_point.y()

    # We need to find the initial outside border point first we will rotate around the current point in a circle to find it
    angle_to_search_upon = None
    initial_border_point = None
    
    for search_radius in range(5, 50, 5):
        for angle in range(0, 360, 5):
            x = search_radius * math.cos(math.radians(angle)) + current_x
            y = search_radius * math.sin(math.radians(angle)) + current_y
            new_point = QgsPointXY(x, y)
            pixel_value = get_pixel_value_at_point(raster_layer, new_point)
            if pixel_value == 0:
                initial_border_point = new_point
                angle_to_search_upon = angle
                break

        if initial_border_point != None:
            break

    if initial_border_point == None:
        x = current_x + 5
        y = current_y + 5
        initial_border_point = QgsPointXY(x,y)
        angle_to_search_upon = 45
    
    outside_border_point = initial_border_point
    outside_border_point_confirmed = False
    # Now we start looking for the outside border point further out along the same angle
    # We need to cutoff after a certain point in case we run down the border of another region
    
    i = 0
    while not outside_border_point_confirmed and i < 10:
        x = outside_border_point.x() + search_distance * math.cos(math.radians(angle_to_search_upon))
        y = outside_border_point.y() + search_distance * math.sin(math.radians(angle_to_search_upon))
        new_point = QgsPointXY(x, y)
        pixel_value = get_pixel_value_at_point(raster_layer, new_point)
        if pixel_value != 0:
            outside_border_point_confirmed = True
        else:
            outside_border_point = new_point

        i += 1

    return outside_border_point



def find_closest_white_border_point(current_point, outside_border_point, raster_layer, search_distance):
    current_x = current_point.x()
    current_y = current_point.y()

    outside_x = outside_border_point.x()
    outside_y = outside_border_point.y()

    relative_y = outside_y - current_y
    relative_x = outside_x - current_x
    angle_offset = math.degrees(math.atan2(relative_y, relative_x))

    adjusted_angle = 0 + angle_offset
    previous_x = current_x + search_distance * math.cos(math.radians(adjusted_angle))
    previous_y = current_y + search_distance * math.sin(math.radians(adjusted_angle))
    previous_point = QgsPointXY(previous_x, previous_y)

    # Find optimal white pixel
    optimal_white_pixel = previous_point
    for angle in range(-90, 90, 5):
        adjusted_angle = angle + angle_offset
        x = current_x + search_distance * math.cos(math.radians(adjusted_angle))
        y = current_y + search_distance * math.sin(math.radians(adjusted_angle))

        new_point = QgsPointXY(x, y)
        previous_pixel_value = get_pixel_value_at_point(raster_layer, previous_point)
        pixel_value = get_pixel_value_at_point(raster_layer, new_point)
        if pixel_value == 0:
            break
        elif previous_pixel_value < pixel_value:
            # optimal_white_pixel = new_point
            previous_point = new_point

    return previous_point

def get_distance_between_neighboring_pixels(pixel_position1, pixel_position2):
    # [(0,0), (0,1), (0,2)]
    # [(1,0),        (1,2)]
    # [(2,0), (2,1), (2,2)]

    discrete_condition = (pixel_position1 == (0,0) and pixel_position2 == (2,2)) or \
                (pixel_position1 == (2,2) and pixel_position2 == (0,0)) or \
                (pixel_position1 == (0,1) and pixel_position2 == (2,1)) or \
                (pixel_position1 == (2,1) and pixel_position2 == (0,1))

    if  discrete_condition:
        distance = 4
    else:
        distance = abs(pixel_position1[0]  - pixel_position2[0]) + abs(pixel_position1[1]  - pixel_position2[1])
    return distance

def search_for_diagnonal_point_closest_to_white(original_search_angle, current_point, search_distance, raster_layer):
    if original_search_angle == 315 or original_search_angle == 225:
        new_search_interval = search_distance/10
    elif original_search_angle == 45 or original_search_angle == 135:
        new_search_interval = -search_distance/10
    else:
        raise ValueError("Angle must be 45, 135, 225, 315")

    # previous_point = current_point.y()
    # current_y = current_point.y() + new_search_interval
    # current_x = current_point.x()

    previous_point = current_point
    current_x = previous_point.x()
    current_y = previous_point.y()


    while get_pixel_value_at_point(raster_layer, QgsPointXY(current_x, current_y)) == 0:
        previous_point = QgsPointXY(current_x, current_y)
        if original_search_angle == 45 or original_search_angle == 225:
            current_x = current_x + new_search_interval
        else:
            current_y = current_y + new_search_interval
    
    return previous_point


    current_point_x = current_point.x()
    current_point_y = current_point.y()

def is_pixel_in_range(point_1, point_2, search_distance):
    distance = math.sqrt((point_1.x() - point_2.x())**2 + (point_1.y() - point_2.y())**2)
    # print("Distance between first and last point: " + str(distance))
    # print("Search distance: " + str(search_distance))
    return distance > search_distance

def start_drawing_polygon_from_point(start_point, search_distance, raster_layer, canvas):
    current_x = start_point.x()
    current_y = start_point.y()
    list_of_points = [QgsPointXY(current_x, current_y)]

    # First we are going to find a point on the outside edge of the shape
    # So that we can set an x axis to start proper angle calculations
    # Second we find a white pixel that is close to the new y axis
    x = current_x
    y = current_y
    previous_direction = None

    # oposite_direction_map = [
    #     [(2,2), (2,1), (2,0)],
    #     [(1,1),        (1,0)],
    #     [(0,2), (0,1), (0,0)]
    # ]

    previous_angle = None
    loop_count = 0
    # Need to check what band 1,2,3 values are for black and white and make sure we are using the true black and white values
    f = open('/tmp/logs.txt', 'w')
    

    # while ((list_of_points[0] != list_of_points[-1] or len(list_of_points) == 1)) and len(list_of_points) < 10000:
    while ((is_pixel_in_range(list_of_points[0], list_of_points[-1], search_distance) or len(list_of_points) < 5)):
        # search_radius = pixel_width * 3
        print(len(list_of_points))
        f.write(str(len(list_of_points)) + '\n')
        tracked_point = list_of_points[-1]
        search_values = [0]

        pixel_width = raster_layer.rasterUnitsPerPixelX()
        search_distance = math.sqrt(pixel_width ** 2 + pixel_width ** 2)
        edge_case_2 = False
        # We need to find the white pixel closest to the current point in a radial sweep
        first_black_pixel_is_previous_angle = False
        previous_point = None
        
        # We need to make sure we don't have a situation where we have a diagonal continuation
        # b | w 
        # w | b
        # or 
        # w | b
        # b | w

        _45_x =  1.5 * search_distance * math.cos(math.radians(45)) + current_x
        _45_y =  1.5 * search_distance * math.sin(math.radians(45)) + current_y
        _45_value = get_pixel_value_at_point(raster_layer, QgsPointXY(_45_x, _45_y))

        _135_x = 1.5 * search_distance * math.cos(math.radians(135)) + current_x
        _135_y = 1.5 * search_distance * math.sin(math.radians(135)) + current_y
        _135_value = get_pixel_value_at_point(raster_layer, QgsPointXY(_135_x, _135_y))

        _225_x = 1.5 * search_distance * math.cos(math.radians(225)) + current_x
        _225_y = 1.5 * search_distance * math.sin(math.radians(225)) + current_y
        _225_value = get_pixel_value_at_point(raster_layer, QgsPointXY(_225_x, _225_y))

        _315_x = 1.5 * search_distance * math.cos(math.radians(315)) + current_x
        _315_y = 1.5 * search_distance * math.sin(math.radians(315)) + current_y
        _315_value = get_pixel_value_at_point(raster_layer, QgsPointXY(_315_x, _315_y))

        f.write("_45_value: " + str(_45_value) + "\n")
        f.write("_135_value: " + str(_135_value) + "\n")
        f.write("_225_value: " + str(_225_value) + "\n")
        f.write("_315_value: " + str(_315_value) + "\n")

        if ((_45_value == 0 and _225_value == 0) and (_135_value != 0 and _315_value != 0)):
            # Now move to figure out what is the correct angle 45 or 225 it depends on previous angle
            # Also we check whether previous angle is within 45 degrees of the angle
            # Then to prevent crossing to other side of border we find the closest point to white pixel.
            if (previous_angle > 90 ):
                previous_angle = 225
                f.write("Angle found: 45\n")
                new_point = search_for_diagnonal_point_closest_to_white(45, QgsPointXY(_45_x, _45_y), search_distance, raster_layer)
            elif (previous_angle < 180 or previous_angle > 270):
                previous_angle = 45
                f.write("Angle found: 225\n")
                new_point = search_for_diagnonal_point_closest_to_white(225, QgsPointXY(_225_x, _225_y), search_distance, raster_layer)
                
            list_of_points.append(new_point)
            current_x = list_of_points[-1].x()
            current_y = list_of_points[-1].y()
            f.write("Coordinante Added:  " + str(list_of_points[-1].x()) + ',' + str(list_of_points[-1].y()) + '\n')
            continue

        elif (_45_value != 0 and _225_value != 0) and (_135_value == 0 and _315_value == 0):
            if (previous_angle < 270 and previous_angle != 0):
                previous_angle = 135
                f.write("Angle found: 315\n")
                new_point = search_for_diagnonal_point_closest_to_white(315, QgsPointXY(_315_x, _315_y), search_distance, raster_layer)
            elif (previous_angle < 90 or previous_angle > 180):
                previous_angle = 315
                f.write("Angle found: 135\n")
                new_point = search_for_diagnonal_point_closest_to_white(135, QgsPointXY(_135_x, _135_y), search_distance, raster_layer) 

            list_of_points.append(new_point)
            current_x = list_of_points[-1].x()
            current_y = list_of_points[-1].y()
            f.write("Coordinante Added:  " + str(list_of_points[-1].x()) + ',' + str(list_of_points[-1].y()) + '\n')
            continue
        elif (_45_value != 0 and _225_value != 0 and _135_value != 0 and _315_value != 0):
            f.write("Edge case 3 triggered\n")
            x = search_distance * math.cos(math.radians(0)) + current_x
            y = search_distance * math.sin(math.radians(0)) + current_y
            list_of_points.append(QgsPointXY(x, y))
            previous_angle = 180
            f.write("Coordinante Added:  " + str(list_of_points[-1].x()) + ',' + str(list_of_points[-1].y()) + '\n')
            current_x = x
            current_y = y
            continue
            
        
        
        # There is a situation where we have no black pixels in our search
        # except for the previous angle 90 degrees away from our current angle 
        # Therefore it doubles back on itself in the aggregate
        #  lw | w
        #  b  | w
        # Therefore we should aim in these situtions to go in the 1st quadrant
        # This is mostly a particular problem with the raster we are on not coloring its 
        # pixels alawys completely


        _270_x = 1.5 * search_distance * math.cos(math.radians(270)) + current_x
        _270_y = 1.5 * search_distance * math.sin(math.radians(270)) + current_y
        
        _270_value = get_pixel_value_at_point(raster_layer, QgsPointXY(_270_x, _270_y))
        if (_225_value == 0 and _270_value == 0 and  (_45_value > 0 and _45_value < 10 )and _135_value != 0 and _315_value != 0 ):
            
            f.write("Edge case 2 triggered\n")
            f.write("Utilizing Alternative Trace values\n")
            edge_case_2 = True
            search_distance = 1.5 * search_distance
            search_values = [ _45_value ]
        elif (_45_value != 0 and _225_value == 0 and previous_angle == 225) and (_135_value != 0 and _315_value != 0):
            f.write("Edge case 3 triggered\n")
            f.write("Just adding 0 degree poin")
            _0_x = search_distance * math.cos(math.radians(0)) + current_x
            _0_y = search_distance * math.sin(math.radians(0)) + current_y
            previous_angle = 0
            current_x = _0_x
            current_y = _0_y
            previous_point = QgsPointXY(_0_x, _0_y)
            list_of_points.append(QgsPointXY(_0_x, _0_y))
            f.write("Coordinante Added:  " + str(list_of_points[-1].x()) + ',' + str(list_of_points[-1].y()) + '\n')
            continue
        # elif (_45_value != 0 and previous_angle != )

        for angle in range(0, 360, 45):
            f.write("searching at angle: " + str(angle) + '\n')
            # start searching for the first black pixel


            new_x = search_distance * math.cos(math.radians(angle)) + current_x
            new_y = search_distance * math.sin(math.radians(angle)) + current_y
            
            if len(list_of_points) > 2:
                second_to_last_point = list_of_points[-2]
                distance_second_to_last_point = math.sqrt((new_x - second_to_last_point.x())**2 + (new_y - second_to_last_point.y())**2) 
            # f.write("Point being tested: " + str(QgsPointXY(new_x, new_y)) + '\n')
            
            f.write("Point value: " + str(get_pixel_value_at_point(raster_layer, QgsPointXY(new_x, new_y))) + '\n')


            if not first_black_pixel_is_previous_angle:
                pixel_value = get_pixel_value_at_point(raster_layer, QgsPointXY(new_x, new_y))
                if pixel_value in search_values:
                    if previous_angle is None:
                        if previous_point is not None:
                            f.write("adding point 1\n")
                            list_of_points.append(QgsPointXY(new_x, new_y))
                            previous_angle = angle + 180 % 360
                            break
                        else:
                            f.write("switching mode because found first black pixel and we have no previous point\n")
                            previous_point = QgsPointXY(new_x, new_y)
                            first_black_pixel_is_previous_angle = True
                            f.write("adding point 2\n")
                            # list_of_points.append(QgsPointXY(new_x, new_y))
                            # previous_angle = angle + 180 % 360
                            # break
                    elif previous_angle == angle:
                        f.write("switching mode because the program found previous angle\n")
                        f.write("found previous angle\n")
                        first_black_pixel_is_previous_angle = True
                        if angle != 0:
                            previous_point = QgsPointXY(x, y)
                    else:
                        # print("previous point value: " + previous_point)
                        if previous_point is None:
                            f.write("switching mode\n")
                            first_black_pixel_is_previous_angle = True
                            if previous_angle is not angle - 45:
                                previous_point = QgsPointXY(new_x, new_y)
                        else:
                            # We for some reason find resolve this after switching modes in the previous  
                            # if statement but it should not be possible it should fail this and continue to next angle but it
                            # for some reason things this is the case
                            f.write("adding point 3\n")
                            if distance_second_to_last_point < search_distance:
                                # Sometimes it we can accidentally double back on ourselves because we are picking up on a random black pixel.
                                f.write("Switching Mode because found eligible pixel is too close to second to last point\n")
                                previous_point = QgsPointXY(new_x, new_y)
                                first_black_pixel_is_previous_angle = True
                            else:
                                list_of_points.append(QgsPointXY(new_x, new_y))
                                previous_angle = (angle + 180) % 360
                                break
                else:
                    # print("setting previous point") 
                    previous_point =  QgsPointXY(new_x, new_y) 
            else:
         
                if get_pixel_value_at_point(raster_layer, QgsPointXY(new_x, new_y)) not in search_values:
                    if previous_point is not None and previous_angle is not angle - 45:
                        f.write("adding point 4\n")
                        previous_angle = (angle - 45 + 180) % 360
                        list_of_points.append(previous_point)
                        break
                    elif previous_point is None:
                        # print("switching mode because not valid white point is found")
                        previous_point = QgsPointXY(new_x, new_y)
                        first_black_pixel_is_previous_angle = False
                elif get_pixel_value_at_point(raster_layer, QgsPointXY(new_x, new_y)) in search_values and previous_angle == angle:
                    f.write("found previous angle\n")
                    f.write("switching mode because we found previous angle looking for non white point\n")
                    first_black_pixel_is_previous_angle = False
                    previous_point = None
                else:
                    f.write("stuck in last else\n")
                    previous_point = QgsPointXY(new_x, new_y)
                    if previous_angle == angle - 45:
                        f.write("switching mode to look for black point to avoid doubling back on the same points\n")
                        first_black_pixel_is_previous_angle = True
            # The first point we tested is the point if this is true
        
        if tracked_point is list_of_points[-1]:
            # print("adding because we found nothing else point")
            x = search_distance * math.cos(math.radians(0)) + current_x
            y = search_distance * math.sin(math.radians(0)) + current_y

            f.write("edge_case_2: " + str(edge_case_2) + '\n')
            if get_pixel_value_at_point(raster_layer, QgsPointXY(x, y)) not in search_values and edge_case_2 == False:
            
                f.write("Last default point is white.  We will go to a black point\n")
                for angle in range(315, 45, -45):
                    x =  search_distance * math.cos(math.radians(angle)) + current_x
                    y = search_distance * math.sin(math.radians(angle)) + current_y
                    f.write(str(get_pixel_value_at_point(raster_layer, QgsPointXY(x, y))) + '\n' )
                    f.write(str(angle) + '\n')
                    if get_pixel_value_at_point(raster_layer, QgsPointXY(x, y)) in search_values:
                        break
            list_of_points.append(QgsPointXY(x, y))
            previous_angle = 180

 
        f.write("Coordinante Added:  " + str(list_of_points[-1].x()) + ',' + str(list_of_points[-1].y()) + '\n')

          


        current_x = list_of_points[-1].x()
        current_y = list_of_points[-1].y()

    list_of_points.append(list_of_points[0])

    layer = create_polyline_layer("AutoDrawn_Polygon", raster_layer.crs().authid())
    # polyline = QgsRubberBand(canvas)
    geometry = QgsGeometry.fromPolylineXY(list_of_points)

    feature = QgsFeature(layer.fields())
    feature.setGeometry(geometry)
    layer.dataProvider().addFeatures([feature])
    smoothed_layer = smooth_line(layer)
    QgsProject.instance().addMapLayer(smoothed_layer)


class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, raster_layer):
        super().__init__(canvas)
        self.canvas = canvas
        self.map_layer = raster_layer
        self.canvasClicked.connect(self.handle_click)


    def handle_click(self, point, button):
        if button == Qt.LeftButton:
            results = self.map_layer.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
            print("units per pixel")
            print(self.map_layer.rasterUnitsPerPixelX())
            if results.isValid():
                pixel_value = results.results().get(1)  # band 1
                pixel_width = self.map_layer.rasterUnitsPerPixelX()
                search_distance = math.sqrt(pixel_width ** 2 + pixel_width ** 2)

                border_point = find_border_pixels(point.x(), point.y(), pixel_value, search_distance/25, self.map_layer)
                start_drawing_polygon_from_point(border_point, search_distance, self.map_layer, self.canvas)

                print(f"Clicked at: {point.x()}, {point.y()}")
            else:
                print("No valid pixel value found at this location.")





# Usage in QGIS Python console:
canvas = iface.mapCanvas()
map_layers = QgsProject.instance().mapLayersByName('Ethopia_Map_modified')
map_layer = map_layers[0]

point_tool = PointTool(canvas, map_layer)
canvas.setMapTool(point_tool)

# Example of identifying a point programmatically:
# pt = QgsPointXY(38.0, 9.0)  # replace with real coordinates in map CRS
# nearby_pixels = map_layer.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue)
# print(nearby_pixels.results())