"""Simple DOCX to PDF converter using Chrome."""
import sys
import html
import base64
import mimetypes
import re
import subprocess
import tempfile
from pathlib import Path
import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

def convert(docx_path, pdf_path):
    doc = docx.Document(docx_path)

    html_parts = ['''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page { size: A4; margin: 2.2cm 2.0cm; }
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.45; margin: 0; padding: 0; }
h1 { font-size: 14pt; margin-top: 18pt; margin-bottom: 12pt; }
h2 { font-size: 13pt; margin-top: 14pt; margin-bottom: 10pt; }
p { margin: 6pt 0; text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 12pt 0; font-size: 10pt; }
th, td { border: 1px solid #000; padding: 5px 6px; overflow-wrap: break-word; }
th { background: #D9E2F3; font-weight: bold; }
.center { text-align: center; }
.code { font-family: 'Courier New', monospace; font-size: 8pt; background: #f5f5f5;
        padding: 8px; margin: 6pt 0; white-space: pre-wrap; border: 1px solid #ddd; }
.page-break { page-break-after: always; }
.pb { page-break-before: always; }
figure { margin: 10pt 0 12pt; text-align: center; page-break-inside: avoid; }
figcaption { font-style: italic; font-size: 9.5pt; margin-top: 4pt; text-align: center; }
figure img { max-width: 100%; height: auto; max-height: 11.5cm; }
img { max-width: 100%; height: auto; max-height: 11.5cm; }
ul, ol { margin: 6pt 0; padding-left: 20pt; }
li { margin: 3pt 0; }
</style></head><body>
''']

    def image_tag(run):
        """Return an <img> for a run that carries a drawing, else ''.

        python-docx has no public accessor for an inline image, so the
        relationship id is read from the run's XML and resolved against the
        document part. Without this the converter silently dropped every
        figure: the DOCX held 22 images and the PDF held none, leaving every
        caption printed under blank space.
        """
        xml = run._element.xml
        if 'graphic' not in xml:
            return ''
        # <wp:extent cx=".." cy=".."> carries the size Word would render, in EMU.
        style = ''
        m = re.search(r'<wp:extent[^>]*cx="(\d+)"[^>]*cy="(\d+)"', xml)
        if m:
            w_pt = int(m.group(1)) / 12700.0
            h_pt = int(m.group(2)) / 12700.0
            style = f' style="width:{w_pt:.1f}pt;max-height:{h_pt:.1f}pt"'
        out = []
        for attr in ('r:embed', 'r:link'):
            key = attr + '="'
            start = 0
            while True:
                i = xml.find(key, start)
                if i < 0:
                    break
                j = xml.index('"', i + len(key))
                rid = xml[i + len(key):j]
                start = j
                part = doc.part.related_parts.get(rid)
                if part is None:
                    continue
                blob = part.blob
                ctype = getattr(part, 'content_type', '') or \
                    mimetypes.guess_type(str(part.partname))[0] or 'image/png'
                b64 = base64.b64encode(blob).decode('ascii')
                out.append(f'<img{style} src="data:{ctype};base64,{b64}">')
        return ''.join(out)

    def get_text(para):
        text = ''
        for run in para.runs:
            img = image_tag(run)
            if img:
                text += img
                continue
            t = html.escape(run.text)
            if run.bold:
                t = f'<strong>{t}</strong>'
            if run.italic:
                t = f'<em>{t}</em>'
            text += t
        return text

    def is_code(para):
        for run in para.runs:
            if run.font.name and 'Courier' in run.font.name:
                return True
        return False

    in_code = False
    code_lines = []

    pending_break = False

    def emit(chunk):
        nonlocal pending_break
        if pending_break:
            chunk = f'<div class="pb">{chunk}</div>'
            pending_break = False
        html_parts.append(chunk)

    for element in doc.element.body:
        if element.tag.endswith('}p'):
            para = Paragraph(element, doc)
            text = get_text(para)

            for run in para.runs:
                if run._element.xml and 'w:br' in run._element.xml and 'page' in run._element.xml:
                    if in_code and code_lines:
                        html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')
                        code_lines = []
                        in_code = False
                    pending_break = True

            if not text.strip():
                continue
            if text.lstrip().startswith('<img'):
                emit(f'<p class="center">{text}</p>')
                continue

            if para.style and para.style.name.startswith('Heading'):
                if in_code and code_lines:
                    html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')
                    code_lines, in_code = [], False
                level = para.style.name[-1] if para.style.name[-1].isdigit() else '1'
                emit(f'<h{level}>{text}</h{level}>')
            elif is_code(para):
                if not in_code:
                    in_code = True
                code_lines.append(para.text)
            elif para.style and 'List' in para.style.name:
                if in_code and code_lines:
                    html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')
                    code_lines, in_code = [], False
                emit(f'<li>{text}</li>')
            else:
                if in_code and code_lines:
                    html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')
                    code_lines, in_code = [], False
                align = para.alignment
                cls = ' class="center"' if align and align.name == 'CENTER' else ''
                emit(f'<p{cls}>{text}</p>')

        elif element.tag.endswith('}tbl'):
            if in_code and code_lines:
                html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')
                code_lines, in_code = [], False
            table = Table(element, doc)
            rows_html = []
            for i, row in enumerate(table.rows):
                cells = []
                tag = 'th' if i == 0 else 'td'
                for cell in row.cells:
                    # cells may hold pictures (the SDG tiles on the title page),
                    # so build them the same way as body paragraphs
                    parts = []
                    for cp in cell.paragraphs:
                        for r in cp.runs:
                            img = image_tag(r)
                            if img:
                                parts.append(img)
                        if cp.text.strip():
                            parts.append(html.escape(cp.text))
                    cells.append(f'<{tag}>{" ".join(parts)}</{tag}>')
                rows_html.append('<tr>' + ''.join(cells) + '</tr>')
            emit('<table>' + ''.join(rows_html) + '</table>')

    if in_code and code_lines:
        html_parts.append(f'<pre class="code">{chr(10).join(code_lines)}</pre>')

    # --- pair each picture with the caption that follows it ---------------
    # An image and its caption were two independent paragraphs, so a page break
    # could fall between them: the Module-1 flowchart printed on one page and
    # "Figure 4: ..." at the top of the next. Wrapping the pair in a <figure>
    # (page-break-inside: avoid) keeps them together.
    paired = []
    i = 0
    while i < len(html_parts):
        chunk = html_parts[i]
        nxt = html_parts[i + 1] if i + 1 < len(html_parts) else ''
        is_img = chunk.startswith('<p class="center"><img') and chunk.endswith('</p>')
        is_cap = re.match(r'<p[^>]*>\s*(<em>)?\s*Figure \d+[:.]', nxt or '')
        if is_img and is_cap:
            body = chunk[len('<p class="center">'):-len('</p>')]
            cap = re.sub(r'^<p[^>]*>|</p>$', '', nxt)
            paired.append(f'<figure>{body}<figcaption>{cap}</figcaption></figure>')
            i += 2
            continue
        paired.append(chunk)
        i += 1
    html_parts = paired

    html_parts.append('</body></html>')
    html_content = '\n'.join(html_parts)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_file = f.name

    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    cmd = [chrome, '--headless=new', '--disable-gpu', '--no-sandbox',
           '--no-pdf-header-footer', '--print-to-pdf-no-header',
           f'--print-to-pdf={pdf_path}', f'file://{html_file}']
    subprocess.run(cmd, check=True, capture_output=True)
    Path(html_file).unlink()
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
