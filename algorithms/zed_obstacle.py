import pyzed.sl as sl
import math
import numpy as np
import sys

def main():
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Use PERFORMANCE depth mode
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD720

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Create and set RuntimeParameters after opening the camera
    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
    # Setting the depth confidence parameters
    runtime_parameters.confidence_threshold = 100
    runtime_parameters.textureness_confidence_threshold = 100

    # Capture 150 images and depth, then stop
    i = 0
    point_cloud = sl.Mat()

    mirror_ref = sl.Transform()
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))
    tr_np = mirror_ref.m

    while i < 150: # TODO: Set this to run while rover is roving
        # A new image is available if grab() returns SUCCESS
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Retrieve colored point cloud. Point cloud is aligned on the left image.
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

            # TODO: log what the point cloud looks like
            # TODO: see if we can get xyz data without rgba since we dont need it

            i = round(image.get_width() / 2) # x center
            j = round(image.get_height() / 2) # y center

            # src: https://www.stereolabs.com/docs/depth-sensing/using-depth/
            # Get the 3D point cloud values for pixel (i,j)
            point3D = point_cloud.get_value(i, j)
            x = point3D[0]
            y = point3D[1]
            z = point3D[2]
            color = point3D[3]

            print("3D point cloud value for pixel ({}, {}): x={}, y={}, z={}, color={}".format(i, j, x, y, z, color))

            # Measure the distance of a point in the scene represented by pixel (i,j)
            distance = math.sqrt(point3D[0]*point3D[0] + point3D[1]*point3D[1] + point3D[2]*point3D[2])

            print("Distance: {}".format(distance))

            i += 1

            # TODO: if performance is slow, get lower resolution

            # # Get and print distance value in mm at the center of the image
            # # We measure the distance camera - object using Euclidean distance
            
            # err, point_cloud_value = point_cloud.get_value(x, y)

            # distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
            #                      point_cloud_value[1] * point_cloud_value[1] +
            #                      point_cloud_value[2] * point_cloud_value[2])

            # point_cloud_np = point_cloud.get_data()
            # point_cloud_np.dot(tr_np)

            # if not np.isnan(distance) and not np.isinf(distance):
            #     print("Distance to Camera at ({}, {}) (image center): {:1.3} m".format(x, y, distance), end="\r")
            #     # Increment the loop
            #     i = i + 1
            # else:
            #     print("Can't estimate distance at this position.")
            #     print("Your camera is probably too close to the scene, please move it backwards.\n")
            # sys.stdout.flush()

    # Close the camera
    zed.close()

if __name__ == "__main__":
    main()
