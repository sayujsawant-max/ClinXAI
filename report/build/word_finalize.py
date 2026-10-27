"""Open the generated report in Microsoft Word, update TOC / List of Figures / List of Tables / page fields,
save it, and export the PDF. Requires Microsoft Word (Windows) and pywin32.

Usage (from report/build):  python word_finalize.py
"""
import json
import sys
from pathlib import Path

import pythoncom
import win32com.client as win32

PROJ = Path(__file__).resolve().parents[2]
import sys as _sys
DOCX = Path(_sys.argv[1]) if len(_sys.argv) > 1 else PROJ / "report" / "ClinXAI_Final_Micro_Project_Report.docx"
PDF = DOCX.with_suffix(".pdf")

WD_STAT_PAGES = 2
WD_EXPORT_PDF = 17
WD_EXPORT_OPTIMIZE_PRINT = 0
WD_EXPORT_HEADING_BOOKMARKS = 1
WD_FORMAT_DOCX = 16


def main():
    pythoncom.CoInitialize()
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(DOCX), ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
        # Contents / figure / table list entries: single-spaced list styles (Word built-ins wdStyleTOC1..3 = -20..-22).
        # Body paragraphs keep their 1.5 spacing; only the generated list entries are affected.
        for style_id in (-20, -21, -22):
            pf = doc.Styles(style_id).ParagraphFormat
            pf.LineSpacingRule = 0      # wdLineSpaceSingle
            pf.SpaceBefore = 0
            pf.SpaceAfter = 2
        doc.Repaginate()
        for _ in range(3):              # TOC length changes pagination, so update until stable
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
            doc.Fields.Update()
            for story in doc.StoryRanges:
                story.Fields.Update()
            doc.Repaginate()
        info = {
            "pages": doc.ComputeStatistics(WD_STAT_PAGES),
            "tables_of_contents": doc.TablesOfContents.Count,
            "toc_entries": [doc.TablesOfContents(i).Range.Paragraphs.Count for i in range(1, doc.TablesOfContents.Count + 1)],
            "inline_shapes": doc.InlineShapes.Count,
            "tables": doc.Tables.Count,
            "sections": doc.Sections.Count,
        }
        # Read back the page-number format of each section as Word sees it
        info["section_page_formats"] = []
        for i in range(1, doc.Sections.Count + 1):
            pn = doc.Sections(i).Footers(1).PageNumbers  # wdHeaderFooterPrimary = 1
            info["section_page_formats"].append({"style": pn.NumberStyle, "restart": bool(pn.RestartNumberingAtSection),
                                                 "start": pn.StartingNumber})
        doc.SaveAs2(str(DOCX), FileFormat=WD_FORMAT_DOCX)
        doc.ExportAsFixedFormat(str(PDF), WD_EXPORT_PDF, OpenAfterExport=False, OptimizeFor=WD_EXPORT_OPTIMIZE_PRINT,
                                CreateBookmarks=WD_EXPORT_HEADING_BOOKMARKS, DocStructureTags=True,
                                BitmapMissingFonts=True, UseISO19005_1=False)
        doc.Close(SaveChanges=0)
        print(json.dumps(info, indent=1))
    finally:
        word.Quit()


if __name__ == "__main__":
    sys.exit(main())
