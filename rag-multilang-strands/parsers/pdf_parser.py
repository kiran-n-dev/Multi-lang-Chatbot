
import io
from typing import List, Dict, Any
import pdfplumber
from parsers.common import table_to_html, flatten_table_text

def parse_pdf_bytes(pdf_bytes: bytes, fname: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for pi, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    out.append({"plain_text": text, "source": f"{fname}#p{pi}"})

                tables = page.extract_tables() or []
                for t in tables:
                    if not t or len(t) < 2:
                        continue
                    headers = [str(c or "").strip() for c in t[0]]
                    rows = [[str(c or "").strip() for c in row] for row in t[1:]]
                    html = table_to_html(headers, rows)
                    flat = flatten_table_text(headers, rows)
                    out.append({
                        "table_html": html,
                        "plain_text": flat,
                        "source": f"{fname}#p{pi}"
                    })
    except Exception as e:
        print(f"[parse_pdf_bytes] Error parsing PDF {fname}: {e}")
    return out
