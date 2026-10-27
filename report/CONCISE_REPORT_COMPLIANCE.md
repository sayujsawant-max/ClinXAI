# ClinXAI — Concise Report Compliance (20-page edition)

**Report:** *ClinXAI: Transparent Multi-Modal Clinical Diagnostics Using LIME and SHAP* · ADCOR1PC303 · 2026–27
**Checked on:** 2026-10-27, against the final build. Every value below was measured from the generated DOCX and PDF.

Status key: ✅ verified · ⚠️ verified with a deviation (explained) · ⬜ for the student · ❌ not verified

---

## 1. Files

| File | Status |
|---|---|
| `report/ClinXAI_Concise_20_Page_Report.docx` | ✅ New. Saved by Microsoft Word with fields updated. Office Open XML schema validation: *All validations PASSED*. |
| `report/ClinXAI_Concise_20_Page_Report.pdf` | ✅ New. **20 pages (PDF page count verified)**, all A4 (595 × 842 pt). |
| `report/ClinXAI_Final_Micro_Project_Report.docx` / `.pdf` | ✅ The original 120-page report is **untouched** (restored to its original name; PDF page count re-checked at 120). |
| Earlier 35-page draft | Kept in `report/archive_35page_version/` |

Rebuild: run `python build_report.py "<Initial Pages template>.docx" --concise`, then `python word_finalize.py ..\ClinXAI_Concise_20_Page_Report.docx` (from `report/build`).

## 2. Page allocation (target vs actual)

| Part | Target | Actual | Printed pages |
|---|---|---|---|
| Preliminary pages | 7 | **7** | i–vii |
| Chapter 1 | 1 | 1 | 1 |
| Chapter 2 | 2 | ≈ 1.7 | 2–3 |
| Chapter 3 | 1 | ≈ 1.3 | 3–4 |
| Chapter 4 | 2 | ≈ 1.3 | 5–6 |
| Chapter 5 | 3 | ≈ 3.7 | 6–9 |
| Chapter 6 | 1 | 1 | 10 |
| Chapter 7 | 1 | ≈ 0.6 | 11 |
| References and appendices | 2 | ≈ 2.4 | 11–13 |
| **Total** | **20** | **20** | i–vii + 1–13 |

Chapter 5 got slightly more than its share, so that all the required results and figures stay legible.

## 3. College formatting rules

| Requirement | Measured result | Status |
|---|---|---|
| A4 paper | All sections 210 × 297 mm; all PDF pages 595 × 842 pt | ✅ |
| Left margin 1.25″; others 1″ | Set in every section. 0 words, images or table borders outside the text area (word-level PDF check). | ✅ |
| Times New Roman | Normal, all headings, captions and table text resolve to TNR. Code and equations use Consolas, which the guidelines allow. | ✅ |
| Body 12 pt, line spacing 1.5 | Normal style is 12 pt at 1.5 spacing. All 263 body text runs are 12 pt, apart from inline code (Consolas 10.5 pt) and the template pages' own sizes. | ✅ |
| Chapter headings 16 pt bold centred caps | Heading 1 is 16 pt bold, centred, all caps | ✅ |
| Section headings 14 pt | Heading 2 is 14 pt bold left (all 52 numbered sections present) | ✅ |
| Subsection headings 12 pt | Heading 3 style defined at 12 pt bold; no third-level headings were needed | ✅ |
| Captions and tables 10 pt | Captions are 10 pt italic; all 190 table-cell runs are 10 pt | ✅ |
| Roman, then Arabic page numbers | Cover = i (number hidden), then ii–vii. Arabic 1–13, continuous to the end of Appendix B. Numbers centred in the footer. | ✅ |
| No reduction by smaller fonts, narrower margins or tighter body spacing | None of these was changed. The reduction comes from removing repeated text, tables, screenshots and code, and from letting chapters flow without a forced page break. | ✅ |
| Updateable TOC, LOF, LOT | Real Word fields, updated by Word. 9 of 9 figures and 4 of 4 tables listed. | ✅ |
| No blank pages; no unresolved references | 0 / 0 | ✅ |

## 4. Mandatory content

| Item | Location | Status |
|---|---|---|
| College cover (logo, programme lines, title block) | i | ✅ Copied from the template |
| Certificate | ii | ✅ Template text unchanged (signature blank) |
| Approval page | iii | ✅ Template text unchanged (examiner blank) |
| Declaration | iv | ✅ Template text unchanged (signature blank) |
| CO/PO alignment | v | ⚠️ Condensed: the 2 applicable official rows are shown word for word, and a note lists the 4 components not implemented |
| CIAP rubric | v | ✅ Official rubric reproduced word for word, plus a marks and signature line |
| Abstract and keywords | vi | ✅ 203 words, 7 keywords |
| Contents / list of figures / list of tables / abbreviations | vi / vii / vii / vii | ✅ |
| Chapters 1–7 with official titles, in order | 1–11 | ✅ |
| IEEE references | 11–12 | ✅ 16 entries |
| Appendix A / Appendix B | 13 / 13 | ⚠️ Condensed (see §7, item 1) |

## 5. Required results (each one found in the PDF text by an automated search)

| Item | Value | Location | Status |
|---|---|---|---|
| Accuracy, precision, recall, F1, ROC-AUC | 97.37 %, 100 %, 92.86 %, 96.30 %, 0.9944 | Abstract, Table 5.1 | ✅ |
| Confusion matrix | TN = 72, FP = 0, FN = 3, TP = 39 | §5.4, Figure 5.1 | ✅ |
| Top-5 overlap, Jaccard, Spearman, directional disagreement | 3.66/5, 0.62, 0.70, 28.9 % | Abstract, §5.9 | ✅ |
| SHAP additivity | 4.4 × 10⁻¹⁶ | §5.7 | ✅ |
| Compact table of all five case studies (#70, #74, #100, #86, #73) | — | Table 5.2 | ✅ |
| #86 and #73: malignant but predicted benign; low LIME fidelity; LIME–SHAP disagreement and why it matters | R² 0.03 / 0.06; 0/5 and 1/5 shared features; 4 sign flips each | §5.6–5.9, Figures 5.3–5.5 | ✅ |
| Interpretability trade-off and baseline | LR 96.49 %, AUC 0.9960 | Table 5.1, §5.10 | ✅ |
| Responsible AI: oversight, privacy, limitations, not clinically validated | "not a medical device and is not clinically validated"; "No compliance, certification or clinical validation is claimed" | Chapter 6, §7.3 | ✅ |

**Required figures:** architecture (3.1), DFD (3.2), confusion matrix and ROC (5.1), SHAP global importance and beeswarm (5.2), LIME local explanation and SHAP waterfall (5.3), LIME–SHAP comparison (5.4), confidence analysis (5.5), dashboard and what-if screenshots (5.6), error-handling screenshot (5.7). ✅ All were checked for legibility in the rendered PDF.

**Equations kept (with symbols explained):** the RF average and Gini impurity (2.1), the LIME objective (2.2), SHAP additivity (2.3), the Shapley value (2.4), and Jaccard and Spearman (2.5). ✅

## 6. References

| Check | Result |
|---|---|
| Every in-text number matches an entry | ✅ Automated check: 16 cited = 16 listed; none missing, none uncited |
| Numbered in order of first use | ✅ [1] … [16] in sequence |
| Checked online earlier in this session | UCI dataset, Street et al. 1993, Slack et al. 2020, WHO/IARC 2022 figures (and the ICMR guidelines, now mentioned in text without a citation) |
| Others | ⚠️ Standard citations, not individually re-checked online; spot-check before submission |

## 7. Departures from the college guidelines (flagged, not hidden)

1. **Appendix A is condensed.** The official title "Complete Source Code Listings / Core Configuration Files" is kept, but the appendix holds a file inventory (10 files with line counts) and the key LIME–SHAP comparison routine. **This departs from the expectation of complete listings.** The full code is submitted in the project folder, and the complete listings remain in the original 120-page report (Appendix A there). ⚠️
2. **Appendix B is condensed** to the final lines of the 24-test log and a verification summary table. The full logs are in `report/evidence/` and in the 120-page report. ⚠️
3. **Shared preliminary pages.** CO/PO and rubric share page v; the abstract and contents share page vi; the figure, table and abbreviation lists share page vii. The guidelines specify the order but do not require separate pages. ⚠️
4. **Inner title page omitted.** Your brief lists the cover, certificate, approval and declaration. The template has only one cover design, so the duplicate inner title page was dropped. ⚠️
5. **Chapters do not start on new pages.** The guidelines don't require it; this was the largest saving without touching font size or spacing. ⚠️
6. **Contents-list entries** (TOC, LOF, LOT) are single-spaced. They are generated lists, not body paragraphs; body text stays at 1.5. ⚠️
7. **Code** is 9 pt Consolas, single-spaced on 5 % grey. The guidelines give no size for code; this matches the full report. ⚠️
8. **Abbreviations** are reduced to the 10 used in this edition.
9. **SHAP force plot.** Requirement 8 asks for a "waterfall/force plot"; the waterfall plot (Figure 5.3b) is shown. Force plots remain in `outputs/figures/` and in the 120-page report.
10. **Removed (details only, not results):** the literature comparison table, the per-case LIME/SHAP top-5 tables, the LIME seed-stability table, extra per-case figures, the dataset-distribution figure and the long code excerpts. The headline value of each is stated in the text (for example LIME seed stability of 0.39 for #86).

**Contradictions inside the official documents** (unchanged from the full report, ⬜ for you to confirm):
- **Guide's name:** "Mr. Milind S. Khairrnar" is copied as printed.
- **Programme naming** differs between the header and the certificate.
- **Declaration** uses "We".
- **Rubric marks:** titled 25 marks, but five criteria scored 1–4 give a maximum of 20. No conversion was invented.
- **Template formatting:** the Initial Pages template is US Letter with Aptos fonts. A4 was used, and the template fonts were kept on its own pages.

## 8. Before submission

| Item | Status |
|---|---|
| Replace `[STUDENT NAME]`, `[PRN]`, `[CLASS / DIVISION]`, `[ROLL NUMBER]` (Word: Find & Replace) | ⬜ |
| Signatures, examiner, dates, place, marks (left blank on purpose) | ⬜ |
| After editing: Ctrl+A, then F9, then save as PDF again. Check the PDF still has 20 pages, since longer names can shift lines. | ⬜ |
| Plagiarism check; physical print check | ❌ not done |

## 9. Integrity

No application code, model, metric, case study or experimental output was changed. All numbers are read from the saved outputs at build time. No result, screenshot, signature, approval, source or clinical claim was fabricated.
