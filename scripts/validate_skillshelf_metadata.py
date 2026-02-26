#!/usr/bin/env python3
"""Validate SkillShelf-specific metadata in skillshelf.yaml sidecar files.

This script checks that every skill in the SkillShelf library has a valid
skillshelf.yaml sidecar file alongside its SKILL.md, and that the SKILL.md
itself has a license field.

Usage:
    python validate_skillshelf_metadata.py skills/skill-one skills/skill-two ...

Exit codes:
    0 - All checks passed
    1 - One or more validation errors found
"""

import re
import sys
from pathlib import Path

import yaml

VALID_CATEGORIES = {
    "product-content",
    "catalog-operations",
    "product-discovery-and-recommendations",
    "customer-research-and-voice-of-customer",
    "merchandising-and-assortment",
    "conversion-and-page-optimization",
    "email-and-lifecycle",
    "reporting-and-analysis",
    "operations-and-process",
    "feed-and-channel-management",
}

VALID_LEVELS = {"beginner", "intermediate", "advanced"}

VALID_INTERACTION_PATTERNS = {"single-turn", "multi-turn"}

VALID_INSTALL_METHODS = {"copy", "directory"}

# Individual platform slug: lowercase alphanumeric and hyphens
PLATFORM_SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")

# ISO date format: YYYY-MM-DD
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_frontmatter(skill_md_path: Path) -> dict | None:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[3:end])


def validate_skill(skill_dir: Path) -> list[str]:
    """Validate SkillShelf metadata for a single skill directory.

    Returns a list of error messages. Empty list means all checks passed.
    """
    errors: list[str] = []
    skill_name = skill_dir.name

    # --- Check SKILL.md exists and has license ---
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_name}: SKILL.md not found in {skill_dir}")
        return errors

    frontmatter = parse_frontmatter(skill_md)
    if frontmatter is None:
        errors.append(f"{skill_name}: Could not parse YAML frontmatter")
        return errors

    if "license" not in frontmatter or not frontmatter["license"]:
        errors.append(
            f"{skill_name}: Missing 'license' field in SKILL.md. "
            "SkillShelf skills require a license (e.g., Apache-2.0)"
        )

    # --- Check skillshelf.yaml exists and is valid ---
    sidecar = skill_dir / "skillshelf.yaml"
    if not sidecar.exists():
        errors.append(f"{skill_name}: skillshelf.yaml not found")
        return errors

    data = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        errors.append(f"{skill_name}: skillshelf.yaml is not a valid YAML mapping")
        return errors

    # version (required string)
    version = data.get("version")
    if not version or not isinstance(version, str):
        errors.append(f"{skill_name}: Missing or invalid 'version' (must be a string)")

    # category (required, must be in valid set)
    category = data.get("category")
    if not category:
        errors.append(f"{skill_name}: Missing 'category'")
    elif category not in VALID_CATEGORIES:
        errors.append(
            f"{skill_name}: Invalid category '{category}'. "
            f"Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    # level (required, must be in valid set)
    level = data.get("level")
    if not level:
        errors.append(f"{skill_name}: Missing 'level'")
    elif level not in VALID_LEVELS:
        errors.append(
            f"{skill_name}: Invalid level '{level}'. "
            f"Must be one of: {', '.join(sorted(VALID_LEVELS))}"
        )

    # primitive (required boolean)
    primitive = data.get("primitive")
    if not isinstance(primitive, bool):
        errors.append(f"{skill_name}: 'primitive' must be a boolean (true/false)")

    # platforms (required list of slugs)
    platforms = data.get("platforms")
    if not isinstance(platforms, list) or not all(isinstance(p, str) for p in platforms):
        errors.append(f"{skill_name}: 'platforms' must be a list of strings")
    elif not platforms:
        errors.append(f"{skill_name}: 'platforms' must not be empty")
    else:
        for p in platforms:
            if not PLATFORM_SLUG_PATTERN.match(p):
                errors.append(f"{skill_name}: Invalid platform slug '{p}'")

    # tags (required list of strings)
    tags = data.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        errors.append(f"{skill_name}: 'tags' must be a list of strings")

    # interaction_pattern (optional, specific enum)
    ip = data.get("interaction_pattern")
    if ip is not None and ip not in VALID_INTERACTION_PATTERNS:
        errors.append(
            f"{skill_name}: Invalid interaction_pattern '{ip}'. "
            f"Must be one of: {', '.join(sorted(VALID_INTERACTION_PATTERNS))}"
        )

    # install_method (optional, specific enum, defaults to copy)
    im = data.get("install_method")
    if im is not None and im not in VALID_INSTALL_METHODS:
        errors.append(
            f"{skill_name}: Invalid install_method '{im}'. "
            f"Must be one of: {', '.join(sorted(VALID_INSTALL_METHODS))}"
        )

    # date fields (optional, must be YYYY-MM-DD if present)
    for date_field in ("date_certified", "date_added", "date_updated"):
        val = data.get(date_field)
        if val is not None and (not isinstance(val, str) or not DATE_PATTERN.match(val)):
            errors.append(
                f"{skill_name}: Invalid {date_field} '{val}'. Must be YYYY-MM-DD format"
            )

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_skillshelf_metadata.py <skill-dir> [<skill-dir> ...]", file=sys.stderr)
        return 1

    all_errors: list[str] = []

    for arg in sys.argv[1:]:
        skill_dir = Path(arg)
        if not skill_dir.is_dir():
            all_errors.append(f"{arg}: Not a directory")
            continue
        errors = validate_skill(skill_dir)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n{'='*60}", file=sys.stderr)
        print("SkillShelf metadata validation FAILED", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        for error in all_errors:
            print(f"  ERROR: {error}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) found.\n", file=sys.stderr)
        return 1

    skill_count = len(sys.argv) - 1
    print(f"SkillShelf metadata validation passed ({skill_count} skill(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
