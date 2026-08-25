"""
Traffic Density & Bottleneck Counter Engine
Multi-class vehicle counting and Passenger Car Unit (PCU) weighted density calculation.
"""
from typing import Dict, Any
import random

class TrafficDensityCounter:
    # Standard PCU (Passenger Car Unit) weights for Indian urban traffic conditions
    PCU_WEIGHTS = {
        "two_wheeler": 0.5,
        "auto_rickshaw": 0.8,
        "car": 1.0,
        "lcv": 1.5,
        "bus": 3.0,
        "truck": 3.0
    }

    def __init__(self):
        pass

    def estimate_density(self, current_speed_kmh: float, area_context: str = "urban_arterial") -> Dict[str, Any]:
        """
        Estimates real-time vehicle counts, total PCU, and traffic density level.
        """
        # Baseline counts conditioned on current bus speed (lower speed => higher congestion)
        if current_speed_kmh < 10.0:
            # Heavy traffic / Bottleneck
            two_wheeler = random.randint(15, 30)
            auto = random.randint(6, 14)
            car = random.randint(10, 25)
            bus = random.randint(2, 5)
            truck = random.randint(1, 4)
        elif current_speed_kmh < 25.0:
            # Moderate traffic
            two_wheeler = random.randint(8, 18)
            auto = random.randint(3, 8)
            car = random.randint(5, 14)
            bus = random.randint(1, 3)
            truck = random.randint(0, 2)
        else:
            # Free flow
            two_wheeler = random.randint(2, 8)
            auto = random.randint(1, 4)
            car = random.randint(2, 8)
            bus = random.randint(0, 2)
            truck = random.randint(0, 1)

        counts = {
            "two_wheeler": two_wheeler,
            "auto_rickshaw": auto,
            "car": car,
            "bus": bus,
            "truck": truck
        }

        # Calculate Total PCU
        total_pcu = sum(counts[v] * self.PCU_WEIGHTS[v] for v in counts)

        # Density Category & Bottleneck Alert
        if total_pcu > 40.0:
            density_level = "CRITICAL_BOTTLENECK"
            is_bottleneck = True
        elif total_pcu > 25.0:
            density_level = "HEAVY"
            is_bottleneck = current_speed_kmh < 12.0
        elif total_pcu > 12.0:
            density_level = "MODERATE"
            is_bottleneck = False
        else:
            density_level = "FREE_FLOW"
            is_bottleneck = False

        return {
            "vehicle_counts": counts,
            "total_vehicles": sum(counts.values()),
            "total_pcu": round(total_pcu, 2),
            "density_level": density_level,
            "is_bottleneck": is_bottleneck
        }
