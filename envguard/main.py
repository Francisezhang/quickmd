"""EnvGuard CLI entry point."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import getpass

from .core.crypto import encrypt, decrypt, generate_share_password, verify_password
from .core.vault import (
    init_vault,
    verify_master_password,
    add_to_vault,
    list_entries,
    get_entry,
    get_entry_content,
    delete_entry,
    sync_to_icloud,
)
from .utils.scanner import scan_directory, analyze_env_file

app = typer.Typer(
    name="envguard",
    help="Encrypted .env file backup and sharing for macOS / .env文件加密备份",
    add_completion=False,
)
console = Console()


def get_password(prompt: str = "Enter password 输入密码") -> str:
    """Get password without echo."""
    return getpass.getpass(f"{prompt}: ")


@app.command("init")
def init_cmd():
    """
    Initialize envguard with master password / 初始化并设置主密码.
    """
    console.print("[yellow]Setting up EnvGuard... 设置中...[/yellow]")

    password = get_password("Set master password 设置主密码")

    if len(password) < 8:
        console.print("[red]Password must be at least 8 characters. 密码至少8位[/red]")
        return

    # Confirm password
    confirm = get_password("Confirm password 确认密码")

    if password != confirm:
        console.print("[red]Passwords don't match. 密码不匹配[/red]")
        return

    success = init_vault(password)

    if success:
        console.print("[green]EnvGuard initialized successfully! 初始化成功[/green]")
        console.print("[blue]Vault location: ~/.envguard/vault[/blue]")

        # Ask about iCloud sync
        console.print("\n[yellow]Enable iCloud sync? (y/N) 启用iCloud同步?[/yellow]")
        response = input("> ").strip().lower()
        if response == "y":
            sync_to_icloud()
            console.print("[green]iCloud sync enabled. 已启用[/green]")
    else:
        console.print("[red]Initialization failed. 初始化失败[/red]")


@app.command("add")
def add_cmd(
    filepath: Path = typer.Argument(..., help=".env file to backup / 要备份的文件"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Entry name/alias / 名称别名"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project name / 项目名"),
):
    """
    Add .env file to vault / 添加.env文件到保险库.
    """
    if not filepath.exists():
        console.print(f"[red]File not found: {filepath}[/red]")
        return

    # Analyze file
    info = analyze_env_file(filepath)

    # Warn about high-risk content
    if info.get("high_risk"):
        console.print(f"[red]⚠️  Warning 警告: High-risk patterns detected![/red]")
        console.print(f"[yellow]Risks: {info['high_risk']}[/yellow]")

    # Warn if not in gitignore
    if not info.get("in_gitignore"):
        console.print(f"[yellow]⚠️  Warning 警告: File not in .gitignore![/yellow]")

    # Get password
    password = get_password()

    # Verify master password
    if not verify_master_password(password):
        console.print("[red]Invalid password. 密码错误[/red]")
        return

    # Encrypt
    content = filepath.read_text()
    encrypted = encrypt(content, password)

    # Add to vault
    entry = add_to_vault(filepath, encrypted, name=name, project=project)

    console.print(f"[green]Added to vault! 已添加[/green]")
    console.print(f"[blue]Entry ID: {entry['id']}[/blue]")
    console.print(f"[blue]Name: {entry['name']}[/blue]")


@app.command("list")
def list_cmd():
    """
    List all vault entries / 列出所有备份.
    """
    entries = list_entries()

    if not entries:
        console.print("[yellow]No entries in vault. 保险库为空[/yellow]")
        return

    table = Table(title="Vault Entries 保险库内容", show_header=True)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Name 名称", style="cyan")
    table.add_column("Project 项目", style="blue")
    table.add_column("Created 创建时间", style="dim")
    table.add_column("Size 大小", style="green")

    for entry in entries:
        table.add_row(
            entry["id"],
            entry["name"],
            entry["project"],
            entry["created_at"][:16],
            f"{entry['size']} bytes",
        )

    console.print(table)


@app.command("get")
def get_cmd(
    name_or_id: str = typer.Argument(..., help="Entry name or ID / 名称或ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file / 输出文件"),
    stdout: bool = typer.Option(False, "--stdout", help="Print to stdout / 输出到终端"),
):
    """
    Get and decrypt entry / 获取并解密.
    """
    entry = get_entry(name_or_id)

    if not entry:
        console.print(f"[red]Entry not found: {name_or_id}[/red]")
        return

    # Get password
    password = get_password()

    # Decrypt
    try:
        content = get_entry_content(entry, password)
    except Exception as e:
        console.print(f"[red]Decryption failed. 解密失败[/red]")
        console.print(f"[red]Error: {e}[/red]")
        return

    if stdout:
        console.print(content)
    elif output:
        output.write_text(content)
        console.print(f"[green]Saved to {output}[/green]")
    else:
        console.print(Panel(content, title=f"{entry['name']}"))


@app.command("scan")
def scan_cmd(
    directory: Optional[Path] = typer.Argument(None, help="Directory to scan / 要扫描的目录"),
):
    """
    Scan for .env files / 扫描.env文件.
    """
    if directory is None:
        directory = Path.cwd()

    results = scan_directory(directory)

    if not results:
        console.print("[yellow]No .env files found. 没有找到.env文件[/yellow]")
        return

    table = Table(title=".env Files Found", show_header=True)
    table.add_column("File 文件", style="cyan")
    table.add_column("Vars 变量数", style="green")
    table.add_column("Risks 风险", style="red")
    table.add_column(".gitignore", style="yellow")

    for info in results:
        risks = ",".join(info.get("high_risk", [])) or "None"
        gitignore_status = "✓" if info.get("in_gitignore") else "⚠️"

        table.add_row(
            info["name"],
            str(info["variables"]),
            risks,
            gitignore_status,
        )

    console.print(table)

    # Warn about files not in gitignore
    unsafe = [r for r in results if not r.get("in_gitignore")]
    if unsafe:
        console.print(f"\n[red]⚠️  {len(unsafe)} files not in .gitignore![/red]")


@app.command("share")
def share_cmd(
    name_or_id: str = typer.Argument(..., help="Entry to share / 要分享的条目"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file / 输出文件"),
):
    """
    Create shareable encrypted package / 创建可分享的加密包.
    """
    entry = get_entry(name_or_id)

    if not entry:
        console.print(f"[red]Entry not found: {name_or_id}[/red]")
        return

    # Get master password to decrypt
    master_password = get_password("Master password 主密码")

    # Decrypt original
    try:
        content = get_entry_content(entry, master_password)
    except Exception:
        console.print("[red]Invalid master password. 主密码错误[/red]")
        return

    # Generate share password
    share_password = generate_share_password()

    # Re-encrypt with share password
    encrypted = encrypt(content, share_password)

    # Save
    if output:
        output.write_text(encrypted)
    else:
        share_path = Path.home() / ".envguard" / "shares" / f"{entry['id']}_share.enc"
        share_path.parent.mkdir(parents=True, exist_ok=True)
        share_path.write_text(encrypted)
        output = share_path

    console.print(f"[green]Share package created: {output}[/green]")
    console.print(f"[yellow]Share password 分享密码: {share_password}[/yellow]")
    console.print("[red]⚠️  Share password is independent of master password![/red]")
    console.print("[red]   分享密码独立于主密码，请妥善保存[/red]")


@app.command("delete")
def delete_cmd(
    name_or_id: str = typer.Argument(..., help="Entry to delete / 要删除的条目"),
):
    """
    Delete entry from vault / 从保险库删除.
    """
    entry = get_entry(name_or_id)

    if not entry:
        console.print(f"[red]Entry not found: {name_or_id}[/red]")
        return

    # Confirm with password
    password = get_password("Confirm with password 密码确认")

    if not verify_master_password(password):
        console.print("[red]Invalid password. 密码错误[/red]")
        return

    # Delete
    success = delete_entry(name_or_id)

    if success:
        console.print(f"[red]Entry deleted: {name_or_id}[/red]")
    else:
        console.print("[red]Delete failed. 删除失败[/red]")


@app.command("sync")
def sync_cmd():
    """
    Sync vault to iCloud / 同步到iCloud.
    """
    success = sync_to_icloud()

    if success:
        console.print("[green]Synced to iCloud. 已同步[/green]")
    else:
        console.print("[red]Sync failed. 同步失败[/red]")


if __name__ == "__main__":
    app()