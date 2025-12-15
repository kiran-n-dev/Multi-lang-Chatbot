from typing import List, Dict

def table_to_html(headers: List[str], rows: List[List[str]]) -> str:
    """Return a simple HTML table preserving column order & values."""
    def esc(s: str) -> str:
        return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = []
    for r in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in r)
        trs.append(f"<tr>{tds}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>"

def flatten_table_text(headers: List[str], rows: List[List[str]]) -> str:
    """Generate plain text string for embeddings without losing content."""
    parts = []
    parts.append(" | ".join(headers))
    for r in rows:
        parts.append(" | ".join(r))