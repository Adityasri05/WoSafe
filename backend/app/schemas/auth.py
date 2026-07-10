"""
WoSafe Schemas — Authentication
Request/Response models for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class FirebaseLoginRequest(BaseModel):
    """Login with Firebase ID token."""
    firebase_token: str = Field(..., description="Firebase ID token from client")

    model_config = {"json_schema_extra": {"examples": [{"firebase_token": "eyJhbGciOi..."}]}}


class EmailLoginRequest(BaseModel):
    """Login with email and password."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class PhoneOTPRequest(BaseModel):
    """Request OTP for phone login."""
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$", description="Phone number in E.164 format")


class PhoneOTPVerify(BaseModel):
    """Verify OTP for phone login."""
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    otp_code: str = Field(..., min_length=4, max_length=6)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiry in seconds")
    user_id: str
    role: str


class RefreshTokenRequest(BaseModel):
    """Refresh an access token."""
    refresh_token: str = Field(..., description="Valid refresh token")


class LogoutRequest(BaseModel):
    """Logout and invalidate token."""
    refresh_token: str | None = Field(None, description="Optional refresh token to invalidate")
