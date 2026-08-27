"""
Road Quality & Safety Rating Service.
Calculates continuous multi-factor Road Health Scores (0-100), Letter Grades, Star Ratings,
and PWD Repair Priorities for all urban transit corridors based on mobile bus fleet sensor observations.
"""
from typing import List, Dict, Any, Optional
from backend.app.database import get_db_connection

# Master Urban Corridors with Polyline GPS Waypoints and Baseline Characteristics
URBAN_CORRIDORS_MASTER = [
    {
        "road_id": "ROAD-01",
        "name": "Anna Salai Arterial Corridor",
        "segment": "Central Station to Guindy Metro",
        "length_km": 11.2,
        "lane_count": 6,
        "speed_limit_kmh": 60,
        "avg_speed_kmh": 22.4,
        "potholes_count": 4,
        "waterlogging_risk": "HIGH",
        "crack_density_pct": 38.0,
        "missing_signage_count": 2,
        "citizen_feedback_rating": 2.4,
        "coordinates": [
            [13.0827, 80.2707],  # Central Station
            [13.0732, 80.2609],  # Egmore
            [13.0569, 80.2425],  # Thousand Lights
            [13.0418, 80.2341],  # T. Nagar
            [13.0102, 80.2157]   # Guindy
        ]
    },
    {
        "road_id": "ROAD-02",
        "name": "Old Mahabalipuram Road (OMR Expressway)",
        "segment": "Adyar Depot to Sholinganallur Hub",
        "length_km": 14.5,
        "lane_count": 6,
        "speed_limit_kmh": 70,
        "avg_speed_kmh": 36.2,
        "potholes_count": 2,
        "waterlogging_risk": "LOW",
        "crack_density_pct": 18.0,
        "missing_signage_count": 1,
        "citizen_feedback_rating": 3.6,
        "coordinates": [
            [13.0067, 80.2575],  # Adyar
            [12.9815, 80.2437],  # Thiruvanmiyur
            [12.9516, 80.2411],  # Kandanchavadi
            [12.9249, 80.2312]   # Sholinganallur
        ]
    },
    {
        "road_id": "ROAD-03",
        "name": "Inner Ring Road (Jawaharlal Nehru Road)",
        "segment": "Saidapet to Anna Nagar Roundtana",
        "length_km": 9.8,
        "lane_count": 6,
        "speed_limit_kmh": 60,
        "avg_speed_kmh": 48.0,
        "potholes_count": 0,
        "waterlogging_risk": "NONE",
        "crack_density_pct": 4.0,
        "missing_signage_count": 0,
        "citizen_feedback_rating": 4.8,
        "coordinates": [
            [13.0210, 80.2230],  # Saidapet
            [13.0418, 80.2341],  # T. Nagar Link
            [13.0612, 80.2285],  # Nungambakkam
            [13.0850, 80.2101]   # Anna Nagar
        ]
    },
    {
        "road_id": "ROAD-04",
        "name": "Poonamallee High Road",
        "segment": "Basin Bridge to CMBT Koyambedu Hub",
        "length_km": 8.6,
        "lane_count": 4,
        "speed_limit_kmh": 50,
        "avg_speed_kmh": 26.5,
        "potholes_count": 3,
        "waterlogging_risk": "MEDIUM",
        "crack_density_pct": 32.0,
        "missing_signage_count": 2,
        "citizen_feedback_rating": 2.9,
        "coordinates": [
            [13.1075, 80.2619],  # Basin Bridge
            [13.0850, 80.2101],  # Anna Nagar East
            [13.0694, 80.1948]   # Koyambedu
        ]
    },
    {
        "road_id": "ROAD-05",
        "name": "Kamarajar Promenade (Marina Beach Road)",
        "segment": "Napier Bridge to Santhome Cathedral",
        "length_km": 6.4,
        "lane_count": 6,
        "speed_limit_kmh": 50,
        "avg_speed_kmh": 42.0,
        "potholes_count": 0,
        "waterlogging_risk": "LOW",
        "crack_density_pct": 8.0,
        "missing_signage_count": 0,
        "citizen_feedback_rating": 4.5,
        "coordinates": [
            [13.0690, 80.2880],  # Napier Bridge
            [13.0499, 80.2824],  # Marina Light House
            [13.0336, 80.2780]   # Santhome
        ]
    },
    {
        "road_id": "ROAD-06",
        "name": "North Commercial Expressway",
        "segment": "Tondiarpet to Chennai Port Gate",
        "length_km": 5.2,
        "lane_count": 4,
        "speed_limit_kmh": 40,
        "avg_speed_kmh": 16.0,
        "potholes_count": 5,
        "waterlogging_risk": "CRITICAL",
        "crack_density_pct": 52.0,
        "missing_signage_count": 3,
        "citizen_feedback_rating": 1.7,
        "coordinates": [
            [13.1250, 80.2920],
            [13.1147, 80.2872],
            [13.0980, 80.2950]
        ]
    }
]

class RoadRatingService:
    @staticmethod
    def compute_road_score(road: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes composite Road Quality & Safety Index (0-100 Score).
        Formula:
        Score = 100 - (Pothole Penalty) - (Waterlogging Penalty) - (Crack Penalty) - (Speed Variance Penalty) + (Citizen Score adjustment)
        """
        pothole_penalty = (road.get("potholes_count", 0) / max(1.0, road["length_km"])) * 30.0
        
        water_penalties = {"NONE": 0, "LOW": 5, "MEDIUM": 15, "HIGH": 25, "CRITICAL": 35}
        water_penalty = water_penalties.get(road.get("waterlogging_risk", "LOW"), 10)
        
        crack_penalty = (road.get("crack_density_pct", 10.0) / 100.0) * 20.0
        
        # Speed efficiency: actual vs speed limit
        speed_ratio = min(1.0, road.get("avg_speed_kmh", 30) / max(1.0, road.get("speed_limit_kmh", 50)))
        speed_penalty = (1.0 - speed_ratio) * 15.0
        
        # Citizen feedback contribution (+- 5 points)
        citizen_bonus = (road.get("citizen_feedback_rating", 3.0) - 3.0) * 2.5

        raw_score = 100.0 - pothole_penalty - water_penalty - crack_penalty - speed_penalty + citizen_bonus
        score = max(10.0, min(100.0, round(raw_score, 1)))

        # Assign Letter Grade, Color Code, Star Rating, and PWD Action
        if score >= 85.0:
            grade = "A"
            stars = 5.0
            color = "#10b981"  # Emerald Green
            status = "EXCELLENT"
            description = "Smooth surface, clear lane markings, zero hazardous potholes."
            pwd_action = "Routine annual audit only"
        elif score >= 70.0:
            grade = "B"
            stars = 4.0
            color = "#06b6d4"  # Electric Cyan
            status = "GOOD"
            description = "Satisfactory surface condition with minor wear."
            pwd_action = "Preventive maintenance scheduled"
        elif score >= 55.0:
            grade = "C"
            stars = 3.0
            color = "#facc15"  # Bright Yellow
            status = "FAIR / MODERATE DEFECTS"
            description = "Moderate surface degradation, surface cracks & occasional potholes."
            pwd_action = "Pothole patch work required in 14 days"
        elif score >= 40.0:
            grade = "D"
            stars = 2.0
            color = "#f97316"  # Bright Orange
            status = "POOR / DEGRADED"
            description = "Frequent potholes, degraded dividers, and reduced transit speeds."
            pwd_action = "High Priority: PWD resurfacing work order issued"
        else:
            grade = "F"
            stars = 1.0
            color = "#ef4444"  # Crimson Red
            status = "CRITICAL / HAZARDOUS"
            description = "Severe road fissures, recurrent waterlogging, high accident hazard."
            pwd_action = "URGENT: Immediate emergency road reconstruction needed"

        return {
            **road,
            "quality_score": score,
            "grade": grade,
            "star_rating": round(stars * (score / 100.0), 1),
            "color_hex": color,
            "health_status": status,
            "description": description,
            "pwd_action": pwd_action,
            "potholes_per_km": round(road.get("potholes_count", 0) / max(1.0, road["length_km"]), 2)
        }

    @classmethod
    def get_all_road_ratings(cls) -> List[Dict[str, Any]]:
        """Returns ratings for all urban transit corridors."""
        return [cls.compute_road_score(r) for r in URBAN_CORRIDORS_MASTER]

    @classmethod
    def update_citizen_rating(cls, road_id: str, new_rating: float) -> Optional[Dict[str, Any]]:
        """Updates road rating with new citizen or engineer score."""
        for r in URBAN_CORRIDORS_MASTER:
            if r["road_id"] == road_id:
                # Rolling weighted average
                current = r.get("citizen_feedback_rating", 3.0)
                r["citizen_feedback_rating"] = round((current * 4.0 + new_rating) / 5.0, 1)
                return cls.compute_road_score(r)
        return None

road_rating_service = RoadRatingService()
