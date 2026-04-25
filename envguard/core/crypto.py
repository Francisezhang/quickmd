"""AES-256-GCM encryption/decryption."""

import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Key derivation parameters
KDF_ITERATIONS = 100000
KEY_LENGTH = 32  # 256 bits
SALT_LENGTH = 16
NONCE_LENGTH = 12  # GCM recommended nonce size


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive encryption key from password using PBKDF2-HMAC-SHA256.

    Args:
        password: User password
        salt: Random salt

    Returns:
        32-byte key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def encrypt(data: str, password: str) -> str:
    """
    Encrypt data with AES-256-GCM.

    Args:
        data: Plaintext data
        password: Encryption password

    Returns:
        Base64-encoded encrypted data (salt + nonce + ciphertext)
    """
    # Generate random salt and nonce
    salt = os.urandom(SALT_LENGTH)
    nonce = os.urandom(NONCE_LENGTH)

    # Derive key
    key = derive_key(password, salt)

    # Encrypt
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data.encode(), None)

    # Combine: salt + nonce + ciphertext
    encrypted = salt + nonce + ciphertext

    # Encode as base64
    return base64.b64encode(encrypted).decode()


def decrypt(encrypted_data: str, password: str) -> str:
    """
    Decrypt data with AES-256-GCM.

    Args:
        encrypted_data: Base64-encoded encrypted data
        password: Decryption password

    Returns:
        Decrypted plaintext
    """
    # Decode base64
    encrypted = base64.b64decode(encrypted_data.encode())

    # Extract salt, nonce, ciphertext
    salt = encrypted[:SALT_LENGTH]
    nonce = encrypted[SALT_LENGTH:SALT_LENGTH + NONCE_LENGTH]
    ciphertext = encrypted[SALT_LENGTH + NONCE_LENGTH:]

    # Derive key
    key = derive_key(password, salt)

    # Decrypt
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext.decode()


def generate_share_password() -> str:
    """Generate a random password for sharing."""
    import secrets
    return secrets.token_urlsafe(16)


def verify_password(encrypted_data: str, password: str) -> bool:
    """
    Verify if password is correct for encrypted data.

    Args:
        encrypted_data: Encrypted data to verify against
        password: Password to verify

    Returns:
        True if password is correct
    """
    try:
        decrypt(encrypted_data, password)
        return True
    except Exception:
        return False