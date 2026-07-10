"""
WoSafe Security — Input Validation, Encryption, and Audit Logging
"""

import base64
import hashlib
import re

import bleach
from cryptography.fernet import Fernet

from app.core.config import settings


# ── Input Validation & Sanitization ────────

def sanitize_html(content: str) -> str:
    """Strip all HTML tags and dangerous content."""
    return bleach.clean(content, tags=[], strip=True)


def sanitize_input(content: str) -> str:
    """Sanitize user input — remove SQL injection patterns and XSS vectors."""
    content = sanitize_html(content)
    # Remove common SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|EXEC)\b)",
        r"(--|;|/\*|\*/)",
        r"(\bOR\b\s+\b1\b\s*=\s*\b1\b)",
    ]
    for pattern in sql_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE)
    return content.strip()


def validate_phone(phone: str) -> bool:
    """Validate E.164 phone number format."""
    return bool(re.match(r"^\+[1-9]\d{1,14}$", phone))


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate geographic coordinates."""
    return -90 <= lat <= 90 and -180 <= lng <= 180


# ── Encryption ─────────────────────────────

def get_encryption_key() -> bytes:
    """Get or derive the encryption key."""
    if settings.ENCRYPTION_KEY:
        key = settings.ENCRYPTION_KEY.encode()
        # Ensure key is 32 bytes for Fernet (base64 of 32 bytes = 44 chars)
        if len(key) < 32:
            key = hashlib.sha256(key).digest()
        return base64.urlsafe_b64encode(key[:32])
    return Fernet.generate_key()


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data using Fernet symmetric encryption."""
    f = Fernet(get_encryption_key())
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt Fernet-encrypted data."""
    f = Fernet(get_encryption_key())
    return f.decrypt(encrypted_data.encode()).decode()


def hash_data(data: str) -> str:
    """Create SHA-256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


# ── File Security ──────────────────────────

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/webm"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def validate_file_type(mime_type: str, allowed_types: set[str]) -> bool:
    """Validate file MIME type."""
    return mime_type in allowed_types


def validate_file_size(size_bytes: int) -> bool:
    """Validate file size against maximum."""
    return size_bytes <= MAX_FILE_SIZE
