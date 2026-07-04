"""
reporter.py
------------
Builds and prints the final ResumeIQ analysis report to the terminal
using the Rich library for beautiful, color-coded output.

This is the only module that produces terminal output. Every other
module (parser, analyzer, scorer) works purely with data — no printing.

REPORT STRUCTURE (in order):
  1. Header banner with overall score and ATS score
  2. One-line verdict from the AI
  3. Section scores table (sorted worst-first)
  4. Strengths (what's already good)
  5. Critical issues (what must be fixed)
  6. ATS keyword analysis (found vs missing)
  7. Improved bullet points (before/after rewrites)
  8. Next steps (generated from the worst sections)
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box

from .scorer import SectionResult, get_overall_verdict

console = Console()


def _score_bar(score: int, color: str, width: int = 20) -> str:
    """
    Build a compact ASCII progress bar for a score (0–100).
    Used inside the section scores table.

    e.g. score=75 -> [███████████████░░░░░] 75
    """
    filled = int(round((score / 100) * width))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{color}][{bar}] {score:>3}[/{color}]"


def print_header(overall_score: int, ats_score: int, one_line_verdict: str) -> None:
    """Print the top banner with both key scores and the AI's one-line verdict."""
    _, overall_color, overall_emoji = _grade_from_score(overall_score)
    _, ats_color, _ = _grade_from_score(ats_score)

    # Build two side-by-side "score cards" using Rich Columns
    overall_card = Panel(
        f"[bold {overall_color}]{overall_score}/100[/bold {overall_color}]\n"
        f"[dim]Overall Score[/dim]",
        title=f"{overall_emoji} Resume Score",
        border_style=overall_color,
        width=28,
    )
    ats_card = Panel(
        f"[bold {ats_color}]{ats_score}/100[/bold {ats_color}]\n"
        f"[dim]ATS Compatibility[/dim]",
        title="🤖 ATS Score",
        border_style=ats_color,
        width=28,
    )

    console.print()
    console.print(Columns([overall_card, ats_card]))
    console.print(
        Panel(
            f"[italic]{one_line_verdict}[/italic]",
            title="[bold cyan]AI Verdict[/bold cyan]",
            border_style="cyan",
        )
    )


def _grade_from_score(score: int):
    """
    Thin wrapper that re-derives grade/color/emoji from scorer's thresholds
    without importing the scorer's private structure.
    """
    from .scorer import grade_score
    return grade_score(score)


def print_section_scores(section_results: list) -> None:
    """
    Print a table of all section scores, sorted worst-first.
    Each row shows: emoji, section name, score bar, grade, and a brief feedback snippet.
    """
    table = Table(
        title="📋 Section Scores (lowest first — fix these first!)",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold cyan",
    )
    table.add_column("", width=3)                        # emoji
    table.add_column("Section", style="bold", width=22)
    table.add_column("Score", width=28)
    table.add_column("Grade", justify="center", width=6)
    table.add_column("Quick Feedback", width=40)

    for result in section_results:
        # Truncate long feedback to fit in the table — full feedback is in its own panel
        short_feedback = (
            result.feedback[:75] + "…"
            if len(result.feedback) > 75
            else result.feedback
        )
        table.add_row(
            result.emoji,
            result.name,
            _score_bar(result.score, result.color),
            f"[{result.color}]{result.grade}[/{result.color}]",
            f"[dim]{short_feedback}[/dim]",
        )

    console.print(table)


def print_strengths_and_issues(strengths: list, critical_issues: list) -> None:
    """Print the strengths (green panel) and critical issues (red panel) side by side."""
    strengths_text = "\n".join(f"  ✅ {s}" for s in strengths)
    issues_text = "\n".join(f"  ❌ {i}" for i in critical_issues)

    strengths_panel = Panel(
        strengths_text or "  [dim]No specific strengths noted.[/dim]",
        title="[bold green]💪 Strengths[/bold green]",
        border_style="green",
    )
    issues_panel = Panel(
        issues_text or "  [dim]No critical issues found.[/dim]",
        title="[bold red]🚨 Critical Issues[/bold red]",
        border_style="red",
    )

    console.print(Columns([strengths_panel, issues_panel]))


def print_ats_keywords(found: list, missing: list) -> None:
    """Print the ATS keyword analysis — what's already there vs what's missing."""
    found_text = "  " + ",  ".join(f"[green]{k}[/green]" for k in found) if found else "  [dim]None detected[/dim]"
    missing_text = "  " + ",  ".join(f"[red]{k}[/red]" for k in missing) if missing else "  [dim]Great — nothing obvious missing[/dim]"

    console.print(Panel(
        f"[bold]Found ({len(found)}):[/bold]\n{found_text}\n\n"
        f"[bold]Missing — add these:[/bold]\n{missing_text}",
        title="[bold cyan]🔍 ATS Keyword Analysis[/bold cyan]",
        border_style="cyan",
    ))


def print_improved_bullets(improved_bullets: list) -> None:
    """
    Print before/after rewrites for the weakest bullet points.
    These are concrete, copy-paste-ready improvements for the candidate.
    """
    if not improved_bullets:
        return

    console.print(Panel(
        "[dim]Here are AI-rewritten versions of your weakest bullet points.[/dim]",
        title="[bold yellow]✍️  Improved Bullet Points[/bold yellow]",
        border_style="yellow",
    ))

    for i, bullet in enumerate(improved_bullets, 1):
        original = bullet.get("original", "")
        improved = bullet.get("improved", "")

        console.print(f"  [dim]Bullet {i}[/dim]")
        console.print(f"  [red]Before:[/red]  {original}")
        console.print(f"  [green]After: [/green]  {improved}")
        console.print()


def print_next_steps(section_results: list) -> None:
    """
    Generate and print actionable next steps based on the three lowest-scoring
    sections in the analysis.
    """
    # Take the 3 lowest-scoring sections
    worst_three = section_results[:3]

    steps = []
    for i, result in enumerate(worst_three, 1):
        steps.append(
            f"  [cyan]{i}.[/cyan] [bold]{result.name}[/bold] ({result.score}/100)\n"
            f"     {result.feedback}"
        )

    console.print(Panel(
        "\n\n".join(steps),
        title="[bold magenta]🎯 Your Top 3 Next Steps[/bold magenta]",
        border_style="magenta",
    ))


def print_full_report(analysis: dict, section_results: list) -> None:
    """
    Orchestrate the complete report: call every print function in order
    to produce the full ResumeIQ output.

    Args:
        analysis: the raw dict from analyzer.py
        section_results: the list of SectionResult from scorer.py
    """
    overall_score = analysis.get("overall_score", 0)
    ats_score = analysis.get("ats_score", 0)
    one_line_verdict = analysis.get("one_line_verdict", "Analysis complete.")
    headline, advice = get_overall_verdict(overall_score)

    console.rule("[bold cyan]ResumeIQ — AI-Powered Resume Analysis[/bold cyan]")

    print_header(overall_score, ats_score, one_line_verdict)

    console.print(f"\n[bold]{headline}[/bold] — {advice}\n")

    print_section_scores(section_results)
    console.print()

    print_strengths_and_issues(
        analysis.get("strengths", []),
        analysis.get("critical_issues", []),
    )
    console.print()

    print_ats_keywords(
        analysis.get("ats_keywords_found", []),
        analysis.get("ats_keywords_missing", []),
    )
    console.print()

    print_improved_bullets(analysis.get("improved_bullets", []))

    print_next_steps(section_results)

    console.rule("[dim]End of ResumeIQ Report[/dim]")
    console.print()