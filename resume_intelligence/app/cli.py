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


def print_usage() -> None:
    print("Usage:")
    print("  python app/cli.py <path_to_resume_or_jd>")
    print("")
    print("Example:")
    print("  python app/cli.py data/samples/resume.pdf")


def main() -> None:
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found → {file_path}")
        sys.exit(1)

    try:
        # Step 1: Parse document
        raw_text = parse_document(str(file_path))
        doc = Document(raw_text, metadata={"source": str(file_path)})

        # Step 2: Normalize document
        doc = normalize_document(doc)

        assert doc.clean_text is not None

        # Output diagnostics
        print("\nDocument loaded successfully\n")
        print(f"File: {file_path.name}")
        print(f"Raw text length: {len(doc.raw_text)} characters")
        print(f"Clean text length: {len(doc.clean_text)} characters")
        print(f"Sentence count: {len(doc.sentences)}\n")

        print("Sample sentences:")
        for sentence in doc.sentences[:5]:
            print(f"- {sentence}")

    except UnsupportedFileTypeError as e:
        print(f"Unsupported file type: {e}")
        sys.exit(2)

    except DocumentParseError as e:
        print(f"Failed to process document: {e}")
        sys.exit(3)

    except Exception as e:
        print("Unexpected error occurred.")
        print(str(e))
        sys.exit(99)


if __name__ == "__main__":
    main()
