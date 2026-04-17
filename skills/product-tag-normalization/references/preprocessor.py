import re
from typing import List, Dict, Any

STRICT_MODE = True
DEBUG_MODE = False


def normalize_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    title = title.strip()
    title = re.sub(r"[-_]+", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.title()


def normalize_tag(tag: str) -> str:
    if not isinstance(tag, str):
        return ""

    tag = tag.strip().lower()
    tag = re.sub(r"[-_]+", " ", tag)
    tag = re.sub(r"[^a-z0-9\s]", "", tag)
    tag = re.sub(r"\s+", " ", tag)
    return tag


def dedupe_preserve_order(tags: List[str]) -> List[str]:
    seen = set()
    result = []

    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)

    return result


def generate_handle(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text


def validate_output(title: str, tags: List[str]) -> None:
    errors = []

    if len(tags) != len(set(tags)):
        errors.append("Duplicate tags detected")

    for tag in tags:
        if tag != tag.lower():
            errors.append(f"Non-lowercase tag detected: {tag}")

    if "-" in title or "_" in title:
        errors.append("Title not normalized")

    if errors and STRICT_MODE:
        raise ValueError(f"Validation failed: {errors}")


def preprocess(input_data: Dict[str, Any]) -> Dict[str, Any]:
    if "title" not in input_data or "tags" not in input_data:
        raise ValueError("Input must contain title and tags")

    normalized_title = normalize_title(input_data["title"])

    raw_tags = input_data["tags"]
    if not isinstance(raw_tags, list):
        raise ValueError("Tags must be a list")

    normalized_tags = [normalize_tag(tag) for tag in raw_tags]
    normalized_tags = [t for t in normalized_tags if t]

    clean_tags = dedupe_preserve_order(normalized_tags)

    validate_output(normalized_title, clean_tags)

    handle = generate_handle(normalized_title)

    return {
        "handle": handle,
        "title_clean": normalized_title,
        "normalized_tags": clean_tags,
        "added_tags": [],   # LLM will populate
        "taxonomy": {},     # LLM will populate
        "vendor": "",
        "raw_locked": True
    }