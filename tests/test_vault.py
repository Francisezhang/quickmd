"""Tests for vault module."""

import pytest
from pathlib import Path
import tempfile
import json

from envguard.core.vault import (
    load_manifest,
    save_manifest,
    add_to_vault,
    list_entries,
    get_entry,
    delete_entry,
    init_vault,
    verify_master_password,
    get_entry_content,
)


@pytest.fixture(autouse=True)
def temp_vault():
    """Use temporary vault for tests."""
    temp_dir = Path(tempfile.mkdtemp())

    import envguard.core.vault as vault_module
    vault_module.ENVGUARD_DIR = temp_dir
    vault_module.VAULT_DIR = temp_dir / "vault"
    vault_module.MANIFEST_FILE = temp_dir / "manifest.json"

    yield

    vault_module.ENVGUARD_DIR = Path.home() / ".envguard"
    vault_module.VAULT_DIR = vault_module.ENVGUARD_DIR / "vault"
    vault_module.MANIFEST_FILE = vault_module.ENVGUARD_DIR / "manifest.json"


def test_init_vault():
    """Test vault initialization."""
    success = init_vault("master_password")

    assert success
    assert (Path.home() / ".envguard" / ".verification").exists() or \
           Path(tempfile.gettempdir()).glob("*verification")


def test_verify_master_password():
    """Test master password verification."""
    init_vault("correct_password")

    assert verify_master_password("correct_password") is True
    assert verify_master_password("wrong_password") is False


def test_load_manifest_empty():
    """Test loading empty manifest."""
    manifest = load_manifest()

    assert "entries" in manifest
    assert manifest["entries"] == []


def test_save_and_load_manifest():
    """Test saving and loading manifest."""
    manifest = {"entries": [{"id": "test123"}]}
    save_manifest(manifest)

    loaded = load_manifest()
    assert loaded["entries"][0]["id"] == "test123"


def test_add_to_vault():
    """Test adding entry to vault."""
    from envguard.core.crypto import encrypt

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY=value")
        filepath = Path(f.name)

    encrypted = encrypt("KEY=value", "password")

    entry = add_to_vault(filepath, encrypted, name="test_env", project="test_project")

    assert entry["id"]
    assert entry["name"] == "test_env"
    assert entry["project"] == "test_project"

    # Cleanup
    filepath.unlink()


def test_list_entries():
    """Test listing entries."""
    from envguard.core.crypto import encrypt

    entries = list_entries()
    assert entries == []

    # Add entry
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY=value")
        filepath = Path(f.name)

    encrypted = encrypt("KEY=value", "password")
    add_to_vault(filepath, encrypted)

    entries = list_entries()
    assert len(entries) >= 1

    filepath.unlink()


def test_get_entry_by_id():
    """Test getting entry by ID."""
    from envguard.core.crypto import encrypt

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY=value")
        filepath = Path(f.name)

    encrypted = encrypt("KEY=value", "password")
    entry = add_to_vault(filepath, encrypted, name="my_env")

    found = get_entry(entry["id"])
    assert found["id"] == entry["id"]

    filepath.unlink()


def test_get_entry_by_name():
    """Test getting entry by name."""
    from envguard.core.crypto import encrypt

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY=value")
        filepath = Path(f.name)

    encrypted = encrypt("KEY=value", "password")
    add_to_vault(filepath, encrypted, name="unique_name")

    found = get_entry("unique_name")
    assert found["name"] == "unique_name"

    filepath.unlink()


def test_get_entry_not_found():
    """Test getting non-existent entry."""
    found = get_entry("nonexistent")
    assert found is None


def test_delete_entry():
    """Test deleting entry."""
    from envguard.core.crypto import encrypt

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY=value")
        filepath = Path(f.name)

    encrypted = encrypt("KEY=value", "password")
    entry = add_to_vault(filepath, encrypted)

    success = delete_entry(entry["id"])
    assert success

    found = get_entry(entry["id"])
    assert found is None

    filepath.unlink()


def test_get_entry_content():
    """Test decrypting entry content."""
    from envguard.core.crypto import encrypt

    content = "API_KEY=secret123"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content)
        filepath = Path(f.name)

    password = "test_password"
    encrypted = encrypt(content, password)
    entry = add_to_vault(filepath, encrypted)

    decrypted = get_entry_content(entry, password)
    assert decrypted == content

    filepath.unlink()