# Rover State Matrix

||Idle|Navigating|Searching|ApproachingMarker|ObstacleAvoidance|Shutdown|
|---|---|---|---|---|---|---|
|START|Navigating|-|-|-|-|-|
|REACHED_GPS_COORDINATE|-|Searching|-|-|-|-|
|MARKER_SIGHTED|-|-|ApproachingMarker|-|-|-|
|SEARCH_FAILED|-|-|Navigating|-|-|-|
|MARKER_UNSEEN|-|-|-|Searching|-|-|
|REACHED_MARKER|-|-|-|Idle|-|-|
|ALL_MARKERS_REACHED|Idle|-|-|-|-|-|
|ABORT|Shutdown|Shutdown|Shutdown|Shutdown|-|-|
|RESTART|-|-|-|-|-|Idle|
|OBSTACLE_AVOIDANCE|-|-|-|ObstacleAvoidance|-|-|
|END_OBSTACLE_AVOIDANCE|-|-|-|-|-|-|