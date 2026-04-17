from typing import Dict, Any


def get_all_tags(data):
    return data.get("normalized_tags", []) + data.get("added_tags", [])


def export_csv(data: Dict[str, Any]) -> str:
    headers = ["Handle", "Title", "Tags", "Vendor"]

    all_tags = get_all_tags(data)

    row = [
        data.get("handle", ""),
        data.get("title_clean", ""),
        ", ".join(all_tags),
        data.get("vendor", "")
    ]

    return ",".join(headers) + "\n" + ",".join(row)


def export_table(data: Dict[str, Any]) -> str:
    all_tags = get_all_tags(data)

    return "\n".join([
        "| Field  | Value |",
        "|--------|-------|",
        f"| Handle | {data.get('handle','')} |",
        f"| Title  | {data.get('title_clean','')} |",
        f"| Tags   | {', '.join(all_tags)} |",
        f"| Vendor | {data.get('vendor','')} |"
    ])


def export_output(data: Dict[str, Any], format_type="csv") -> str:
    if format_type == "csv":
        return export_csv(data)
    elif format_type == "table":
        return export_table(data)
    else:
        raise ValueError("Unsupported format")