#!/usr/bin/env python3
"""Build an evidence table mapping Shopify product fields to their presence in
the rendered storefront PDP.

Phase 1 deterministic processor for the map-pdp-structure skill. The output
is consumed by the LLM alongside the rendered page and metafield definitions
to classify visible PDP sections and map them to Shopify sources.

Usage:
    python3 references/build_evidence_table.py \\
        --product-data <product1.json>[,<product2.json>,...] \\
        --rendered-pages <page1.md>[,<page2.md>,...] \\
        --output evidence.json

The first product in --product-data is the primary reference; its fields
drive the evidence table. Additional products (up to 2 more) enable
static/dynamic detection by comparing metafield values across products.

Exit codes:
    0 - success
    1 - fatal error (file not found, parse failure)
"""

import argparse
import html
import html.parser
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "0.1.0"

BLOCK_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol",
              "div", "blockquote", "pre", "section", "article", "aside"}

REFERENCE_TYPE_SUFFIXES = ("_reference",)
REFERENCE_TYPE_NAMES = {"file_reference", "product_reference",
                        "metaobject_reference", "page_reference",
                        "collection_reference", "variant_reference"}

MIN_MATCH_LEN = 5  # strings shorter than this are too noisy to evidence-match


# ─── Text normalization ─────────────────────────────────────────────────────

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags, decode entities, return plain text."""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return text


def normalize(text: str) -> str:
    """Canonicalize for substring matching: decode entities, strip tags,
    lowercase, unicode-normalize, collapse whitespace."""
    if not text:
        return ""
    text = strip_html(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def strip_jina_header(page_text: str) -> str:
    """Jina Reader markdown starts with `Title:` / `URL Source:` / blank line /
    `Markdown Content:`. Strip everything up through that marker so the body
    is what we match against."""
    marker = "Markdown Content:"
    idx = page_text.find(marker)
    if idx == -1:
        return page_text
    return page_text[idx + len(marker):].lstrip()


# ─── body_html chunking ─────────────────────────────────────────────────────

class BodyHtmlChunker(html.parser.HTMLParser):
    """Split body_html into sequential chunks keyed on top-level block tags.

    Inline tags (em, strong, a, span, br) flatten into the enclosing block
    chunk's text. Bare text between block tags becomes a `text` chunk.
    Nested block tags are flattened into the outer chunk (Shopify body_html
    is typically shallow)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks: list[dict] = []
        self._open_block: dict | None = None
        self._top_text: list[str] = []

    def _new_id(self) -> str:
        return f"chunk_{len(self.chunks) + 1}"

    def _flush_top_text(self) -> None:
        text = "".join(self._top_text).strip()
        self._top_text = []
        if text:
            self.chunks.append({
                "id": self._new_id(),
                "tag": "text",
                "text": text,
                "html": text,
            })

    def _serialize_start(self, tag: str, attrs: list) -> str:
        pairs = []
        for key, value in attrs:
            if value is None:
                pairs.append(f" {key}")
            else:
                escaped = html.escape(value, quote=True)
                pairs.append(f' {key}="{escaped}"')
        return f"<{tag}{''.join(pairs)}>"

    def handle_starttag(self, tag, attrs):
        if self._open_block is None and tag in BLOCK_TAGS:
            self._flush_top_text()
            self._open_block = {
                "tag": tag,
                "text": [],
                "html": [self._serialize_start(tag, attrs)],
            }
        elif self._open_block is not None:
            self._open_block["html"].append(self._serialize_start(tag, attrs))
            self._open_block["text"].append(" ")

    def handle_startendtag(self, tag, attrs):
        if self._open_block is None:
            return
        pairs = []
        for key, value in attrs:
            if value is None:
                pairs.append(f" {key}")
            else:
                escaped = html.escape(value, quote=True)
                pairs.append(f' {key}="{escaped}"')
        self._open_block["html"].append(f"<{tag}{''.join(pairs)} />")
        self._open_block["text"].append(" ")

    def handle_endtag(self, tag):
        if self._open_block is None:
            return
        self._open_block["html"].append(f"</{tag}>")
        if tag == self._open_block["tag"]:
            block = self._open_block
            self._open_block = None
            text = _WHITESPACE_RE.sub(" ", "".join(block["text"])).strip()
            self.chunks.append({
                "id": self._new_id(),
                "tag": block["tag"],
                "text": text,
                "html": "".join(block["html"]),
            })

    def handle_data(self, data):
        if self._open_block is not None:
            self._open_block["text"].append(data)
            self._open_block["html"].append(data)
        else:
            self._top_text.append(data)

    def close(self):
        super().close()
        self._flush_top_text()
        if self._open_block is not None:
            # Unclosed block (malformed HTML): flush as-is
            block = self._open_block
            self._open_block = None
            text = _WHITESPACE_RE.sub(" ", "".join(block["text"])).strip()
            self.chunks.append({
                "id": self._new_id(),
                "tag": block["tag"],
                "text": text,
                "html": "".join(block["html"]),
            })


def chunk_body_html(body_html: str) -> list[dict]:
    parser = BodyHtmlChunker()
    parser.feed(body_html or "")
    parser.close()
    return parser.chunks


# ─── Metafield searchable-text extraction ──────────────────────────────────

def metafield_searchable_text(value: str, type_name: str) -> tuple[str | None, str]:
    """Return (searchable_text, value_type) for a metafield.
    searchable_text is None when the metafield is a reference type (content
    lives elsewhere). value_type is one of: string, json, list, rich_text,
    html, reference, empty."""
    if value is None or value == "":
        return None, "empty"

    if type_name in REFERENCE_TYPE_NAMES or any(type_name.endswith(s) for s in REFERENCE_TYPE_SUFFIXES):
        return None, "reference"

    if type_name == "json":
        try:
            obj = json.loads(value)
        except json.JSONDecodeError:
            return value, "string"
        return _json_leaves_as_text(obj), "json"

    if type_name.startswith("list."):
        try:
            items = json.loads(value) if value.lstrip().startswith("[") else [value]
        except json.JSONDecodeError:
            items = [value]
        return " ".join(str(i) for i in items), "list"

    if type_name == "rich_text_field":
        return strip_html(value), "rich_text"

    if type_name == "multi_line_text_field" and value.lstrip().startswith("<"):
        return strip_html(value), "html"

    return value, "string"


def _json_leaves_as_text(obj: Any) -> str:
    parts: list[str] = []
    if isinstance(obj, dict):
        for v in obj.values():
            parts.append(_json_leaves_as_text(v))
    elif isinstance(obj, list):
        for v in obj:
            parts.append(_json_leaves_as_text(v))
    elif isinstance(obj, str):
        parts.append(obj)
    elif obj is not None:
        parts.append(str(obj))
    return " ".join(p for p in parts if p)


# ─── Evidence matching ─────────────────────────────────────────────────────

def find_in_page(needle: str, haystack_norm: str) -> tuple[str, list[int]]:
    """Return (match_confidence, match_span). Confidence is exact | partial | none."""
    needle_norm = normalize(needle)
    if len(needle_norm) < MIN_MATCH_LEN:
        return "none", []

    idx = haystack_norm.find(needle_norm)
    if idx != -1:
        return "exact", [idx, idx + len(needle_norm)]

    # Partial: try shrinking the needle from the end down to 50% of its length
    min_len = max(MIN_MATCH_LEN, len(needle_norm) // 2)
    step = max(1, len(needle_norm) // 20)
    for length in range(len(needle_norm) - step, min_len - 1, -step):
        prefix = needle_norm[:length].rstrip()
        if len(prefix) < MIN_MATCH_LEN:
            break
        idx = haystack_norm.find(prefix)
        if idx != -1:
            return "partial", [idx, idx + len(prefix)]

    return "none", []


def preview(text: str, length: int = 60) -> str:
    text = " ".join(text.split())
    return text if len(text) <= length else text[:length] + "…"


# ─── Product loading ────────────────────────────────────────────────────────

def load_product(path: Path) -> dict:
    """Load a product JSON file. Supports both `{product: {...}}` (Shopify
    `.json` endpoint shape) and bare `{...}` (direct product object)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["product"] if "product" in data and isinstance(data["product"], dict) else data


def load_page(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    return strip_jina_header(raw)


# ─── Evidence table construction ────────────────────────────────────────────

def build_evidence_rows(product: dict, page_norm: str,
                        body_html_chunks: list[dict]) -> list[dict]:
    rows: list[dict] = []

    def add(field_source: str, value: str, value_type: str) -> None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return
        confidence, span = find_in_page(value, page_norm)
        rows.append({
            "field_source": field_source,
            "value_preview": preview(value),
            "value_type": value_type,
            "appears_on_page": confidence != "none",
            "match_confidence": confidence,
            "match_span": span,
        })

    add("title", product.get("title", ""), "string")
    add("vendor", product.get("vendor", ""), "string")
    add("product_type", product.get("product_type", ""), "string")

    seo = product.get("seo") or {}
    add("seo.title", seo.get("title", ""), "string")
    add("seo.description", seo.get("description", ""), "string")

    tags_raw = product.get("tags", "")
    if isinstance(tags_raw, list):
        tags_str = ", ".join(tags_raw)
    else:
        tags_str = tags_raw or ""
    add("tags", tags_str, "string")

    for mf in product.get("metafields", []) or []:
        source = f"metafield/{mf['namespace']}.{mf['key']}"
        searchable, vtype = metafield_searchable_text(mf.get("value", ""),
                                                      mf.get("type", ""))
        if searchable is None:
            rows.append({
                "field_source": source,
                "value_preview": f"[{vtype}]",
                "value_type": vtype,
                "appears_on_page": False,
                "match_confidence": "none",
                "match_span": [],
            })
        else:
            add(source, searchable, vtype)

    for chunk in body_html_chunks:
        source = f"body_html/{chunk['id']}"
        add(source, chunk["text"], f"body_html_{chunk['tag']}")

    return rows


# ─── Static/dynamic detection ──────────────────────────────────────────────

def detect_static_dynamic(primary: dict, others: list[dict]) -> tuple[list, list]:
    """Compare metafield values across products. A metafield with identical
    value in all products is a static candidate. Differing values make it a
    dynamic candidate. Metafields absent from other products are neither."""
    static_candidates: list[dict] = []
    dynamic_candidates: list[dict] = []

    if not others:
        return static_candidates, dynamic_candidates

    primary_mfs = {(m["namespace"], m["key"]): m for m in primary.get("metafields") or []}

    for (ns, key), mf in primary_mfs.items():
        value = mf.get("value")
        if value is None or value == "":
            continue
        other_values = []
        for o in others:
            for om in o.get("metafields") or []:
                if om.get("namespace") == ns and om.get("key") == key:
                    other_values.append(om.get("value", ""))
                    break
            else:
                other_values.append(None)  # absent
        if any(ov is None for ov in other_values):
            continue  # can't classify without coverage
        record = {
            "field_source": f"metafield/{ns}.{key}",
            "value_preview": preview(str(value)),
        }
        if all(ov == value for ov in other_values):
            static_candidates.append(record)
        else:
            dynamic_candidates.append(record)

    return static_candidates, dynamic_candidates


# ─── Orchestration ─────────────────────────────────────────────────────────

def build_output(product_paths: list[Path], page_paths: list[Path]) -> dict:
    if not product_paths:
        raise SystemExit("error: at least one product JSON is required")
    if not page_paths:
        raise SystemExit("error: at least one rendered page is required")

    products = [load_product(p) for p in product_paths]
    pages = [load_page(p) for p in page_paths]
    pages_norm = [normalize(p) for p in pages]

    primary = products[0]
    primary_page_norm = pages_norm[0]

    body_html = primary.get("body_html") or primary.get("descriptionHtml") or ""
    body_html_chunks = chunk_body_html(body_html)

    evidence_rows = build_evidence_rows(primary, primary_page_norm, body_html_chunks)

    static_candidates, dynamic_candidates = detect_static_dynamic(primary, products[1:])

    metafield_definitions = []
    for mf in primary.get("metafields") or []:
        defn = mf.get("definition") or {}
        type_obj = defn.get("type") or {}
        metafield_definitions.append({
            "namespace": mf.get("namespace"),
            "key": mf.get("key"),
            "type": mf.get("type") or type_obj.get("name"),
            "definition_name": defn.get("name"),
            "description": defn.get("description", ""),
        })

    return {
        "script_version": SCRIPT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product_handle": primary.get("handle"),
        "product_title": primary.get("title"),
        "reference_products": [p.get("handle") for p in products],
        "rendered_page_count": len(pages),
        "metafield_definitions": metafield_definitions,
        "body_html_chunks": body_html_chunks,
        "evidence_table": evidence_rows,
        "static_candidates": static_candidates,
        "dynamic_candidates": dynamic_candidates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--product-data", required=True,
                        help="Comma-separated paths to product JSON files "
                             "(first is primary reference).")
    parser.add_argument("--rendered-pages", required=True,
                        help="Comma-separated paths to rendered-page markdown files.")
    parser.add_argument("--output", required=True,
                        help="Path to write evidence JSON.")
    args = parser.parse_args(argv)

    product_paths = [Path(p.strip()) for p in args.product_data.split(",") if p.strip()]
    page_paths = [Path(p.strip()) for p in args.rendered_pages.split(",") if p.strip()]

    for p in product_paths + page_paths:
        if not p.is_file():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1

    try:
        result = build_output(product_paths, page_paths)
    except json.JSONDecodeError as exc:
        print(f"error: JSON parse failure: {exc}", file=sys.stderr)
        return 1
    except SystemExit:
        raise
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
