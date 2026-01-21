#!/usr/bin/env python3
"""Generate secure secrets for JWT and encryption"""
import secrets
import base64

# Generate JWT secret (32 bytes = 256 bits, good for HS256)
jwt_secret = secrets.token_urlsafe(32)
print(f"JWT_SECRET={jwt_secret}")

# Generate encryption key (32 bytes base64 encoded)
encryption_key = base64.b64encode(secrets.token_bytes(32)).decode()
print(f"ENCRYPTION_KEY_BASE64={encryption_key}")

print("\nAdd these to your apps/api/.env file")
