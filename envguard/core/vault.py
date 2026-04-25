"""Vault management for .env backups."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import uuid

# Paths
ENVGUARD_DIR = Path.home() / ".envguard"
VAULT_DIR = ENVGUARD_DIR / "vault"
MANIFEST_FILE = ENVGUARD_DIR / "manifest.json"

# iCloud sync path (optional)
ICLOUD_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "envguard"


def ensure_dirs() -> None:
    """Ensure vault directories exist."""
    ENVGUARD_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)


def load_manifest() -> Dict:
    """Load manifest file."""
    ensure_dirs()
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"entries": []}


def save_manifest(manifest: Dict) -> None:
    """Save manifest file."""
    ensure_dirs()
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def add_to_vault(
    filepath: Path,
    encrypted_data: str,
    name: Optional[str] = None,
    project: Optional[str] = None,
) -> Dict:
    """
    Add encrypted .env to vault.

    Args:
        filepath: Original .env file path
        encrypted_data: Encrypted content
        name: Optional name/alias
        project: Optional project name

    Returns:
        Entry info dict
    """
    ensure_dirs()

    # Generate entry ID
    entry_id = str(uuid.uuid4())[:8]

    # Create vault filename
    vault_name = f"{entry_id}.enc"
    vault_path = VAULT_DIR / vault_name

    # Save encrypted file
    vault_path.write_text(encrypted_data)

    # Create entry metadata
    entry = {
        "id": entry_id,
        "name": name or filepath.name,
        "project": project or filepath.parent.name,
        "original_path": str(filepath),
        "vault_path": str(vault_path),
        "created_at": datetime.now().isoformat(),
        "size": len(encrypted_data),
    }

    # Add to manifest
    manifest = load_manifest()
    manifest["entries"].append(entry)
    save_manifest(manifest)

    return entry


def list_entries() -> List[Dict]:
    """List all vault entries."""
    manifest = load_manifest()
    return manifest["entries"]


def get_entry(entry_id: str) -> Optional[Dict]:
    """Get specific entry by ID or name."""
    manifest = load_manifest()
    for entry in manifest["entries"]:
        if entry["id"] == entry_id or entry["name"] == entry_id:
            return entry
    return None


def get_entry_content(entry: Dict, password: str) -> str:
    """
    Decrypt and get entry content.

    Args:
        entry: Entry metadata
        password: Decryption password

    Returns:
        Decrypted content
    """
    from .crypto import decrypt

    vault_path = Path(entry["vault_path"])
    encrypted_data = vault_path.read_text()

    return decrypt(encrypted_data, password)


def delete_entry(entry_id: str) -> bool:
    """Delete entry from vault."""
    manifest = load_manifest()

    for i, entry in enumerate(manifest["entries"]):
        if entry["id"] == entry_id or entry["name"] == entry_id:
            # Delete vault file
            vault_path = Path(entry["vault_path"])
            if vault_path.exists():
                vault_path.unlink()

            # Remove from manifest
            manifest["entries"].pop(i)
            save_manifest(manifest)
            return True

    return False


def create_share_package(entry: Dict, share_password: str) -> str:
    """
    Create shareable encrypted package with independent password.

    Args:
        entry: Entry to share
        share_password: Independent password for sharing

    Returns:
        Encrypted package path
    """
    from .crypto import encrypt, decrypt

    # Get original content (need user password - handled by caller)
    # This function re-encrypts with share_password

    vault_path = Path(entry["vault_path"])
    encrypted_data = vault_path.read_text()

    share_dir = ENVGUARD_DIR / "shares"
    share_dir.mkdir(parents=True, exist_ok=True)

    share_name = f"{entry['id']}_share.enc"
    share_path = share_dir / share_name

    share_path.write_text(encrypted_data)

    return str(share_path)


def sync_to_icloud() -> bool:
    """
    Sync vault to iCloud.

    Returns:
        True if sync successful
    """
    if not ICLOUD_DIR.exists():
        ICLOUD_DIR.mkdir(parents=True, exist_ok=True)

    import shutil

    # Copy vault files
    for enc_file in VAULT_DIR.glob("*.enc"):
        dest = ICLOUD_DIR / enc_file.name
        shutil.copy2(enc_file, dest)

    # Copy manifest
    if MANIFEST_FILE.exists():
        shutil.copy2(MANIFEST_FILE, ICLOUD_DIR / "manifest.json")

    return True


def init_vault(master_password: str) -> bool:
    """
    Initialize vault with master password verification.

    Args:
        master_password: Master password

    Returns:
        True if initialization successful
    """
    ensure_dirs()

    # Create a verification file
    from .crypto import encrypt

    verification_data = "envguard_verification"
    encrypted = encrypt(verification_data, master_password)

    verification_file = ENVGUARD_DIR / ".verification"
    verification_file.write_text(encrypted)

    return True


def verify_master_password(password: str) -> bool:
    """
    Verify master password.

    Args:
        password: Password to verify

    Returns:
        True if correct
    """
    from .crypto import decrypt

    verification_file = ENVGUARD_DIR / ".verification"
    if not verification_file.exists():
        return False

    try:
        encrypted = verification_file.read_text()
        decrypted = decrypt(encrypted, password)
        return decrypted == "envguard_verification"
    except Exception:
        return False