"""Output formatting for diff results."""
from typing import List
from envdiff.comparator import DiffResult

TRY_RICH = True
try:
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    TRY_RICH = False


def report_plain(result: DiffResult) -> str:
    """Return a plain-text report string."""
    return result.summary()


def report_rich(result: DiffResult) -> None:
    """Print a rich-formatted table to stdout. Falls back to plain if rich unavailable."""
    if not TRY_RICH:
        print(report_plain(result))
        return

    console = Console()
    console.print(f"[bold]envdiff:[/bold] [cyan]{result.base_file}[/cyan] vs [cyan]{result.compare_file}[/cyan]")

    if not result.has_differences:
        console.print("[green]✓ No differences found.[/green]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key")
    table.add_column("Status")
    table.add_column("Base Value")
    table.add_column("Compare Value")

    for key in sorted(result.missing_in_compare):
        table.add_row(key, "[red]missing in compare[/red]", "", "")
    for key in sorted(result.missing_in_base):
        table.add_row(key, "[yellow]missing in base[/yellow]", "", "")
    for key in sorted(result.mismatched):
        base_val, cmp_val = result.mismatched[key]
        table.add_row(key, "[blue]mismatch[/blue]", str(base_val), str(cmp_val))

    console.print(table)


def report(result: DiffResult, fmt: str = "plain") -> None:
    """Dispatch to the appropriate reporter."""
    if fmt == "rich":
        report_rich(result)
    else:
        print(report_plain(result))
