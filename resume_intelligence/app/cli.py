# Purpose:

# Manual testing
# Debugging
# Quick validation
import sys
from pathlib import Path

from resume_intelligence.core.parser import parse_document
from resume_intelligence.core.normalizer import normalize_document
from resume_intelligence.core.document import Document
from resume_intelligence.core.exception import (
    DocumentParseError,
    UnsupportedFileTypeError,
)
from resume_intelligence.core.semantics.extractor import extract_concepts
from resume_intelligence.core.semantics.consolidator import consolidate_concepts


def print_usage() -> None:
    print("\nUsage:")
    print("  python app/cli.py <path_to_resume_or_jd>\n")
    print("Example:")
    print("  python app/cli.py data/samples/resume.pdf\n")


def main() -> None:
    # ---- Argument validation
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"\nError: File not found → {file_path}\n")
        sys.exit(1)

    try:
        # ---- Phase 1: Parsing
        raw_text = parse_document(str(file_path))
        doc = Document(raw_text, metadata={"source": str(file_path)})

        # ---- Phase 1: Normalization
        doc = normalize_document(doc)

        # Explicit state assertion (important for typing & correctness)
        assert doc.clean_text is not None

        # ---- Diagnostics
        print("\nDocument loaded successfully\n")
        print(f"File: {file_path.name}")
        print(f"Raw text length   : {len(doc.raw_text)} characters")
        print(f"Clean text length : {len(doc.clean_text)} characters")
        print(f"Sentence count    : {len(doc.sentences)}\n")

        print("Sample sentences:")
        for sentence in doc.sentences[:5]:
            print(f"- {sentence}")

        # ---- Phase 2: Concept Extraction
        raw_concepts = extract_concepts(doc, source="resume")
        concepts = consolidate_concepts(raw_concepts)

        print("\nExtracted Concepts:")
        if not concepts:
            print("⚠️  No concepts extracted.")
        else:
            for concept in sorted(
                concepts, key=lambda c: c.confidence, reverse=True
            ):
                print(
                    f"- {concept.text:<30} "
                    f"| confidence={concept.confidence} "
                    f"| sentences={len(concept.sentences)}"
                )

    except UnsupportedFileTypeError as e:
        print(f"\nUnsupported file type:\n{e}\n")
        sys.exit(2)

    except DocumentParseError as e:
        print(f"\nFailed to process document:\n{e}\n")
        sys.exit(3)

    except AssertionError:
        print("\nInternal error: document normalization state invalid.\n")
        sys.exit(4)

    except Exception as e:
        print("\nUnexpected error occurred.\n")
        print(str(e))
        sys.exit(99)


if __name__ == "__main__":
    main()
