"""
cli.py
------
ResumeIQ command-line interface.

Usage:
    python cli.py resume.pdf
    python cli.py resume.txt
    python cli.py resume.pdf --output report.json   # also save raw JSON

The ANTHROPIC_API_KEY environment variable must be set.
Get a free key at: https://console.anthropic.com
"""

import argparse
import json
import sys

from rich.console import Console

from src.parser import parse_resume, ParseError
from src.analyzer import analyze_resume, AnalysisError
from src.scorer import interpret_section_scores
from src.reporter import print_full_report

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resumeiq",
        description="🎯 ResumeIQ — AI-Powered Resume Analyzer (Claude AI)",
        epilog="Requires ANTHROPIC_API_KEY environment variable.",
    )
    parser.add_argument(
        "resume_file",
        type=str,
        help="Path to your resume file (.pdf or .txt)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional: save the raw JSON analysis to a file",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Step 1: Parse the resume file into plain text
    console.print(f"\n[cyan]📄 Parsing resume:[/cyan] {args.resume_file}")
    try:
        resume_text = parse_resume(args.resume_file)
    except ParseError as exc:
        console.print(f"[red]❌ Parse error:[/red] {exc}")
        sys.exit(1)

    console.print(f"[dim]   Extracted {len(resume_text)} characters of text.[/dim]")

    # Step 2: Send to Claude AI for analysis
    console.print("[cyan]🤖 Sending to Claude AI for analysis…[/cyan] [dim](this takes ~15 seconds)[/dim]")
    try:
        analysis = analyze_resume(resume_text)
    except AnalysisError as exc:
        console.print(f"[red]❌ Analysis error:[/red] {exc}")
        sys.exit(1)

    # Step 3: Interpret scores into grade labels and colors
    section_results = interpret_section_scores(analysis)

    # Step 4: Print the full report to the terminal
    print_full_report(analysis, section_results)

    # Step 5 (optional): Save the raw JSON analysis to disk
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            console.print(f"[dim]💾 Raw JSON saved to: {args.output}[/dim]\n")
        except OSError as exc:
            console.print(f"[yellow]⚠️  Could not save JSON output:[/yellow] {exc}")


if __name__ == "__main__":
    main()