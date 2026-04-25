# EnvGuard .env加密备份工具

**macOS .env文件加密备份和分享工具 — AES-256-GCM加密，iCloud同步**

## 简介

EnvGuard 使用 AES-256-GCM 加密安全备份你的 .env 文件。再也不怕丢失敏感配置数据。

**核心功能：**
- AES-256-GCM 加密
- PBKDF2-HMAC-SHA256 密钥派生（10万次迭代）
- iCloud 同步支持
- 团队分享（独立密码）
- 自动检测高风险内容（AWS密钥、私钥等）
- 警告不在.gitignore中的.env文件
- 扫描.env文件

## 安装

```bash
cd envguard
pip install -e .
```

## 快速上手

```bash
# 初始化保险库
envguard init

# 添加.env文件
envguard add .env

# 列出所有备份
envguard list

# 获取备份内容
envguard get <名称>

# 扫描.env文件
envguard scan ~/project
```

## 命令详解

### `envguard init`

初始化保险库并设置主密码。

创建：
- 保险库目录：`~/.envguard/vault`
- 清单文件：`~/.envguard/manifest.json`
- 可选 iCloud 同步

### `envguard add <文件路径>`

添加.env文件到保险库。

选项：
- `-n, --name`: 名称别名
- `-p, --project`: 项目名

### `envguard list`

列出所有保险库条目（不显示明文）。

### `envguard get <名称或ID>`

解密并获取条目内容。

选项：
- `-o, --output`: 保存到文件
- `--stdout`: 输出到终端

### `envguard scan <目录>`

扫描目录中的.env文件。

显示：
- 文件路径
- 变量数量
- 高风险警告
- .gitignore状态

### `envguard share <名称>`

创建可分享的加密包（独立密码）。

分享密码独立于主密码，适合团队分享。

### `envguard delete <名称或ID>`

从保险库删除条目。

### `envguard sync`

同步保险库到 iCloud。

## 安全特性

- **加密算法**: AES-256-GCM
- **密钥派生**: PBKDF2-HMAC-SHA256，10万次迭代
- **密码输入**: 使用`getpass`（不回显）
- **无明文存储**: 主密码永不存储

## 存储

- 保险库：`~/.envguard/vault/*.enc`
- 清单：`~/.envguard/manifest.json`
- iCloud：`~/Library/Mobile Documents/com~apple~CloudDocs/envguard/`

## 系统要求

- Python 3.9+
- macOS
- cryptography 库

## 许可证

MIT License

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**