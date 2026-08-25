"""
Transit Analytics & Route Optimization Router.
Integrates ML ETA prediction, bottleneck scoring, and OR-Tools detour optimization.
"""
from fastapi import APIRouter
from backend.app.schemas import RouteDelayQuery, DynamicRouteQuery
from backend.app.services.delay_predictor import delay_service
from backend.app.services.gtfs_analyzer import gtfs_analyzer
from backend.app.services.route_optimizer import route_optimizer
from typing import Dict, Any, List

router = APIRouter(prefix="/api/analytics", tags=["Transit Analytics"])

@router.get("/kpis")
async def get_system_kpis() -> Dict[str, Any]:
    """Returns top-level dashboard metrics for the urban transit network."""
    return gtfs_analyzer.get_system_summary_kpis()

@router.get("/bottlenecks")
async def get_corridor_bottlenecks() -> List[Dict[str, Any]]:
    """Returns GTFS corridor bottleneck rankings."""
    return gtfs_analyzer.get_corridor_bottleneck_rankings()

@router.post("/predict-delay")
async def predict_route_delay(query: RouteDelayQuery) -> Dict[str, Any]:
    """Predicts trip delay using ML regression model (Random Forest / XGBoost)."""
    return delay_service.predict_route_delay(
        route_id=query.route_id,
        hour=query.hour_of_day,
        weather=query.weather_condition or "CLEAR",
        crowding_pct=query.current_crowding_pct or 45.0
    )

@router.post("/dynamic-route")
async def calculate_dynamic_route(query: DynamicRouteQuery) -> Dict[str, Any]:
    """Solves dynamic hazard-avoidance detour routing using OR-Tools principles."""
    return route_optimizer.calculate_optimized_route(
        origin_node="NODE_CENTRAL",
        dest_node="NODE_AIRPORT",
        avoid_critical_hazards=query.avoid_hazards
    )
