"""
WoSafe AI Engine — Emergency Detector
Multi-signal emergency detection from text, voice transcriptions, and sensor data.
"""

import re
from datetime import UTC, datetime

from loguru import logger


# Emergency keyword categories with severity weights
EMERGENCY_PATTERNS = {
    "critical": {
        "weight": 1.0,
        "keywords": [
            "help me", "i'm being attacked", "someone is attacking me",
            "kidnapped", "abducted", "held hostage", "gun", "knife", "weapon",
            "shot", "stabbed", "rape", "sexual assault", "call 911", "call police",
            "i'm going to die", "he's going to kill me", "she's going to kill me",
            "i can't escape", "locked in", "tied up", "bleeding",
        ],
    },
    "high": {
        "weight": 0.8,
        "keywords": [
            "i'm being followed", "someone is following me", "i'm scared",
            "i'm in danger", "stalker", "threatening me", "i need help",
            "chasing me", "won't leave me alone", "harassing me",
            "blocked my path", "grabbed me", "touched me",
            "i'm trapped", "can't get away", "surrounded",
        ],
    },
    "moderate": {
        "weight": 0.5,
        "keywords": [
            "feel unsafe", "uncomfortable", "suspicious person",
            "strange man", "dark area", "alone at night", "lost",
            "no one around", "area feels dangerous", "emergency",
            "creepy", "watching me", "staring at me",
        ],
    },
    "low": {
        "weight": 0.3,
        "keywords": [
            "worried", "nervous", "anxious", "not sure if safe",
            "heard noise", "something feels wrong", "uneasy",
        ],
    },
}

# Safe word patterns (user-configurable, these are defaults)
DEFAULT_SAFE_WORDS = ["pineapple", "butterfly", "red alert", "code red"]


class EmergencyDetector:
    """Multi-signal emergency detection engine."""

    def __init__(self):
        # Compile regex patterns for efficient matching
        self._patterns: dict[str, list[re.Pattern]] = {}
        for severity, data in EMERGENCY_PATTERNS.items():
            self._patterns[severity] = [
                re.compile(re.escape(kw), re.IGNORECASE)
                for kw in data["keywords"]
            ]

    def detect(self, text: str, user_safe_word: str | None = None) -> dict:
        """
        Analyze text for emergency signals.

        Returns:
            - is_emergency: bool
            - severity: critical/high/moderate/low/none
            - confidence: 0-1.0
            - matched_signals: list of matched emergency patterns
            - safe_word_triggered: bool
            - recommended_action: str
        """
        text_lower = text.lower().strip()
        if not text_lower:
            return self._no_emergency()

        matched_signals = []
        max_weight = 0.0
        detected_severity = "none"

        # Check safe word first (highest priority)
        safe_word_triggered = False
        safe_words = DEFAULT_SAFE_WORDS.copy()
        if user_safe_word:
            safe_words.append(user_safe_word.lower())

        for sw in safe_words:
            if sw.lower() in text_lower:
                safe_word_triggered = True
                matched_signals.append({
                    "signal": f"Safe word detected: '{sw}'",
                    "severity": "critical",
                    "weight": 1.0,
                })
                max_weight = 1.0
                detected_severity = "critical"
                break

        # Check emergency keyword patterns
        for severity, patterns in self._patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    weight = EMERGENCY_PATTERNS[severity]["weight"]
                    matched_signals.append({
                        "signal": pattern.pattern,
                        "severity": severity,
                        "weight": weight,
                    })
                    if weight > max_weight:
                        max_weight = weight
                        detected_severity = severity

        # Calculate confidence
        signal_count = len(matched_signals)
        confidence = min(1.0, max_weight * (1 + 0.1 * (signal_count - 1))) if signal_count > 0 else 0.0

        is_emergency = detected_severity in ("critical", "high") or safe_word_triggered

        return {
            "is_emergency": is_emergency,
            "severity": detected_severity,
            "confidence": round(confidence, 2),
            "matched_signals": matched_signals[:10],  # Limit to 10 signals
            "safe_word_triggered": safe_word_triggered,
            "signal_count": signal_count,
            "recommended_action": self._get_recommended_action(detected_severity, safe_word_triggered),
            "detected_at": datetime.now(UTC).isoformat(),
        }

    def detect_from_sensors(self, sensor_data: dict) -> dict:
        """
        Detect emergency from device sensor data.

        Sensor signals:
            - sudden_stop: bool (movement suddenly stopped)
            - fall_detected: bool (accelerometer fall detection)
            - shake_pattern: bool (violent shaking detected)
            - noise_level_db: float (ambient noise level)
            - heart_rate_elevated: bool (from wearable)
            - battery_critical: bool (battery < 5%)
        """
        signals = []
        severity = "none"
        max_weight = 0.0

        if sensor_data.get("fall_detected"):
            signals.append({"signal": "Fall detected (accelerometer)", "severity": "high", "weight": 0.8})
            max_weight = max(max_weight, 0.8)
            severity = "high"

        if sensor_data.get("shake_pattern"):
            signals.append({"signal": "Violent shaking pattern", "severity": "high", "weight": 0.7})
            max_weight = max(max_weight, 0.7)
            if severity != "critical":
                severity = "high"

        if sensor_data.get("sudden_stop"):
            signals.append({"signal": "Sudden movement stop", "severity": "moderate", "weight": 0.5})
            max_weight = max(max_weight, 0.5)
            if severity == "none":
                severity = "moderate"

        noise_db = sensor_data.get("noise_level_db", 0)
        if noise_db > 90:
            signals.append({"signal": f"High noise level: {noise_db}dB (screaming detected)", "severity": "high", "weight": 0.75})
            max_weight = max(max_weight, 0.75)
            severity = "high"

        if sensor_data.get("heart_rate_elevated"):
            signals.append({"signal": "Elevated heart rate detected", "severity": "moderate", "weight": 0.4})

        if sensor_data.get("battery_critical"):
            signals.append({"signal": "Battery critically low", "severity": "low", "weight": 0.2})

        is_emergency = severity in ("critical", "high")

        return {
            "is_emergency": is_emergency,
            "severity": severity,
            "confidence": round(max_weight, 2),
            "matched_signals": signals,
            "safe_word_triggered": False,
            "signal_count": len(signals),
            "recommended_action": self._get_recommended_action(severity, False),
            "detected_at": datetime.now(UTC).isoformat(),
        }

    def _get_recommended_action(self, severity: str, safe_word: bool) -> str:
        if safe_word or severity == "critical":
            return "TRIGGER_SOS_IMMEDIATELY"
        elif severity == "high":
            return "ALERT_EMERGENCY_CONTACTS"
        elif severity == "moderate":
            return "ACTIVATE_GUARDIAN_MODE"
        elif severity == "low":
            return "SUGGEST_SAFETY_CHECK"
        return "NO_ACTION"

    def _no_emergency(self) -> dict:
        return {
            "is_emergency": False,
            "severity": "none",
            "confidence": 0.0,
            "matched_signals": [],
            "safe_word_triggered": False,
            "signal_count": 0,
            "recommended_action": "NO_ACTION",
            "detected_at": datetime.now(UTC).isoformat(),
        }


# Singleton
emergency_detector = EmergencyDetector()
