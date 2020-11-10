import pyzed.sl as sl
import math
import numpy as np
import sys
import cv2


# gets the vector from the left eye to an (x,z) point
def get_vector(x,z):
    angle = math.atan(x/z)
    # pythagorean theorem to find hypotenuse
    distance = math.sqrt(x**2 + z**2)
    return (angle, distance)


def get_y_slice(point_cloud, y, tolerance):
    # get number of rows and cols in point cloud
    rows = point_cloud.shape[0]
    cols = point_cloud.shape[1]

    slice = []

    # loop over every point in the point cloud
    for i in range(0, rows):
        for j in range(0, cols):
            point = point_cloud.get_value(i,j) # [x,y,z]
            if abs(point[1] - y) <= tolerance:
                slice.append(point)
    
    return slice


# WIP
def search_for_depth_disparity(y_slice):
    # get number of rows and cols in y_slice
    rows = y_slice.shape[0]
    cols = y_slice.shape[1]

    # minimum change in depth to be recognized as an obstacle.
    depth_disparity = 1 # meters
    avoidance_range = 1 # meters

    previous_z_distance = 0
    current_z_distance = 0

    # iterate columns on that slice from left to right.
    for x in range(0, slice_cols):
        # iterate each row
        # this can be thought of as the z distance at every x value.
        for z in range(0, slice_rows):
            current_z_distance = math.sqrt(x**2 + z**2)
        
        # check if there is a large enough difference in depth between
        # current and previous z distances,
        if abs(previous_z_distance-current_z_distance) > depth_disparity:
            # assume that we detected the left corner of an obstacle.
            print("Possible obstacle found. Left corner: ({},{})".format(x,z))
            obstacle_vector = get_vector(x,z)
            return obstacle_vector
    
    # if it didn't find anything
    return None


def main():
    zed = sl.Camera()

    # Configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Use PERFORMANCE depth mode
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    zed.set_depth_max_range_value(5) # meters

    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Create and set RuntimeParameters
    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
    # Depth confidence parameters
    # runtime_parameters.confidence_threshold = 100
    # runtime_parameters.textureness_confidence_threshold = 100
    
    image = sl.Mat()
    depth_map = sl.Mat()
    point_cloud = sl.Mat()
    depth_image = sl.Mat()

    mirror_ref = sl.Transform()
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))
    tr_np = mirror_ref.m

    while True:
        # A new image is available if grab() returns SUCCESS
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZ)
            # zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            # zed.retrieve_image(depth_image, sl.VIEW.DEPTH)

            ####################################################################
            # Experimentation with depth map
            ####################################################################

            # avoidance_distance = 1 # meters
            # total_points_within_distance = 0

            # # Show depth image on screen
            # cv2.imshow("Image", depth_image.get_data())
            # key = cv2.waitKey(10)

            # depth_data = depth_map.get_data()
            # np_depth_data = np.array(depth_map.get_data())
            # columns = np_depth_data.shape[1]

            # print(np_depth_data.shape)
            # for x in range(columns):
            #     total_points_within_distance += len(np.where(np_depth_data[:,x] < avoidance_distance)[0]))

            # print("Points within {} meter: {}".format(avoidance_distance, total_points_within_distance))

            # # min number of points before checking point cloud data
            # min_points = 1000
            # # check point cloud data if it looks like there might be an object there
            # if total_points_within_distance > min_points:

            ####################################################################
            # Basic Avoidance by searching a Y slice for depth disparities
            ####################################################################

            # get point cloud
            np_point_cloud = np.array(point_cloud.get_data())
            
            # get y slice at specific y position
            y_slice = get_y_slice(np_point_cloud, -0.3, 0.1)

            print(np.matrix(y_slice))

            # search the y slice
            obstacle_vector = search_for_depth_disparity(y_slice)

            if obstacle_vector != None:
                print(obstacle_vector)
                # call code to drive around obstacle

    zed.close()

if __name__ == "__main__":
    main()
