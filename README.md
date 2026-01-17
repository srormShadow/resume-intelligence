# Resume Intelligence

A scalable, domain-agnostic resume intelligence engine that transforms unstructured resumes and job descriptions into structured, normalized representations for semantic matching and explainable ATS-style analysis.

---

## 🚀 Overview

**Resume Intelligence** is designed to be a robust foundation for building next-generation resume screening, ATS matching, and resume optimization systems.

Instead of relying on fragile keyword matching or resume formatting assumptions, this project focuses on **document understanding**, **text normalization**, and **semantic readiness** — enabling accurate, explainable, and extensible resume analysis.

This repository is intentionally built in **phases**, starting with a strong document processing foundation before introducing matching, scoring, and AI-driven insights.

---

## 🎯 Key Principles

- **Domain-agnostic** — works for any job role or industry
- **Format-independent** — resilient to resume layout and structure
- **Explainable** — every processing step is transparent
- **Extensible** — designed for gradual evolution into advanced AI systems
- **Production-oriented** — clean architecture and explicit error handling

---

## 🗂️ Project Structure

resume_intelligence/
│
├── app/
│ └── cli.py # CLI entry point for local testing
│
├── core/
│ ├── document.py # Canonical Document model
│ ├── parser.py # File parsing (PDF, DOCX, text)
│ ├── normalizer.py # Text normalization logic
│ ├── exception.py # Custom exception definitions
│ └── init.py
│
├── data/
│ └── samples/ # Local testing samples (ignored in git)
│
├── tests/
│ ├── test_document.py
│ ├── test_parser.py
│ └── test_normalizer.py
│
├── pyproject.toml
├── requirements.txt
└── README.md

yaml

---

PHRASE 1
This commit completes Phase 1 of the Resume Intelligence system by establishing
a reliable document ingestion and normalization foundation.

Key highlights:

- Implemented a unified Document model to represent raw and normalized content
  - Stores clean_text and sentence-level representations
  - Serves as the single source of truth for downstream semantic processing

- Added robust document parsing support
  - PDF parsing using pdfplumber
  - Plain text handling for job descriptions and test inputs
  - Clear error handling for unsupported or malformed files

- Introduced text normalization pipeline
  - Lowercasing and whitespace normalization
  - Sentence segmentation for fine-grained semantic analysis
  - Defensive validation to ensure documents are normalized before further processing

- Established clean project structure and core abstractions
  - Separated parsing, normalization, and domain models
  - Prepared the architecture for future semantic and matching layers

Outcome:
- Enables consistent, predictable input for semantic extraction
- Eliminates document-format variability as a source of error
- Provides a stable and extensible foundation for Phase 2 (semantic concept extraction)


PHRASE 2
This commit completes Phase 2 of the Resume Intelligence pipeline by introducing
robust, language-aware semantic concept extraction.

Key highlights:

- Implemented linguistic concept extraction using spaCy
  - Noun phrase extraction for skills, tools, and domains
  - Verb-based extraction for experience and practices

- Added multi-stage semantic normalization
  - Lemmatization and stopword cleanup
  - Verb canonicalization (e.g., "unit test" → "testing",
    "restful apis" → "api integration")

- Introduced concept validation and noise filtering
  - Removed pronouns, filler phrases, and role-only context
  - Enforced minimum semantic density for extracted concepts

- Implemented confidence scoring based on:
  - Frequency of occurrence
  - Action-based linguistic strength
  - Emphasis signals in sentences
  - Caps for overly generic concepts

- Added concept typing for downstream intelligence
  - skill, practice, tool, role_context
  - Automatically filtered role_context concepts

- Implemented concept consolidation layer
  - Collapsed duplicate and variant concepts into canonical forms
  - Preserved strongest confidence and merged evidence sentences
  - Maintained immutability of Concept objects

Outcome:
- Produces clean, canonical, ATS-grade semantic concepts
- Output is domain-agnostic, explainable, and ready for similarity matching
- Establishes a stable foundation for Phase 3 (semantic matching & gap analysis)
