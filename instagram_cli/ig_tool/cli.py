"""click entry point: search, profile, export."""
from __future__ import annotations

import csv
import dataclasses
import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .cache import Cache
from .client import IGClient, IGClientError, RequestCapReached
from .config import Settings, load_settings
from .models import Profile, UserSummary
from .search import SearchService

console = Console()


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True, show_path=False)
        ],
    )


def _build_service(settings: Settings) -> SearchService:
    cache = Cache(settings.db_path, settings.cache_ttl_seconds)
    client = IGClient(settings)
    client.login()
    return SearchService(client, cache)


@click.group()
@click.option("--request-cap", type=int, default=None, help="Override the per-session request cap.")
@click.option("--log-level", default=None, help="DEBUG, INFO, WARNING, ERROR.")
@click.pass_context
def cli(ctx: click.Context, request_cap: int | None, log_level: str | None) -> None:
    """Instagram public-data CLI. See README for ToS warnings."""
    settings = load_settings()
    if request_cap is not None:
        settings = dataclasses.replace(settings, request_cap_per_session=request_cap)
    _setup_logging(log_level or settings.log_level)
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings


@cli.command()
@click.argument("keyword")
@click.option("--limit", type=int, default=20, help="Max users to return.")
@click.option("--force-refresh", is_flag=True, help="Bypass the cache.")
@click.pass_context
def search(ctx: click.Context, keyword: str, limit: int, force_refresh: bool) -> None:
    """Search Instagram for users by keyword."""
    settings: Settings = ctx.obj["settings"]
    try:
        service = _build_service(settings)
        users = service.search(keyword, limit=limit, force_refresh=force_refresh)
    except RequestCapReached as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        sys.exit(2)
    except IGClientError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    _render_users(users, keyword)


@cli.command()
@click.argument("username")
@click.option("--force-refresh", is_flag=True, help="Bypass the cache.")
@click.pass_context
def profile(ctx: click.Context, username: str, force_refresh: bool) -> None:
    """Fetch full public profile for a single user."""
    settings: Settings = ctx.obj["settings"]
    try:
        service = _build_service(settings)
        prof = service.profile(username, force_refresh=force_refresh)
    except RequestCapReached as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        sys.exit(2)
    except IGClientError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    _render_profile(prof)


@cli.command()
@click.argument("keyword")
@click.option("--limit", type=int, default=20)
@click.option(
    "--format", "fmt",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Output format.",
)
@click.option(
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output file path (default: stdout).",
)
@click.option("--force-refresh", is_flag=True, help="Bypass the cache.")
@click.pass_context
def export(
    ctx: click.Context,
    keyword: str,
    limit: int,
    fmt: str,
    out: Path | None,
    force_refresh: bool,
) -> None:
    """Export search results to CSV or JSON."""
    settings: Settings = ctx.obj["settings"]
    try:
        service = _build_service(settings)
        users = service.search(keyword, limit=limit, force_refresh=force_refresh)
    except RequestCapReached as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        sys.exit(2)
    except IGClientError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    if fmt == "json":
        _write_json(users, out)
    else:
        _write_csv(users, out)


def _write_json(users: list[UserSummary], out: Path | None) -> None:
    payload = json.dumps([u.to_dict() for u in users], indent=2)
    if out is None:
        click.echo(payload)
        return
    out.write_text(payload, encoding="utf-8")
    console.print(f"[green]Wrote {len(users)} users to {out}[/green]")


def _write_csv(users: list[UserSummary], out: Path | None) -> None:
    fields = ["pk", "username", "full_name", "is_private", "is_verified", "profile_pic_url"]
    if out is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        for u in users:
            writer.writerow(u.to_dict())
        return
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for u in users:
            writer.writerow(u.to_dict())
    console.print(f"[green]Wrote {len(users)} users to {out}[/green]")


def _render_users(users: list[UserSummary], keyword: str) -> None:
    if not users:
        console.print(f"[yellow]No results for {keyword!r}.[/yellow]")
        return
    table = Table(title=f"Instagram search: {keyword!r}  ({len(users)} results)")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Username", style="cyan")
    table.add_column("Full name")
    table.add_column("Verified", justify="center", width=8)
    table.add_column("Private", justify="center", width=8)
    for i, u in enumerate(users, 1):
        table.add_row(
            str(i),
            u.username,
            u.full_name,
            "yes" if u.is_verified else "",
            "yes" if u.is_private else "",
        )
    console.print(table)


def _render_profile(p: Profile) -> None:
    table = Table(title=f"@{p.username}", show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    table.add_row("Full name", p.full_name)
    table.add_row("Bio", p.biography)
    table.add_row("Followers", f"{p.follower_count:,}")
    table.add_row("Following", f"{p.following_count:,}")
    table.add_row("Posts", f"{p.media_count:,}")
    table.add_row("Verified", "yes" if p.is_verified else "no")
    table.add_row("Private", "yes" if p.is_private else "no")
    table.add_row("Business", "yes" if p.is_business else "no")
    if p.category:
        table.add_row("Category", p.category)
    if p.external_url:
        table.add_row("URL", p.external_url)
    table.add_row("Fetched", p.fetched_at.isoformat(timespec="seconds"))
    console.print(table)


if __name__ == "__main__":
    cli()
