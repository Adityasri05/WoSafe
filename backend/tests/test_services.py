"""
WoSafe Tests — Service Layer Tests
Unit tests for core services: auth, user, journey, emergency, AI.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.core.security import create_access_token, create_refresh_token, verify_access_token, verify_refresh_token, hash_password, verify_password
from app.core.exceptions import AuthenticationError
from app.utils.helpers import haversine_distance, time_of_day_category, time_ago, paginate
from app.security.validation import sanitize_input, validate_phone, validate_email, validate_coordinates


class TestSecurityUtils:
    """Test JWT and password utilities."""

    def test_password_hash_and_verify(self):
        password = "Str0ng!P@ssw0rd"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_access_token_creation_and_verification(self):
        user_id = uuid4()
        token = create_access_token(subject=user_id, role="user")
        payload = verify_access_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["role"] == "user"
        assert payload["type"] == "access"

    def test_refresh_token_creation_and_verification(self):
        user_id = uuid4()
        token = create_refresh_token(subject=user_id)
        payload = verify_refresh_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_access_token_invalid(self):
        with pytest.raises(AuthenticationError):
            verify_access_token("invalid-token")

    def test_refresh_token_as_access_fails(self):
        user_id = uuid4()
        refresh = create_refresh_token(subject=user_id)
        with pytest.raises(AuthenticationError):
            verify_access_token(refresh)


class TestValidation:
    """Test input validation and sanitization."""

    def test_sanitize_html(self):
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_validate_phone(self):
        assert validate_phone("+1234567890")
        assert validate_phone("+919876543210")
        assert not validate_phone("1234567890")
        assert not validate_phone("")
        assert not validate_phone("+0123456")

    def test_validate_email(self):
        assert validate_email("user@example.com")
        assert validate_email("test.user+tag@domain.co")
        assert not validate_email("invalid")
        assert not validate_email("@domain.com")

    def test_validate_coordinates(self):
        assert validate_coordinates(40.7128, -74.0060)
        assert validate_coordinates(0, 0)
        assert validate_coordinates(-90, -180)
        assert validate_coordinates(90, 180)
        assert not validate_coordinates(91, 0)
        assert not validate_coordinates(0, 181)


class TestGeoUtils:
    """Test geocoding utilities."""

    def test_haversine_distance_same_point(self):
        assert haversine_distance(40.7128, -74.0060, 40.7128, -74.0060) == 0.0

    def test_haversine_distance_nyc_to_la(self):
        # NYC to LA is approximately 3,940 km
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        assert 3900 < distance < 4000

    def test_time_of_day_category(self):
        assert time_of_day_category(8) == "morning"
        assert time_of_day_category(14) == "afternoon"
        assert time_of_day_category(19) == "evening"
        assert time_of_day_category(22) == "night"
        assert time_of_day_category(3) == "late_night"

    def test_pagination(self):
        result = paginate(total=95, page=2, page_size=20)
        assert result["total"] == 95
        assert result["total_pages"] == 5
        assert result["has_next"] is True
        assert result["has_prev"] is True

    def test_pagination_last_page(self):
        result = paginate(total=95, page=5, page_size=20)
        assert result["has_next"] is False
        assert result["has_prev"] is True

    def test_pagination_first_page(self):
        result = paginate(total=50, page=1, page_size=20)
        assert result["has_next"] is True
        assert result["has_prev"] is False
