"""
Edge AI Detectors Package
Includes modules for road hazards, vehicle traffic density, pedestrian VRU, and ANPR incident detection.
"""
from .road_hazard_detector import RoadHazardDetector
from .traffic_density_counter import TrafficDensityCounter
from .pedestrian_vru_detector import PedestrianVRUDetector
from .anpr_incident_tracker import ANPRIncidentTracker

__all__ = [
    "RoadHazardDetector",
    "TrafficDensityCounter",
    "PedestrianVRUDetector",
    "ANPRIncidentTracker"
]
