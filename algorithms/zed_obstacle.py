import pyzed.sl as sl
import math
import numpy as np
import sys
import cv2

def main():
    zed = sl.Camera()

    # Configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Use PERFORMANCE depth mode
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    # zed.set_depth_max_range_value(10) # meters

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
            # zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            zed.retrieve_image(depth_image, sl.VIEW.DEPTH)

            avoidance_distance = 1 # meters
            total_points_within_distance = 0

            cv2.imshow("Image", depth_image.get_data())
            key = cv2.waitKey(10)

            depth_data = depth_map.get_data()
            np_depth_data = np.array(depth_map.get_data())
            columns = np_depth_data.shape[1]

            print(np_depth_data.shape)
            for x in range(columns):
                total_points_within_distance += len(np.where(np_depth_data[:,x] < avoidance_distance)[0]))

            print("Total number of points detected within {} meter: {}".format(avoidance_distance, total_points_within_distance))

            # ---- POINT CLOUD STUFF ----
            # Get and print distance value in mm at the center of the image
            # We measure the distance camera - object using Euclidean distance
            # x = round(image.get_width() / 2)
            # y = round(image.get_height() / 2)
            # err, point_cloud_value = point_cloud.get_value(x, y)

            # distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
            #                      point_cloud_value[1] * point_cloud_value[1] +
            #                      point_cloud_value[2] * point_cloud_value[2])

            # print("Distance: {}".format(distance))

    zed.close()

if __name__ == "__main__":
    main()