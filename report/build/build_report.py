"""Build ClinXAI_Final_Micro_Project_Report.docx (two passes so all cross-references resolve).

Usage (from report/build):  python build_report.py "<path to Format for Initial Pages.docx>"
Requires python-docx and Pillow. Run word_finalize.py afterwards to update the TOC/LOF/LOT and export the PDF.
"""
import csv
import json
import sys
from pathlib import Path

from engine import Report, set_pgnum
from refs import Citations
import content_front as cf
import content_mid as cm
import content_results as cr
import content_back as cb
import content_short as cs
import content_twenty as ct

PROJ = Path(__file__).resolve().parents[2]
OUT_DOCX = PROJ / "report" / "ClinXAI_Final_Micro_Project_Report.docx"          # full / compact editions
OUT_DOCX_CONCISE = PROJ / "report" / "ClinXAI_Concise_20_Page_Report.docx"     # concise edition

FILL = {
    "title": "ClinXAI: Transparent Multi-Modal Clinical Diagnostics Using LIME and SHAP",
    "name": "[STUDENT NAME]",
    "prn": "[PRN]",
    "class_div": "[CLASS / DIVISION]",
    "roll": "[ROLL NUMBER]",
    # Name exactly as printed on the official certificate template (spelling to be verified by the student).
    "guide": "Mr. Milind S. Khairrnar",
}


def load_data():
    j = lambda p: json.loads((PROJ / p).read_text(encoding="utf-8"))
    t = lambda p: (PROJ / p).read_text(encoding="utf-8")
    rows = lambda p: list(csv.DictReader(open(PROJ / p, encoding="utf-8")))
    return {
        "metrics": j("outputs/metrics/metrics.json"),
        "cases": j("outputs/case_studies/case_studies.json"),
        "case_csv": rows("outputs/case_studies/case_studies.csv"),
        "summary": rows("outputs/case_studies/test_set_lime_vs_shap.csv"),
        "additivity": j("outputs/metrics/shap_additivity.json"),
        "global_importance": rows("outputs/metrics/shap_global_importance.csv"),
        "desc": j("report/figures/report_descriptive_analysis.json"),
        "facts": j("report/evidence/report_facts.json"),
        "environment": t("report/evidence/environment.txt"),
        "pytest": t("report/evidence/pytest_verbose.txt"),
        "validation": t("report/evidence/output_validation.txt"),
        "browser": j("report/evidence/browser_check_results.json"),
        "train_log": t("report/evidence/train_model_console.txt"),
        "evaluate_log": t("report/evidence/evaluate_console.txt"),
    }


def build(template, D, labels, mode="compact"):
    """mode: 'full' (~120 pp), 'compact' (~35 pp) or 'concise' (~20 pp)."""
    R = Report(template, labels, chapter_page_breaks=(mode != "concise"))
    cite = Citations()

    # ---------------- Section 1: template pages (cover, [inner title], certificate, approval, declaration)
    R.copy_initial_pages(dict(FILL, inner_title=(mode != "concise")))
    # ---------------- Section 2: remaining preliminary pages
    s2 = R.new_section()
    (ct.prelims if mode == "concise" else cf.prelims)(R, D, cite)
    # ---------------- Section 3: technical body, references, appendices
    s3 = R.new_section()
    if mode == "concise":
        ct.body(R, D, cite)
        cb.references(R, cite)
        ct.appendices(R, D)
    elif mode == "full":   # original ~100-page technical body
        cf.chapter1(R, D, cite); cf.chapter2(R, D, cite); cm.chapter3(R, D, cite); cm.chapter4(R, D, cite)
        cr.chapter5(R, D, cite); cb.chapter6(R, D, cite); cb.chapter7(R, D, cite)
        cb.references(R, cite); cb.appendix_a(R); cb.appendix_b(R, D)
    else:      # compact ~20-page technical body
        for ch in (cs.chapter1, cs.chapter2, cs.chapter3, cs.chapter4, cs.chapter5, cs.chapter6, cs.chapter7):
            ch(R, D, cite)
        cb.references(R, cite); cs.appendix_a(R); cs.appendix_b(R, D)

    # A document ending in a table must still end with a paragraph; make that final paragraph 1 pt so it cannot
    # spill onto an otherwise empty page.
    from docx.enum.text import WD_LINE_SPACING
    from docx.shared import Pt as _Pt
    last = R.doc.paragraphs[-1]
    if not last.text.strip():
        last.paragraph_format.space_before = _Pt(0)
        last.paragraph_format.space_after = _Pt(0)
        last.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        last.paragraph_format.line_spacing = _Pt(1)
        mark = last._p.get_or_add_pPr()
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn as _qn
        rpr = OxmlElement("w:rPr"); sz = OxmlElement("w:sz"); sz.set(_qn("w:val"), "2"); rpr.append(sz); mark.append(rpr)

    s1, s2, s3 = R.doc.sections
    # Section 1: college header (logo) on every page; Roman numbering starting at i, hidden on the outer cover
    s1.different_first_page_header_footer = True
    R.college_header(s1.header)
    R.college_header(s1.first_page_header)
    s1.first_page_footer.is_linked_to_previous = False
    R.footer_page_number(s1.footer)
    set_pgnum(s1, "lowerRoman", 1)
    # Section 2: no logo header, Roman numbering continues
    s2.different_first_page_header_footer = False
    s2.header.is_linked_to_previous = False
    s2.footer.is_linked_to_previous = False
    R.footer_page_number(s2.footer)
    set_pgnum(s2, "lowerRoman", None)
    # Section 3: Arabic numbering restarts at 1 for Chapter 1 and runs continuously through the appendices
    s3.different_first_page_header_footer = False
    s3.header.is_linked_to_previous = False
    s3.footer.is_linked_to_previous = False
    R.footer_page_number(s3.footer)
    set_pgnum(s3, "decimal", 1)

    cp = R.doc.core_properties
    cp.title = FILL["title"]
    cp.subject = "Trustworthy and Responsible AI (ADCOR1PC303) — Technical Micro-Project Report"
    cp.author = FILL["name"]
    cp.keywords = "Explainable AI; LIME; SHAP; Random Forest; Breast cancer; Clinical decision support"
    return R, cite


def main():
    template = Path(sys.argv[1])
    mode = "full" if "--full" in sys.argv else "concise" if "--concise" in sys.argv else "compact"
    out_docx = {"concise": OUT_DOCX_CONCISE, "full": OUT_DOCX,
                "compact": PROJ / "report" / "archive_35page_version" / "ClinXAI_Report_35pages.docx"}[mode]
    D = load_data()
    R1, _ = build(template, D, {}, mode)
    R2, cite = build(template, D, dict(R1.collected), mode)
    assert R1.collected == R2.collected, "label assignment unstable between passes"
    unresolved = [p.text for p in R2.doc.paragraphs if "Figure ?" in p.text or "Table ?" in p.text]
    for t in R2.doc.tables:
        for row in t.rows:
            for c in row.cells:
                if "Figure ?" in c.text or "Table ?" in c.text:
                    unresolved.append(c.text)
    if unresolved:
        raise SystemExit(f"Unresolved references: {unresolved[:5]}")
    if R2.warnings:
        print("WARNINGS:", *R2.warnings, sep="\n  ")
    out_docx.parent.mkdir(parents=True, exist_ok=True)
    R2.doc.save(out_docx)
    figs = sum(1 for v in R2.collected.values() if v.startswith("Figure"))
    tabs = sum(1 for v in R2.collected.values() if v.startswith("Table"))
    print(f"saved {out_docx}\n  figures: {figs}  captioned tables: {tabs}  references cited: {len(cite.order)}")
    (PROJ / "report" / "build" / "build_manifest.json").write_text(json.dumps(
        {"labels": R2.collected, "references_order": cite.order, "warnings": R2.warnings}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
