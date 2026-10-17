"""
Convierte DOCUMENTO_DE_SOPORTE_RETO5.md en DOCUMENTO_DE_SOPORTE_RETO5.html (con imágenes embebidas)
y genera DOCUMENTO_DE_SOPORTE_RETO5.pdf listo para entrega ejecutiva.
"""
from __future__ import annotations
import base64
import html
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "DOCUMENTO_DE_SOPORTE_RETO5.md"
HTML_PATH = ROOT / "DOCUMENTO_DE_SOPORTE_RETO5.html"
PDF_PATH = ROOT / "DOCUMENTO_DE_SOPORTE_RETO5.pdf"


def img_to_data_uri(rel_path: str) -> str:
    p = ROOT / rel_path
    if not p.exists():
        return rel_path
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def inline_format(text: str) -> str:
    # Replace images ![alt](src)
    def repl_img(m):
        alt = html.escape(m.group(1))
        src = m.group(2).strip()
        uri = img_to_data_uri(src)
        return f'<div class="img-wrap"><img src="{uri}" alt="{alt}" /><div class="caption">{alt}</div></div>'

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl_img, text)
    # Inline code
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Math symbols cleanup for clean HTML/PDF
    text = text.replace(r"\ge", "≥").replace(r"\rightarrow", "→").replace(r"\approx", "≈")
    text = re.sub(r"\$([^$]+)\$", r"\1", text)
    return text


def md_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out = []
    in_code = False
    code_lang = ""
    code_buf = []
    in_table = False
    table_rows = []
    in_ul = False
    in_ol = False

    def flush_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table:
            return
        out.append("<table>")
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if idx == 0:
                out.append("<thead><tr>" + "".join(f"<th>{inline_format(c)}</th>" for c in cells) + "</tr></thead><tbody>")
            elif idx == 1 and all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                continue
            else:
                out.append("<tr>" + "".join(f"<td>{inline_format(c)}</td>" for c in cells) + "</tr>")
        out.append("</tbody></table>")
        in_table = False
        table_rows = []

    for line in lines:
        if line.startswith("```"):
            flush_lists()
            flush_table()
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            else:
                in_code = False
                out.append(f'<pre class="code-block"><code class="lang-{code_lang}">{html.escape(chr(10).join(code_buf))}</code></pre>')
            continue

        if in_code:
            code_buf.append(line)
            continue

        if line.strip().startswith("|") and line.strip().endswith("|"):
            flush_lists()
            in_table = True
            table_rows.append(line.strip())
            continue
        else:
            flush_table()

        s = line.strip()
        if not s:
            flush_lists()
            continue

        if s == "---":
            flush_lists()
            out.append("<hr/>")
            continue

        if s.startswith("# "):
            flush_lists()
            out.append(f"<h1>{inline_format(s[2:])}</h1>")
        elif s.startswith("## "):
            flush_lists()
            out.append(f"<h2>{inline_format(s[3:])}</h2>")
        elif s.startswith("### "):
            flush_lists()
            out.append(f"<h3>{inline_format(s[4:])}</h3>")
        elif re.match(r"^-\s+", s):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_format(re.sub(r'^-\s+', '', s))}</li>")
        elif re.match(r"^\d+\.\s+", s):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_format(re.sub(r'^\d+\.\s+', '', s))}</li>")
        else:
            flush_lists()
            out.append(f"<p>{inline_format(s)}</p>")

    flush_lists()
    flush_table()

    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Documento de Soporte — Reto 5 QA Cloud-Native</title>
<style>
  @page {{ size: A4; margin: 16mm 14mm; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 13px;
    max-width: 980px;
    margin: 0 auto;
    padding: 20px;
  }}
  h1 {{ font-size: 22px; color: #0f172a; border-bottom: 3px solid #2563eb; padding-bottom: 8px; margin-top: 8px; }}
  h2 {{ font-size: 17px; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-top: 24px; page-break-after: avoid; }}
  h3 {{ font-size: 14px; color: #0f172a; margin-top: 16px; page-break-after: avoid; }}
  p, li {{ margin-bottom: 6px; }}
  ul, ol {{ margin: 6px 0 12px 22px; }}
  code {{
    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
    background: #f1f5f9;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 11.5px;
    color: #0f172a;
  }}
  pre.code-block {{
    background: #0f172a;
    color: #f8fafc;
    padding: 12px 14px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 10px 0;
    page-break-inside: avoid;
  }}
  pre.code-block code {{
    background: transparent;
    color: #e2e8f0;
    padding: 0;
    font-size: 11px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 12px;
    page-break-inside: avoid;
  }}
  th, td {{
    border: 1px solid #cbd5e1;
    padding: 7px 9px;
    text-align: left;
    vertical-align: top;
  }}
  th {{ background: #eff6ff; color: #1e3a8a; font-weight: 700; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  .img-wrap {{
    margin: 12px 0;
    text-align: center;
    page-break-inside: avoid;
  }}
  .img-wrap img {{
    max-width: 100%;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }}
  .caption {{
    font-size: 11px;
    color: #475569;
    margin-top: 4px;
    font-style: italic;
  }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    md_text = MD_PATH.read_text(encoding="utf-8")
    html_str = md_to_html(md_text)
    HTML_PATH.write_text(html_str, encoding="utf-8")
    print(f"HTML generado en: {HTML_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file://{HTML_PATH}", wait_until="networkidle")
        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()
    print(f"PDF generado en: {PDF_PATH}")


if __name__ == "__main__":
    main()
