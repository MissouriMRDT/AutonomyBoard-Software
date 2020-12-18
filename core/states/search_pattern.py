import core
import algorithms
import interfaces
import asyncio
from core.states import RoverState


class SearchPattern(RoverState):
    """
    The goal of this state is to navigate to the GPS coordinates provided by base station in succession, the last of which is the coordinate provided by the judges for that leg of the task.
    Coordinates before the last are simply the operators in base station’s best guess of the best path for the rover due to terrain identified on RED’s map.
    """

    def on_event(self, event) -> RoverState:
        """
        Defines all transitions between states based on events
        """
        if event == core.MARKER_SIGHTED:
            # return core.states.ApproachingMarker()
            pass

        elif event == core.START:
            return core.states.SearchPattern()

        elif event == core.ABORT:
            return core.states.Idle()

        else:
            return core.states.Idle()

    async def run(self) -> RoverState:
        """
        Defines regular rover operation when under this state
        """
        gps_data = core.waypoints.get_waypoint()

        goal, start = gps_data.data()
        current = interfaces.nav_board.location()

        self.logger.debug(
            f"Searching: Location ({interfaces.nav_board._location[0]}, {interfaces.nav_board._location[1]}) to Goal ({goal[0]}, {goal[1]})"
        )

        # Call Track AR Tag code here
        found_tag = False
        center, radius = 0, 0

        if found_tag:
            interfaces.drive_board.stop()

            # Sleep for a brief second
            await asyncio.sleep(0.1)

            self.logger.info("Marker seen at %s with r=%i, locking on..." % (center, radius))
            return self.on_event(core.MARKER_SIGHTED)

        if (
            algorithms.gps_navigate.get_approach_status(goal, current, start)
            != core.constants.ApproachState.APPROACHING
        ):
            interfaces.drive_board.stop()

            # Sleep for a little bit before we move to the next point, allows for AR Tag to be picked up
            await asyncio.sleep(0.1)

            # Find and set the next goal in the search pattern
            goal = algorithms.marker_search.calculate_next_coordinate(start, goal)
            core.waypoints.set_goal(goal)

            self.logger.info(f"Searching: Adding New Waypoint ({goal[0]}, {goal[1]}")

        left, right = algorithms.gps_navigate.calculate_move(goal, current, start, core.constants.DRIVE_POWER)

        self.logger.debug(f"Navigating: Driving at ({left}, {right})")
        interfaces.drive_board.send_drive(left, right)

        return self
