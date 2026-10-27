"""Mechanical verification of the generated DOCX and PDF against the college formatting rules.

Usage (from report/build):  python verify_report.py   -> prints JSON and writes report/build/verification.json
"""
import json
import re
from pathlib import Path

import docx
import pymupdf
from docx.oxml.ns import qn

PROJ = Path(__file__).resolve().parents[2]
import sys as _sys
DOCX = Path(_sys.argv[1]) if len(_sys.argv) > 1 else PROJ / "report" / "ClinXAI_Final_Micro_Project_Report.docx"
PDF = DOCX.with_suffix(".pdf")
R = {}

# ------------------------------------------------------------------ DOCX: page setup and styles
d = docx.Document(str(DOCX))
R["sections"] = []
for s in d.sections:
    pg = s._sectPr.find(qn("w:pgNumType"))
    R["sections"].append({
        "page_w_mm": round(s.page_width.mm, 1), "page_h_mm": round(s.page_height.mm, 1),
        "top_in": round(s.top_margin.inches, 3), "bottom_in": round(s.bottom_margin.inches, 3),
        "left_in": round(s.left_margin.inches, 3), "right_in": round(s.right_margin.inches, 3),
        "orientation": str(s.orientation), "pgNum_fmt": pg.get(qn("w:fmt")) if pg is not None else None,
        "pgNum_start": pg.get(qn("w:start")) if pg is not None else None,
        "title_page": s.different_first_page_header_footer,
    })


def _resolve(st, getter):
    while st is not None:
        v = getter(st)
        if v is not None:
            return v
        st = st.base_style
    return None


DEFAULT_FONT = d.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr")).find(
    qn("w:rFonts")).get(qn("w:ascii"))


def style_info(name):
    """Effective style values, resolving base-style inheritance and document defaults."""
    st = d.styles[name]

    def font_of(s):
        rpr = s.element.rPr
        if rpr is not None and rpr.find(qn("w:rFonts")) is not None:
            return rpr.find(qn("w:rFonts")).get(qn("w:ascii"))
        return None

    def shd_of(s):
        ppr = s.element.pPr
        e = ppr.find(qn("w:shd")) if ppr is not None else None
        return e.get(qn("w:fill")) if e is not None else None

    size = _resolve(st, lambda s: s.font.size)
    sa = _resolve(st, lambda s: s.paragraph_format.space_after)
    al = _resolve(st, lambda s: s.paragraph_format.alignment)
    return {"font": _resolve(st, font_of) or DEFAULT_FONT, "size": size.pt if size else 12.0,
            "bold": _resolve(st, lambda s: s.font.bold), "italic": _resolve(st, lambda s: s.font.italic),
            "caps": _resolve(st, lambda s: s.font.all_caps), "align": str(al) if al is not None else "LEFT (default)",
            "line_spacing": _resolve(st, lambda s: s.paragraph_format.line_spacing),
            "space_after": sa.pt if sa is not None else None, "shading": _resolve(st, shd_of)}


R["styles"] = {n: style_info(n) for n in ["Normal", "Heading 1", "Heading 2", "Heading 3", "Figure Caption",
                                          "Table Caption", "Table Text", "Code", "Equation", "List Bullet"]}
# code paragraphs carry direct shading
code_paras = [p for p in d.paragraphs if p.style.name == "Code"]
R["code_paragraphs"] = len(code_paras)
R["code_paragraphs_shaded_F2F2F2"] = sum(1 for p in code_paras
                                         if p._p.pPr is not None and p._p.pPr.find(qn("w:shd")) is not None
                                         and p._p.pPr.find(qn("w:shd")).get(qn("w:fill")) == "F2F2F2")
# body paragraph fonts / sizes (direct formatting in Normal paragraphs after the template pages)
sizes = {}
for p in d.paragraphs:
    if p.style.name == "Normal":
        for r in p.runs:
            sz = r.font.size.pt if r.font.size else 12.0
            sizes[sz] = sizes.get(sz, 0) + 1
R["normal_run_sizes"] = sizes
# table cell font sizes
tsizes = {}
for t in d.tables[2:]:   # skip the two template tables (certificate / declaration)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    sz = r.font.size.pt if r.font.size else None
                    tsizes[sz] = tsizes.get(sz, 0) + 1
R["table_run_sizes"] = {str(k): v for k, v in tsizes.items()}
# headings
R["heading1"] = [p.text for p in d.paragraphs if p.style.name == "Heading 1"]
R["n_heading2"] = sum(1 for p in d.paragraphs if p.style.name == "Heading 2")
R["n_heading3"] = sum(1 for p in d.paragraphs if p.style.name == "Heading 3")
R["figure_captions"] = [p.text for p in d.paragraphs if p.style.name == "Figure Caption"]
R["table_captions"] = [p.text for p in d.paragraphs if p.style.name == "Table Caption"]
xml = d.element.xml
R["toc_fields"] = re.findall(r"TOC \\[^<]*", xml)
R["inline_images_body"] = len(d.inline_shapes)
R["unresolved_refs"] = sum(1 for p in d.paragraphs if "Figure ?" in p.text or "Table ?" in p.text)
R["placeholders_present"] = sorted(set(re.findall(r"\[(?:STUDENT NAME|PRN|CLASS / DIVISION|ROLL NUMBER)\]", xml)))
hdr = d.sections[0].header
R["section1_header_has_logo"] = bool(hdr._element.findall(".//" + qn("w:drawing")))
R["section1_firstpage_header_has_logo"] = bool(d.sections[0].first_page_header._element.findall(".//" + qn("w:drawing")))
R["section2_header_empty"] = not d.sections[1].header._element.findall(".//" + qn("w:drawing"))
R["section3_header_empty"] = not d.sections[2].header._element.findall(".//" + qn("w:drawing"))
R["footer_page_field"] = all("PAGE" in s.footer._element.xml for s in d.sections)

# ------------------------------------------------------------------ PDF: geometry, fonts, blank pages, numbering
pdf = pymupdf.open(str(PDF))
R["pdf_pages"] = pdf.page_count
R["pdf_page_sizes_pt"] = sorted({(round(p.rect.width), round(p.rect.height)) for p in pdf})
fonts = set()
for p in pdf:
    for f in p.get_fonts():
        fonts.add(re.sub(r"^[A-Z]{6}\+", "", f[3]))
R["pdf_fonts"] = sorted(fonts)
min_x0, max_x1, min_y0, max_y1 = 1e9, 0, 1e9, 0
blank, overflow = [], []
footer_labels = []
for i, p in enumerate(pdf):
    W, H = p.rect.width, p.rect.height
    blocks = [b for b in p.get_text("blocks") if b[4].strip()]
    imgs = p.get_images()
    if not blocks and not imgs:
        blank.append(i + 1)
    # footer label = lowest text block on the page
    if blocks:
        low = max(blocks, key=lambda b: b[3])
        footer_labels.append(low[4].strip())
    for w in p.get_text("words"):      # word boxes exclude the trailing spaces Word lets hang into the margin
        x0, y0, x1, y1 = w[:4]
        if y0 > H - 60:
            continue
        min_x0, max_x1 = min(min_x0, x0), max(max_x1, x1)
        if x0 < 90.0 - 1 or x1 > W - 72.0 + 1:
            overflow.append((i + 1, round(x0, 1), round(x1, 1), w[4]))
    for img in p.get_image_info():
        x0, y0, x1, y1 = img["bbox"]
        if x0 < 90.0 - 1 or x1 > W - 72.0 + 1:
            overflow.append((i + 1, "image", round(x0, 1), round(x1, 1)))
R["pdf_text_min_x0_pt"], R["pdf_text_max_x1_pt"] = round(min_x0, 1), round(max_x1, 1)
R["pdf_expected_left_pt"], R["pdf_expected_right_edge_pt"] = 90.0, round(595.3 - 72.0, 1)
R["pdf_blank_pages"] = blank
R["pdf_margin_violations"] = overflow[:20]
R["pdf_n_margin_violations"] = len(overflow)
R["pdf_footer_labels"] = footer_labels
roman = [l for l in footer_labels[:25] if re.fullmatch(r"[ivxl]+", l)]
arabic = [int(l) for l in footer_labels if l.isdigit()]
R["roman_sequence"] = roman
R["arabic_first_last"] = [arabic[0], arabic[-1]] if arabic else None
R["arabic_continuous"] = arabic == list(range(arabic[0], arabic[0] + len(arabic))) if arabic else False
R["pdf_bookmarks"] = len(pdf.get_toc())
out = PROJ / "report" / "build" / ("verification_concise.json" if "Concise" in DOCX.name else "verification.json")
out.write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in R.items() if k not in ("pdf_footer_labels", "figure_captions", "table_captions")},
                 indent=1, default=str))
