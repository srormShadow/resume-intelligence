import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

from resume_intelligence.core.document import Document
from resume_intelligence.core.normalizer import normalize_document
from resume_intelligence.core.parser import parse_document
from resume_intelligence.core.semantics.extractor import extract_concepts
from resume_intelligence.core.semantics.consolidator import consolidate_concepts
from resume_intelligence.core.semantics.concept import ConceptSource
from resume_intelligence.core.matching.matcher import ConceptMatcher
from resume_intelligence.core.matching.ats_score import compute_ats_score
from resume_intelligence.core.exception import DocumentParseError


app = typer.Typer(help="ATS-grade Resume ↔ Job Description Matcher")
console = Console()


@app.command()
def match(
    resume: Path = typer.Argument(..., help="Path to resume file (PDF/TXT)"),
    jd: Path = typer.Argument(..., help="Path to job description file (TXT)"),
):
    """
    Compare a resume against a job description and compute ATS match score.
    """

    console.rule("[bold blue]ATS Resume Matcher[/bold blue]")

    try:
        # -------------------------
        # Parse & normalize resume
        # -------------------------
        console.print("📄 Parsing resume...")
        resume_text = parse_document(str(resume))
        resume_doc = Document(raw_text=resume_text)
        normalize_document(resume_doc)

        # -------------------------
        # Parse & normalize JD
        # -------------------------
        console.print("📄 Parsing job description...")
        jd_text = parse_document(str(jd))
        jd_doc = Document(raw_text=jd_text)
        normalize_document(jd_doc)

        # -------------------------
        # Extract & consolidate concepts
        # -------------------------
        console.print("🧠 Extracting resume concepts...")
        resume_concepts = consolidate_concepts(
            extract_concepts(resume_doc, ConceptSource.RESUME)
        )

        console.print("🧠 Extracting JD concepts...")
        jd_concepts = consolidate_concepts(
            extract_concepts(jd_doc, ConceptSource.JD)
        )

        if not jd_concepts:
            raise ValueError("No valid concepts found in job description.")

        # -------------------------
        # Semantic matching
        # -------------------------
        console.print("🔍 Performing semantic matching...")
        matcher = ConceptMatcher()
        match_results = matcher.match(jd_concepts, resume_concepts)

        # -------------------------
        # ATS score
        # -------------------------
        ats_score = compute_ats_score(jd_concepts, match_results)

    except FileNotFoundError as e:
        console.print(f"[bold red]File not found:[/bold red] {e}")
        raise typer.Exit(code=1)

    except DocumentParseError as e:
        console.print(f"[bold red]Document error:[/bold red] {e}")
        raise typer.Exit(code=1)

    except ValueError as e:
        console.print(f"[bold red]Invalid input:[/bold red] {e}")
        raise typer.Exit(code=1)

    # ❌ DO NOT catch bare Exception — let real bugs crash
    # except Exception as e:
    #     console.print(f"[bold red]Unexpected error:[/bold red] {e}")
    #     raise typer.Exit(code=1)

    # -------------------------
    # Display results
    # -------------------------
    console.rule("[bold green]ATS Match Result[/bold green]")
    console.print(f"🎯 [bold]ATS Match Score:[/bold] [green]{ats_score}%[/green]\n")

    def render_table(title, rows, color):
        table = Table(title=title, title_style=color)
        table.add_column("JD Concept", style="bold")
        table.add_column("Type")
        table.add_column("Score")
        table.add_column("Matched Resume Concept")

        for r in rows:
            table.add_row(
                r["jd_concept"],
                r["jd_type"].value,
                str(r["score"]),
                r["matched_resume_concept"] or "-",
            )

        console.print(table)

    if match_results["matched"]:
        render_table("✅ Matched Concepts", match_results["matched"], "green")

    if match_results["partial"]:
        render_table("⚠️ Partially Matched Concepts", match_results["partial"], "yellow")

    if match_results["missing"]:
        render_table("❌ Missing Concepts", match_results["missing"], "red")

    console.rule("[bold blue]Done[/bold blue]")


if __name__ == "__main__":
    app()
