# EnvGuard

**Cross-platform encrypted .env backup — AES-256-GCM, cloud sync**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## Quick Start

```bash
# Install
pip install envguard

# Scan for exposed .env files
envguard scan ~/projects

# Encrypt and backup
envguard add .env --name production

# Retrieve when needed
envguard get production
```

## Features

- **AES-256-GCM encryption** — military-grade security
- Scan projects for exposed credentials
- Warn if .env not in .gitignore
- **Cross-platform cloud sync**: iCloud (macOS), OneDrive (Windows), Dropbox (Linux)
- Team sharing with independent passwords
- Cross-platform: macOS, Windows, Linux

## Documentation

- [Full Documentation (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## License

MIT License — Free to use, modify, and distribute.

---

**Made by [Francisezhang](https://github.com/Francisezhang)**