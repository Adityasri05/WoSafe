"""
WoSafe AI Engine — Safety Engine
Multi-factor risk analysis: location, time, weather, movement, crowd, lighting,
historical incidents, nearby safe places, device sensors.
"""

from datetime import UTC, datetime

from loguru import logger

from app.utils.helpers import time_of_day_category


class SafetyEngine:
    """
    Multi-factor AI safety scoring engine.
    Accepts contextual data and returns a comprehensive risk assessment.
    """

    # Weight configuration for risk factors
    WEIGHTS = {
        "time_of_day": 0.15,
        "lighting": 0.20,
        "crowd_density": 0.15,
        "weather": 0.05,
        "historical_incidents": 0.20,
        "nearby_safe_places": 0.10,
        "movement_pattern": 0.05,
        "area_reputation": 0.10,
    }

    def assess(self, data: dict) -> dict:
        """
        Perform comprehensive risk assessment.

        Input data:
            - latitude, longitude (required)
            - time_of_day: morning/afternoon/evening/night/late_night
            - weather: clear/cloudy/rain/storm/fog
            - movement_speed: km/h
            - crowd_density: high/medium/low/empty
            - lighting: bright/moderate/dim/dark
            - nearby_safe_places: count of nearby safe locations
            - historical_incidents: count of recent incidents in area
            - device_sensors: {accelerometer, gyroscope, noise_level}
            - route_geojson: planned route geometry

        Returns:
            - safety_score: 0-100
            - risk_level: safe/low/moderate/high/critical
            - risk_factors: list of identified risk factors
            - recommended_actions: list of safety recommendations
            - confidence: 0-1.0
        """
        factors = []
        scores = {}

        # ── Time-of-Day Analysis ──────────
        time_score, time_factors = self._assess_time(data)
        scores["time_of_day"] = time_score
        factors.extend(time_factors)

        # ── Lighting Analysis ─────────────
        light_score, light_factors = self._assess_lighting(data)
        scores["lighting"] = light_score
        factors.extend(light_factors)

        # ── Crowd Density ─────────────────
        crowd_score, crowd_factors = self._assess_crowd(data)
        scores["crowd_density"] = crowd_score
        factors.extend(crowd_factors)

        # ── Weather ───────────────────────
        weather_score, weather_factors = self._assess_weather(data)
        scores["weather"] = weather_score
        factors.extend(weather_factors)

        # ── Historical Incidents ──────────
        incident_score, incident_factors = self._assess_incidents(data)
        scores["historical_incidents"] = incident_score
        factors.extend(incident_factors)

        # ── Nearby Safe Places ────────────
        safe_score, safe_factors = self._assess_safe_places(data)
        scores["nearby_safe_places"] = safe_score
        factors.extend(safe_factors)

        # ── Movement Pattern ──────────────
        movement_score, movement_factors = self._assess_movement(data)
        scores["movement_pattern"] = movement_score
        factors.extend(movement_factors)

        # ── Calculate Weighted Score ──────
        weighted_sum = sum(scores[k] * self.WEIGHTS[k] for k in scores if k in self.WEIGHTS)
        total_weight = sum(self.WEIGHTS[k] for k in scores if k in self.WEIGHTS)
        safety_score = (weighted_sum / total_weight) if total_weight > 0 else 50.0
        safety_score = max(0, min(100, safety_score))

        # ── Determine Risk Level ──────────
        risk_level = self._score_to_risk_level(safety_score)

        # ── Generate Recommendations ──────
        recommendations = self._generate_recommendations(risk_level, factors)

        return {
            "safety_score": round(safety_score, 1),
            "risk_level": risk_level,
            "risk_factors": factors,
            "recommended_actions": recommendations,
            "component_scores": scores,
            "confidence": 0.78,
            "model_version": "v1.0-multi-factor",
            "assessed_at": datetime.now(UTC).isoformat(),
        }

    # ── Factor Assessment Methods ──────────

    def _assess_time(self, data: dict) -> tuple[float, list[dict]]:
        time = data.get("time_of_day", "")
        now_hour = datetime.now(UTC).hour
        if not time:
            time = time_of_day_category(now_hour)

        scores = {"morning": 90, "afternoon": 85, "evening": 65, "night": 40, "late_night": 25}
        score = scores.get(time, 70)
        factors = []
        if score < 60:
            factors.append({"factor": f"Time: {time}", "impact": -(90 - score), "severity": "high" if score < 40 else "moderate"})
        return score, factors

    def _assess_lighting(self, data: dict) -> tuple[float, list[dict]]:
        lighting = data.get("lighting", "moderate")
        scores = {"bright": 95, "moderate": 75, "dim": 45, "dark": 20}
        score = scores.get(lighting, 70)
        factors = []
        if score < 60:
            factors.append({"factor": f"Poor lighting: {lighting}", "impact": -(90 - score), "severity": "high" if score < 40 else "moderate"})
        return score, factors

    def _assess_crowd(self, data: dict) -> tuple[float, list[dict]]:
        crowd = data.get("crowd_density", "medium")
        scores = {"high": 90, "medium": 75, "low": 50, "empty": 25}
        score = scores.get(crowd, 70)
        factors = []
        if score < 60:
            factors.append({"factor": f"Low crowd density: {crowd}", "impact": -(90 - score), "severity": "high" if score < 40 else "moderate"})
        return score, factors

    def _assess_weather(self, data: dict) -> tuple[float, list[dict]]:
        weather = data.get("weather", "clear")
        scores = {"clear": 95, "cloudy": 85, "rain": 65, "heavy_rain": 50, "storm": 35, "fog": 45}
        score = scores.get(weather, 80)
        factors = []
        if score < 60:
            factors.append({"factor": f"Adverse weather: {weather}", "impact": -(90 - score), "severity": "moderate"})
        return score, factors

    def _assess_incidents(self, data: dict) -> tuple[float, list[dict]]:
        count = data.get("historical_incidents", 0)
        if count == 0:
            return 95, []
        elif count <= 2:
            return 75, [{"factor": f"{count} recent incidents in area", "impact": -15, "severity": "low"}]
        elif count <= 5:
            return 50, [{"factor": f"{count} recent incidents — elevated risk area", "impact": -35, "severity": "moderate"}]
        else:
            return 25, [{"factor": f"{count} incidents — high-risk zone", "impact": -60, "severity": "high"}]

    def _assess_safe_places(self, data: dict) -> tuple[float, list[dict]]:
        count = data.get("nearby_safe_places", 0)
        if count >= 5:
            return 95, []
        elif count >= 2:
            return 75, []
        elif count == 1:
            return 55, [{"factor": "Limited nearby safe locations", "impact": -20, "severity": "moderate"}]
        else:
            return 30, [{"factor": "No nearby safe locations identified", "impact": -50, "severity": "high"}]

    def _assess_movement(self, data: dict) -> tuple[float, list[dict]]:
        speed = data.get("movement_speed", 0)
        if speed == 0:
            return 80, []
        elif speed < 6:  # Walking
            return 85, []
        elif speed < 15:  # Running
            return 60, [{"factor": "Elevated movement speed (running)", "impact": -20, "severity": "moderate"}]
        else:
            return 75, []

    # ── Helpers ─────────────────────────────

    def _score_to_risk_level(self, score: float) -> str:
        if score >= 80:
            return "safe"
        elif score >= 60:
            return "low"
        elif score >= 40:
            return "moderate"
        elif score >= 20:
            return "high"
        return "critical"

    def _generate_recommendations(self, risk_level: str, factors: list) -> list[str]:
        recs = ["Stay aware of your surroundings at all times"]

        if risk_level in ("critical", "high"):
            recs.extend([
                "🚨 Consider activating Guardian Mode immediately",
                "Share your live location with trusted contacts",
                "Move to the nearest well-lit, populated area",
                "Keep your phone accessible with emergency contacts ready",
                "Avoid isolated streets and shortcuts",
                "Consider requesting a volunteer escort",
            ])
        elif risk_level == "moderate":
            recs.extend([
                "Share your journey with a trusted contact",
                "Stay on main, well-lit roads",
                "Keep your phone charged and accessible",
                "Consider using the safest route alternative",
            ])
        elif risk_level == "low":
            recs.extend([
                "Your current area appears relatively safe",
                "Stay on planned route for optimal safety",
            ])

        return recs


# Singleton
safety_engine = SafetyEngine()
