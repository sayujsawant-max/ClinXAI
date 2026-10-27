# ClinXAI Report — Compliance Checklist

**Report:** *ClinXAI: Transparent Multi-Modal Clinical Diagnostics Using LIME and SHAP*
**Course:** Trustworthy and Responsible AI (ADCOR1PC303) · Academic Year 2026–27
**Checked on:** 2026-10-27, against the final build of the DOCX and PDF.

Status key: ✅ verified · ⚠️ verified with a note or deviation · ⬜ to be completed by the student · ❌ not verified

---

## 1. Generated files

| File | Status | Details |
|---|---|---|
| `report/ClinXAI_Final_Micro_Project_Report.docx` | ✅ exists | 4.7 MB. Opened, field-updated and re-saved by Microsoft Word. Passes the Office Open XML schema validation (`validate.py`: "All validations PASSED"). |
| `report/ClinXAI_Final_Micro_Project_Report.pdf` | ✅ exists | 8.5 MB, **120 pages**, A4. Exported by Microsoft Word with heading bookmarks (97 entries). |
| `report/REPORT_COMPLIANCE_CHECKLIST.md` | ✅ | This file. |
| `report/figures/` | ✅ | 13 real dashboard screenshots and 5 report-only figures (see §8). |
| `report/evidence/` | ✅ | Raw logs and facts used in Appendix B. |
| `report/build/` | ✅ | Build scripts, `verification.json` (mechanical checks) and `page_map.json`. |

**How to regenerate:** run `python build_report.py "<Initial Pages template>.docx"` and then `python word_finalize.py` from `report/build`. This needs python-docx, Pillow, pywin32 and Microsoft Word. Run `verify_report.py` afterwards to repeat the checks.

## 2. Source documents analysed

| Document | How it was used |
|---|---|
| `TRAI - Micro-Project Report - Format for Initial Pages.docx` | **Copied, not imitated.** The cover, certificate, approval and declaration paragraphs and tables were taken from the template's XML, along with its logo image (`word/media/image1.png`) and header text. Only the blanks were filled in. |
| `TRAI - Micro_Project_Report_Format.docx` | Formatting authority (Section 1). Mandatory sequence (Section 2). Chapter content guide (Section 3). The CO/PO mapping table and the 25-mark rubric (Sections 4–5) were reproduced word for word. |
| Project sources | `FINAL_VALIDATION_REPORT.md`, `docs/PROJECT_SUMMARY.md`, `outputs/`, and all source code. Numbers are read from these files when the report is built, not typed by hand. |

## 3. Formatting rules (guidelines, Section 1)

Checked mechanically with `report/build/verify_report.py`, which reads the DOCX styles and measures the PDF geometry, and by visually inspecting every page.

| Rule | Requirement | Measured result | Status |
|---|---|---|---|
| Page size | A4, portrait | All 3 sections are 210.0 × 297.0 mm, portrait. All 120 PDF pages are 595 × 842 pt. | ✅ |
| Margins | Top 1.0″, bottom 1.0″, left 1.25″, right 1.0″ | Set exactly in all 3 sections. In the PDF, no word, image or table border falls outside the 1.25″ / 1.0″ text area (0 violations, word-level check). | ✅ |
| Body font | Times New Roman | Normal, headings, captions and table text all resolve to Times New Roman. TNR regular, bold and italic are embedded in the PDF. | ✅ |
| Monospace | Consolas or Courier New for code, equations, logs and configuration | Code blocks, equations and inline code use Consolas (embedded). | ✅ |
| Chapter headings | 16 pt, bold, centred, ALL CAPS | Heading 1 is 16 pt, bold, centred, all caps. | ✅ |
| Section headings | 14 pt, bold, left | Heading 2 is 14 pt, bold, left (76 used). | ✅ |
| Sub-section headings | 12 pt, bold, left | Heading 3 is 12 pt, bold, left (5 used). | ✅ |
| Body text | 12 pt, regular, justified | Normal is 12 pt and justified. Every body run is 12 pt except inline code (Consolas 10.5 pt) and the template pages' own sizes. | ✅ |
| Captions, footnotes, tables | 10 pt, regular or italic | Figure and table captions are 10 pt italic. All 1,219 table-cell runs are 10 pt. | ✅ |
| Line spacing | 1.5 with 6 pt after | Normal and bullets are 1.5 spacing. Normal has 6 pt after; bullets have 3 pt after. | ⚠️ Bullets use 3 pt after, so lists read as one block. |
| Code and equations | Single spacing, 5 % light-grey fill | All 2,399 code paragraphs are single-spaced with fill F2F2F2 (5 % grey). Equations are the same. | ✅ |
| Code size | User request: about 10 pt | Code is 9 pt, equations 10 pt. | ⚠️ 9 pt reduces wrapping of 100-character source lines. Long lines wrap with a hanging indent. |
| Preliminary page numbers | Lowercase Roman | Section 1 uses lowerRoman from i. Section 2 continues. Printed labels run ii–xix. | ✅ |
| Body page numbers | Continuous Arabic, centred footer | Section 3 restarts at 1. Printed labels run 1 → 101 with no gaps, from Chapter 1 to the end of Appendix B. The PAGE field is centred in every footer. | ✅ |
| Outer cover number | (not specified) | The cover counts as page i, but its number is hidden (different first-page footer). | ⚠️ Conventional choice. Untick "Different First Page" in Word to show "i". |
| Word heading styles | Real styles, not simulated | Heading 1/2/3 and custom caption, table, code and equation styles are used throughout. No spacing-based layout. | ✅ |
| Updateable TOC | Automatic | Real `TOC \o "1-3" \h \z \u` field, updated by Word (no placeholders left). | ✅ |
| List of Figures / Tables | Automatic | Real TOC fields built from the "Figure Caption" and "Table Caption" styles. 34 of 34 figures and 31 of 31 tables are listed with page numbers. | ✅ |
| Tables within margins | Required | The builder refuses any table wider than 6.0″. Fixed layout. Header rows repeat on long tables, and short tables are kept on one page. | ✅ |
| Figure and table numbering | By chapter (Figure 5.1, …) | 34 figures and 31 tables numbered by chapter (B.x in Appendix B). Every in-text reference is generated, with 0 unresolved. | ✅ |
| Blank pages | None | 0 blank pages in the PDF. | ✅ |

## 4. Mandatory report sequence (guidelines, Section 2)

| # | Required item | Location (printed page) | Status |
|---|---|---|---|
| 1a | Outer cover page | PDF p.1 (i, number hidden). Template layout and logo. | ✅ |
| 1b | Inner title page | ii. Same template layout (the template provides one cover design). | ✅ |
| 2 | Certificate of authenticity and evaluation approval | Certificate on iii; Approval for Project Report on iv. Template wording unchanged. | ✅ (signatures left blank) |
| 3 | Student declaration and anti-plagiarism undertaking | v. Template wording unchanged; data row added. | ✅ (signature left blank) |
| 4 | Course articulation and CO/PO/PSO alignment sheet | vi–vii | ✅ |
| 5 | CIAP 25-mark rubric evaluation sheet | viii | ✅ (see §10, item 6) |
| 6 | Abstract and keywords | ix. 292 words; 7 keywords. | ✅ |
| 7 | Table of contents | x–xiii | ✅ |
| 7 | List of figures | xiv–xvi | ✅ |
| 7 | List of tables | xvii–xviii | ✅ |
| 7 | List of abbreviations | xix (38 entries) | ✅ |
| II | Chapters 1–7 | 1, 4, 10, 18, 26, 52, 56 | ✅ |
| III | References (IEEE) | 59–61 | ✅ |
| III | Appendix A: complete source code listings and core configuration files | 62–94 | ✅ |
| III | Appendix B: raw diagnostic trace logs, audit tables and verification sheets | 95–101 | ✅ |

## 5. Chapter coverage

| Chapter | Required sub-sections present | Status |
|---|---|---|
| 1 Problem Definition & Operational Relevance | 1.1 Problem statement · 1.2 Clinical/societal relevance · 1.3 Four measurable objectives with Bloom verbs (Table 1.1) · 1.4 Scope, boundaries, assumptions, constraints, and what "multi-modal" means in the title | ✅ |
| 2 Theory, Literature Review & Mathematical Framework | 2.1–2.9 as requested. 11 numbered equations (2.1–2.11) covering the RF average, Gini, the LIME objective, loss and kernel, the ridge surrogate, the SHAP additive form, local accuracy, the Shapley value, Jaccard and Spearman. Chapter 5 adds 5 metric equations. Every symbol is defined. LIME vs SHAP table (2.1) and literature table (2.2). Local fidelity, consistency, stability and cost are distinguished. | ✅ |
| 3 Architecture, Design Pipeline & Workflow | 3.1–3.8. Architecture diagram, data-flow diagram, explanation workflow, UI flow, component interface table, JSON interface schema. All diagrams match the implemented files. | ✅ |
| 4 Implementation | 4.1–4.9. 12 code excerpts pulled from the real files, each with its file name and line range. 2 pseudocode algorithms. Guardrail table. Module table with line counts. | ✅ |
| 5 Evaluation & Results | 5.1–5.11. All five case studies (#70, #74, #100, #86, #73) with model output, LIME top-5, SHAP top-5, agreement, reasons and clinical limitation for each. | ✅ |
| 6 Societal Impact, Ethics, Safety & Security | 6.1–6.7 as requested. Includes the guidelines' required items: vulnerability and robustness audit (Table 6.1), legal and regulatory alignment explicitly *not* claimed as compliance (Table 6.2), and SDG 3. | ✅ |
| 7 Conclusion, Limitations & Future Work | 7.1–7.4. Covers local instability, SHAP background assumptions, small dataset, distribution shift, lack of external validation, multimodal future work and the need for medical-expert validation. | ✅ |

## 6. Experimental evidence (all values read from generated files)

| Required item | Value in report | Source file | Report location | Status |
|---|---|---|---|---|
| Accuracy | 97.37 % | `outputs/metrics/metrics.json` | Abstract, Table 5.2, §5.3 | ✅ |
| Precision | 100 % | same | same | ✅ |
| Recall | 92.86 % | same | same | ✅ |
| F1-score | 96.30 % | same | same | ✅ |
| ROC-AUC | 0.9944 | same | same, Figure 5.2 | ✅ |
| Confusion matrix | TN 72, FP 0, FN 3, TP 39 | same | §5.4, Figure 5.1 | ✅ |
| SHAP additivity | max error 4.4 × 10⁻¹⁶ | `outputs/metrics/shap_additivity.json` | §5.7, Table 5.10, Appendix B.7 | ✅ |
| Mean top-5 overlap | 3.66 / 5 | `outputs/case_studies/case_studies.json` | Abstract, Table 5.10 | ✅ |
| Mean Jaccard | 0.62 | same | same | ✅ |
| Mean Spearman | 0.70 | same | same | ✅ |
| Direction disagreement | 28.9 % (33 of 114 patients) | same | same | ✅ |
| Five case studies | #70, #74, #100, #86, #73 | `case_studies.csv/json` | Table 5.4, §5.8, Appendix B.9 | ✅ |
| #86 and #73 as false negatives | P = 0.297 and 0.160, actual malignant | same, plus independent validation | §5.8, Table 5.12 | ✅ |
| Low LIME fidelity discussion | R² 0.03 (#86) and 0.06 (#73); mean 0.27 | same | §5.6, §5.8, §5.9, §7.2 | ✅ |
| Logistic Regression baseline | 96.49 % accuracy, AUC 0.9960 | `metrics.json` | Table 5.2, Table 5.14 | ✅ |
| Test evidence | 24/24 pytest; 35/35 output validation; 34/34 browser checks; clean install | `report/evidence/*` | Table 5.15, Appendix B | ✅ |

**Analysis added for the report (descriptive, not a new experiment):** §5.9 adds statistics computed from the saved `test_set_lime_vs_shap.csv` by `report/make_report_figures.py`: the confidence-versus-agreement correlations (ρ = 0.60 and 0.49), the confident and uncertain group means, and the profile of the third false negative, #385. Nothing was retrained or re-explained, and the report text says so. The raw output is in `report/figures/report_descriptive_analysis.json` (Appendix B.10).

## 7. CO/PO/PSO mapping and rubric

| Item | Status | Note |
|---|---|---|
| Official CO/PO table reproduced word for word | ✅ | Two columns added: "Applicability to ClinXAI" and "ClinXAI Evidence". |
| Explainability row (CO 1, BL 2/BL 3, PO1, PO2, PO5, PSO1) | ✅ | Marked as the applicable core of the project. |
| Dashboard row (CO 1–CO 3, BL 5/BL 6) | ⚠️ | Marked applicable within the explainability scope only. The table states the app runs locally and is not publicly deployed, and the note says CO 2 and CO 3 activities are not implemented. |
| Fairness, adversarial, privacy and model-card rows | ✅ | Shown as "Not applicable / not implemented". No false claims. |
| Rubric reproduced word for word | ✅ | See the mark conflict in §10, item 6. |

## 8. Figures and screenshots

| Group | Count | Origin |
|---|---|---|
| Project outputs | 16 | `outputs/figures/*.png`, generated by `train_model.py` and `evaluate.py`: architecture, confusion matrix, ROC, SHAP bar, beeswarm, LIME ×2, waterfall ×2, force, LIME-vs-SHAP ×5, case overview |
| Real dashboard screenshots | 13 | Captured from the running app (`streamlit run app.py`) in Microsoft Edge by Playwright at 1440 px width and 2× density. Not edited. Includes the error-handling (out-of-range warning) and what-if screenshots. |
| Report-only figures | 5 | Generated by `report/make_report_figures.py` from the dataset and saved outputs: dataset distribution, data-flow diagram, explanation workflow, UI interaction flow, confidence versus agreement. |
| Placeholders | **0** | Every requested figure exists, so no placeholder was needed. |

**Terminal output** is shown as real console text in monospace (§5.11 and Appendix B), not as screenshots of a terminal window. ⚠️ If your faculty specifically wants terminal *images*, capture a PowerShell window running `python -m pytest -v` and insert it in §5.11.

## 9. References

| Check | Status |
|---|---|
| IEEE format, numbered in order of first citation | ✅ 31 references, [1]–[31] |
| Every listed reference is cited, and no citation is missing | ✅ The builder lists only cited entries; 0 orphans |
| Foundational LIME and SHAP sources | ✅ Ribeiro et al. 2016 (KDD), Lundberg & Lee 2017 (NeurIPS), Lundberg et al. 2020 (Nature MI), Shapley 1953 |
| Checked online in this session | ✅ 6 entries: UCI dataset DOI 10.24432/C5DW2B (year corrected to 1993, as UCI suggests); Street et al. 1993, SPIE 1905, pp. 861–870; Anchors, AAAI 2018, pp. 1527–1535; Slack et al., AIES 2020, pp. 180–186; WHO / IARC 2022 figures (2.3 million cases, 670,000 deaths); ICMR 2023 guideline title and principles |
| Remaining 25 entries | ⚠️ Well-known works cited from established bibliographic details, but not individually re-checked online in this session. Spot-check DOIs and page numbers before submission. |
| Living web sources | ⚠️ The WHO fact sheet and the SHAP, LIME and Streamlit documentation pages change over time. Add the date you access them if your department requires it. |

## 10. Contradictions between the official documents (identified, not silently resolved)

1. **Page size and margins.** The Initial Pages template is US Letter with 1″ margins. The guidelines require A4 with a 1.25″ left margin. **A4 and the guideline margins were used.** The template's logo, 6.5″ wide, was scaled to 6.0″ to fit the narrower text area, keeping its proportions.
2. **Typeface.** The guidelines require Times New Roman throughout. The Initial Pages template uses Aptos for the cover and student details, *Old English Text MT* for "Certificate" and *Lucida Calligraphy* for the certificate wording. **The template's fonts were kept on the five template pages** (per your instruction to use the Initial Pages template for those pages). Times New Roman is used everywhere else.
3. **Programme naming.** The header says "UG Program in Electronics and Computer Science / Honours in Emerging Area offered by Department of Artificial Intelligence and Data Science". The certificate says "B. Tech. Degree in Artificial Intelligence and Data Science". Both are kept exactly as printed. ⬜ Confirm which programme applies to you.
4. **Guide name.** The certificate template prints "Mr. Milind S. Khairrnar" (double "r"). It is copied exactly, also into the cover's Guide field. ⬜ Check the spelling with your guide.
5. **Plural declaration.** The declaration text uses "We / our" (written for a group). It is kept word for word. ⬜ Ask your guide whether a single student may change it to "I / my".
6. **Rubric marks.** The rubric is titled "25 Marks". It has five criteria on a 4-point scale (maximum 20 raw points) with weights that sum to 100 %. It is reproduced exactly. The evaluator table leaves every mark blank under a "Total (CIAP — 25 Marks)" label, and **no conversion was invented.**
7. **Chapter 2 title.** Guidelines Section 3 says "Theoretical Formulation & Mathematical Framework". The mandatory sequence and your brief say "…Literature Review & Mathematical Framework". The longer title was used.
8. **Chapter 6 sub-headings.** The guidelines list 6.1 Vulnerability, 6.2 Legal, 6.3 SDG. Your brief lists seven sub-headings. **Your headings were used**, and the guideline topics are covered inside them (Table 6.1 robustness audit, Table 6.2 regulatory alignment, §6.7 SDG 3).
9. **One cover design for two pages.** The sequence asks for an outer cover *and* an inner title page, but the template provides one layout. It is used for both.
10. **Dashboard benchmark.** The official row says "Fully responsive live dashboard deployed on Streamlit or Gradio". ClinXAI runs locally and was checked at desktop width only. This is stated in the table and not overclaimed.

## 11. Items for the student to complete before submission

| Item | Where | Status |
|---|---|---|
| `[STUDENT NAME]` | Outer cover, inner title, certificate, approval, declaration | ⬜ Use Find & Replace in Word, or edit `FILL` in `build_report.py` and rebuild |
| `[PRN]`, `[CLASS / DIVISION]` | Outer cover and inner title | ⬜ |
| `[ROLL NUMBER]` | Certificate and declaration | ⬜ |
| Guide signature, examiner name and signature, date, place | Certificate, approval, declaration, rubric sheet | ⬜ Left blank on purpose; no signatures or approvals were invented |
| Rubric marks | Rubric sheet | ⬜ Committee only |
| Update fields after any edit | Whole document | ⬜ Ctrl+A, then F9 in Word (updates the TOC and lists) |
| Similarity / plagiarism check | Whole report | ❌ Not run (no checker available here) |
| Physical print check | Printed copy | ❌ Not done. Only the PDF was inspected, page by page. |
| Department-specific extras (for example a running header on body pages) | — | ⬜ The guidelines specify none, so body pages have no header. The college logo appears only on the template pages, as in the template. |

## 12. Integrity statements

- No source code, model, evaluation data or generated experimental result was modified to produce this report. The report scripts only read `outputs/`, `models/` and the dataset.
- No metric, screenshot, signature, approval, source or clinical claim was fabricated. The report states that ClinXAI is not clinically validated, not a medical device, and not compliant or certified under any framework.
- The three figure-styling fixes made earlier during final validation (tick spacing, value labels, and force-plot number format in `src/visualization.py`) are recorded in `FINAL_VALIDATION_REPORT.md`. No figure, code or result was altered while producing this report.
