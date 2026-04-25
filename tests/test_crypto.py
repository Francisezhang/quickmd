"""Tests for crypto module."""

import pytest
from envguard.core.crypto import encrypt, decrypt, generate_share_password, verify_password


def test_encrypt_decrypt_cycle():
    """Test encrypt→decrypt content match."""
    data = "AWS_KEY=secret123\nDB_PASS=password"
    password = "test_password_123"

    encrypted = encrypt(data, password)
    decrypted = decrypt(encrypted, password)

    assert decrypted == data


def test_encrypt_produces_different_output():
    """Test encryption produces different output each time (random salt/nonce)."""
    data = "same_data"
    password = "same_password"

    encrypted1 = encrypt(data, password)
    encrypted2 = encrypt(data, password)

    # Should be different due to random salt/nonce
    assert encrypted1 != encrypted2
    # But both decrypt correctly
    assert decrypt(encrypted1, password) == data
    assert decrypt(encrypted2, password) == data


def test_decrypt_wrong_password():
    """Test decrypt with wrong password throws exception."""
    data = "secret_data"
    password = "correct_password"
    wrong_password = "wrong_password"

    encrypted = encrypt(data, password)

    with pytest.raises(Exception):
        decrypt(encrypted, wrong_password)


def test_generate_share_password():
    """Test share password generation."""
    password = generate_share_password()

    # Should be non-empty
    assert password
    # Should be reasonably long
    assert len(password) >= 16


def test_verify_password_correct():
    """Test password verification with correct password."""
    data = "verification_data"
    password = "correct"

    encrypted = encrypt(data, password)

    assert verify_password(encrypted, password) is True


def test_verify_password_wrong():
    """Test password verification with wrong password."""
    data = "verification_data"
    password = "correct"
    wrong = "wrong"

    encrypted = encrypt(data, password)

    assert verify_password(encrypted, wrong) is False


def test_encrypt_empty_string():
    """Test encrypting empty string."""
    data = ""
    password = "password"

    encrypted = encrypt(data, password)
    decrypted = decrypt(encrypted, password)

    assert decrypted == ""


def test_encrypt_unicode():
    """Test encrypting unicode content."""
    data = "API_KEY=密码123\n变量=值"
    password = "password"

    encrypted = encrypt(data, password)
    decrypted = decrypt(encrypted, password)

    assert decrypted == data