"""Load and assemble skill prompts from SKILL.md and references."""

from pathlib import Path

import yaml


def _find_skills_dir() -> Path:
    """Walk up from this file to find skillshelf-skills/skills/."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "skills"
        if candidate.is_dir() and (candidate / "brand-voice-extractor").is_dir():
            return candidate
        candidate = current / "skillshelf-skills" / "skills"
        if candidate.is_dir():
            return candidate
        current = current.parent
    raise FileNotFoundError("Cannot find skillshelf-skills/skills/ directory")


SKILLS_DIR = _find_skills_dir()


def list_skills() -> list[dict]:
    """Return metadata for all skills that have a SKILL.md."""
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        refs_dir = skill_dir / "references"
        skills.append({
            "slug": skill_dir.name,
            "name": meta.get("name", skill_dir.name),
            "description": meta.get("description", ""),
            "has_references": refs_dir.is_dir() and any(refs_dir.iterdir()),
        })
    return skills


def load_skill_prompt(slug: str) -> dict:
    """Assemble the full system prompt for a skill.

    Returns dict with keys: slug, name, description, system_prompt, reference_count.
    """
    skill_dir = SKILLS_DIR / slug
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"No SKILL.md found for skill: {slug}")

    raw = skill_md.read_text(encoding="utf-8")
    meta = _parse_frontmatter(raw)
    body = _extract_body(raw)

    parts = [body]
    ref_count = 0

    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.iterdir()):
            if ref_file.is_file() and ref_file.suffix in (".md", ".txt", ".yaml", ".json", ".csv"):
                ref_content = ref_file.read_text(encoding="utf-8")
                parts.append(f"\n\n---\n\n## Reference: {ref_file.name}\n\n{ref_content}")
                ref_count += 1

    return {
        "slug": slug,
        "name": meta.get("name", slug),
        "description": meta.get("description", ""),
        "system_prompt": "".join(parts),
        "reference_count": ref_count,
    }


def _parse_frontmatter(raw: str) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    if not raw.startswith("---"):
        return {}
    end = raw.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(raw[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _extract_body(raw: str) -> str:
    """Extract the markdown body after frontmatter."""
    if not raw.startswith("---"):
        return raw
    end = raw.find("---", 3)
    if end == -1:
        return raw
    return raw[end + 3:].lstrip("\n")
