# EnvGuard

**跨平台加密.env备份工具 — AES-256-GCM加密，云同步**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## 快速开始

```bash
# 安装
pip install envguard

# 扫描暴露的.env文件
envguard scan ~/projects

# 加密备份
envguard add .env --name production

# 需要时取回
envguard get production
```

## 功能特点

- **AES-256-GCM加密** — 军事级安全
- 扫描项目中的暴露凭证
- 警告未在.gitignore的.env
- **跨平台云同步**：iCloud (macOS)、OneDrive (Windows)、Dropbox (Linux)
- 团队分享用独立密码
- 跨平台：macOS、Windows、Linux

## 文档

- [完整文档 (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## 许可证

MIT 许可证 — 免费使用、修改和分发。

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**