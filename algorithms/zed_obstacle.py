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
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZ)
            # zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            # zed.retrieve_image(depth_image, sl.VIEW.DEPTH)

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

            np_point_cloud = np.array(point_cloud.get_data())

            rows = np_point_cloud.shape[0]
            cols = np_point_cloud.shape[1]

            for i in range(0, rows):
                for j in range(0, cols):
                    point3D = point_cloud.get_value(i,j) # [x,y,z]
                    # x = point3D[0]
                    # y = point3D[1]
                    # z = point3D[2]
                    # distance = math.sqrt(point3D[0]*point3D[0] + point3D[1]*point3D[1] + point3D[2]*point3D[2])

                    # ???

            # if obstacle_in_path:
            #     drive_around_obstacle(distance_to_obstacle, angle_to_obstacle)

    zed.close()

if __name__ == "__main__":
    main()