import logging
import core
from collections import deque
import interfaces


class WaypointHandler:
    def __init__(self):
        # Class variables
        self.waypoints: deque = deque()
        self.gps_data: core.GPSData = None

        core.rovecomm_node.set_callback(
            core.manifest["Autonomy"]["Commands"]["AddWaypoint"]["dataId"], self.add_waypoint
        )
        core.rovecomm_node.set_callback(
            core.manifest["Autonomy"]["Commands"]["ClearWaypoints"]["dataId"], self.clear_waypoints
        )

        self.logger = logging.getLogger(__name__)

    def add_waypoint(self, packet) -> None:
        """
        Adds the data from the packet (expects lat, lon) to the waypoints deque
        """
        latitude, longitude = packet.data
        waypoint = core.Coordinate(latitude, longitude)
        self.waypoints.append(waypoint)
        self.logger.info(f"Added Waypoint: lat ({latitude}), lon({longitude})")

    def clear_waypoints(self):
        """
        Clears the deque of waypoints
        """
        self.waypoints.clear()
        self.logger.info("Cleared all waypoints")

    def get_waypoint(self) -> core.GPSData:
        """
        Gets the current waypoint, pops a new from the deque if we haven't grabbed a
        waypoint from the deque yet
        """
        # Pop off a waypoint from the queue if there is currently none
        if self.gps_data is None:
            return self.get_new_waypoint()

        return self.gps_data

    def set_goal(self, goal):
        """
        Sets the goal of the current waypoint
        """
        # Set the goal to the passed in goal
        self.gps_data.goal = goal

    def set_start(self, start):
        """
        Sets the starting location of the current waypoint
        """
        self.gps_data.start = start

    def is_empty(self) -> bool:
        """
        Returns true if there are more waypoints in the deque
        """
        if self.waypoints:
            return False
        else:
            return True

    def get_new_waypoint(self) -> core.GPSData:
        """
        Grabs a new waypoint from the queue, goal being the data in the deque and start
        being the current perceived location of the rover
        """
        self.gps_data = core.GPSData()
        self.gps_data.start = interfaces.nav_board.location()

        try:
            current_goal = self.waypoints.popleft()
        except IndexError:
            self.logger.error("Tried popping waypoint from empty deque")
            return None

        self.gps_data.goal = current_goal

        self.logger.info(f"Set Waypoint Target: lat ({current_goal.lat}), lon({current_goal.lon})")
        return self.gps_data
