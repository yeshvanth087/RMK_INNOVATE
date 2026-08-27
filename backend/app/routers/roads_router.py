"""
Roads & Quality Rating Router.
Serves road corridor ratings, GeoJSON polylines, and user/engineer rating submissions.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.services.road_rating_service import road_rating_service
from typing import List, Dict, Any

router = APIRouter(prefix="/api/roads", tags=["Road Quality & Safety Ratings"])

class RoadRatingSubmission(BaseModel):
    road_id: str
    rating: float = Field(..., ge=1.0, le=5.0, description="Star rating between 1.0 and 5.0")
    feedback_notes: str = ""

@router.get("/ratings")
async def get_road_ratings() -> List[Dict[str, Any]]:
    """Returns calculated road health scores, grades, colors, and defects for all corridors."""
    return road_rating_service.get_all_road_ratings()

@router.get("/geojson")
async def get_roads_geojson() -> Dict[str, Any]:
    """Returns road corridors formatted as GeoJSON FeatureCollection with color-coded styling properties."""
    roads = road_rating_service.get_all_road_ratings()
    features = []

    for r in roads:
        # GeoJSON LineString coordinates format: [[lng, lat], ...]
        coords = [[p[1], p[0]] for p in r["coordinates"]]
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "road_id": r["road_id"],
                "name": r["name"],
                "segment": r["segment"],
                "length_km": r["length_km"],
                "quality_score": r["quality_score"],
                "grade": r["grade"],
                "star_rating": r["star_rating"],
                "color_hex": r["color_hex"],
                "health_status": r["health_status"],
                "potholes_count": r["potholes_count"],
                "potholes_per_km": r["potholes_per_km"],
                "waterlogging_risk": r["waterlogging_risk"],
                "avg_speed_kmh": r["avg_speed_kmh"],
                "pwd_action": r["pwd_action"],
                "description": r["description"]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.post("/rate")
async def submit_road_rating(submission: RoadRatingSubmission):
    """Allows municipal officers, transport planners, or citizens to submit road ratings."""
    updated = road_rating_service.update_citizen_rating(submission.road_id, submission.rating)
    if not updated:
        raise HTTPException(status_code=404, detail="Road corridor not found")
    return {
        "status": "RATING_RECORDED",
        "road_id": submission.road_id,
        "updated_road": updated,
        "message": f"Feedback submitted successfully for {updated['name']}. New composite score: {updated['quality_score']}/100 ({updated['grade']})"
    }
