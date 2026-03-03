#!/usr/bin/env python3
"""
install_bootstrap.py

Reads settleup_bootstrap.py and writes each section to its corresponding
file path in the project. Run this from the project root.

Usage:
    python install_bootstrap.py [--bootstrap-file PATH] [--project-root PATH] [--dry-run]

Options:
    --bootstrap-file    Path to the bootstrap file (default: settleup_bootstrap.py)
    --project-root      Path to the project root (default: current directory)
    --dry-run           Print what would be written without writing any files
"""

import argparse
import os
import re
import sys


HEADER_PATTERN = re.compile(
    r"^#{1,}\s*={3,}\s*\n"          # opening === line
    r"#{1,}\s*(\./.+?)\s*\n"        # # ./path/to/file.py
    r"#{1,}\s*={3,}\s*\n",          # closing === line
    re.MULTILINE,
)

ENV_NOTE_PATTERN = re.compile(
    r"^#\s*NOTE:.*\n(#.*\n)*",
    re.MULTILINE,
)


def parse_sections(bootstrap_text: str) -> list[tuple[str, str]]:
    """
    Returns a list of (filepath, content) tuples parsed from the bootstrap file.
    Skips the .env section — it requires manual handling.
    """
    matches = list(HEADER_PATTERN.finditer(bootstrap_text))

    if not matches:
        print("ERROR: No file sections found. Is this the right bootstrap file?")
        sys.exit(1)

    sections = []
    for i, match in enumerate(matches):
        filepath = match.group(1).strip()

        # Content runs from end of this header to start of next header (or EOF)
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(bootstrap_text)
        content = bootstrap_text[content_start:content_end]

        # Strip leading/trailing blank lines
        content = content.strip("\n")

        # Skip .env — it's documented as a comment block, not real Python
        if filepath == "./.env":
            print(f"  SKIPPED  {filepath}  (edit manually — see comments in bootstrap file)")
            continue

        # Skip __init__.py marked as intentionally empty
        if "intentionally empty" in content:
            content = ""

        sections.append((filepath, content))

    return sections


def normalise_path(filepath: str, project_root: str) -> str:
    """Converts ./path/to/file.py to an absolute path under project_root."""
    relative = filepath.lstrip("./")
    return os.path.join(project_root, relative)


def write_section(filepath: str, content: str, project_root: str, dry_run: bool) -> None:
    abs_path = normalise_path(filepath, project_root)
    directory = os.path.dirname(abs_path)

    if dry_run:
        lines = len(content.splitlines())
        print(f"  DRY RUN  {filepath}  ({lines} lines)")
        return

    # Create intermediate directories if needed
    os.makedirs(directory, exist_ok=True)

    with open(abs_path, "w", encoding="utf-8") as f:
        if content:
            f.write(content + "\n")
        # Empty content writes an empty file (e.g. __init__.py)

    lines = len(content.splitlines())
    print(f"  WRITTEN  {filepath}  ({lines} lines)")


def confirm_overwrite(existing: list[str]) -> bool:
    print("\nThe following files already exist and will be overwritten:")
    for p in existing:
        print(f"    {p}")
    answer = input("\nContinue? [y/N] ").strip().lower()
    return answer == "y"


def main():
    parser = argparse.ArgumentParser(
        description="Install settleup bootstrap files into the project."
    )
    parser.add_argument(
        "--bootstrap-file",
        default="settleup_bootstrap.py",
        help="Path to the bootstrap file (default: settleup_bootstrap.py)",
    )
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="Project root directory (default: current working directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing any files",
    )
    args = parser.parse_args()

    bootstrap_path = os.path.abspath(args.bootstrap_file)
    project_root = os.path.abspath(args.project_root)

    # Validate bootstrap file exists
    if not os.path.isfile(bootstrap_path):
        print(f"ERROR: Bootstrap file not found: {bootstrap_path}")
        sys.exit(1)

    print(f"\nBootstrap file : {bootstrap_path}")
    print(f"Project root   : {project_root}")
    print(f"Mode           : {'DRY RUN' if args.dry_run else 'WRITE'}")
    print()

    with open(bootstrap_path, "r", encoding="utf-8") as f:
        bootstrap_text = f.read()

    sections = parse_sections(bootstrap_text)

    if not sections:
        print("No sections to write.")
        sys.exit(0)

    # Check for existing files before writing anything
    if not args.dry_run:
        existing = [
            fp for fp, _ in sections
            if os.path.isfile(normalise_path(fp, project_root))
        ]
        if existing:
            if not confirm_overwrite(existing):
                print("Aborted.")
                sys.exit(0)
        print()

    # Write all sections
    written = 0
    for filepath, content in sections:
        write_section(filepath, content, project_root, args.dry_run)
        written += 1

    print(f"\n{'Would write' if args.dry_run else 'Wrote'} {written} file(s).")

    if not args.dry_run:
        print("\nNext steps:")
        print("  1. Copy your .env values from the bootstrap file comments")
        print("  2. Update DATABASE_URL in .env with your PostgreSQL credentials")
        print("  3. Run: python manage.py check")
        print("  4. Run: python manage.py makemigrations users")
        print("  5. Run: python manage.py makemigrations groups expenses payments notifications alerts audit")
        print("  6. Run: python manage.py migrate")
        print("  7. Run: python manage.py createsuperuser")
        print("  8. Run: python manage.py runserver")


if __name__ == "__main__":
    main()
