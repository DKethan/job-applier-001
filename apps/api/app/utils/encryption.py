import base64
import os
from cryptography.fernet import Fernet
from app.config import settings


class EncryptionService:
    def __init__(self):
        # Decode base64 key or generate if invalid
        try:
            key_bytes = base64.b64decode(settings.encryption_key_base64)
            if len(key_bytes) != 32:
                raise ValueError("Encryption key must be 32 bytes when base64 decoded")
            # Fernet requires base64-encoded 32-byte key
            self.key = base64.urlsafe_b64encode(key_bytes)
            self.cipher = Fernet(self.key)
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY_BASE64: {e}")

    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt bytes"""
        return self.cipher.encrypt(data)

    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes"""
        return self.cipher.decrypt(encrypted_data)


encryption_service = EncryptionService()
