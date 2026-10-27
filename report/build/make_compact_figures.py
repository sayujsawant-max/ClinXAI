"""Side-by-side composites of existing project figures for the compact report (no new results).

Usage (from report/build):  python make_compact_figures.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJ = Path(__file__).resolve().parents[2]
OUT_FIG = PROJ / "outputs" / "figures"
REP_FIG = PROJ / "report" / "figures"


def side_by_side(paths, out, height=900, gap=40, labels=("(a)", "(b)", "(c)")):
    ims = [Image.open(p).convert("RGB") for p in paths]
    ims = [im.resize((int(im.width * height / im.height), height), Image.LANCZOS) for im in ims]
    top = 60
    W = sum(im.width for im in ims) + gap * (len(ims) - 1)
    canvas = Image.new("RGB", (W, height + top), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("timesbd.ttf", 44)
    except OSError:
        font = ImageFont.load_default()
    x = 0
    for im, lab in zip(ims, labels):
        canvas.paste(im, (x, top))
        draw.text((x + 10, 5), lab, fill="black", font=font)
        x += im.width + gap
    canvas.save(out, dpi=(200, 200))
    print("wrote", out.name, canvas.size)


side_by_side([OUT_FIG / "confusion_matrix.png", OUT_FIG / "roc_curve.png"], REP_FIG / "compact_cm_roc.png")
side_by_side([OUT_FIG / "shap_global_importance.png", OUT_FIG / "shap_summary_beeswarm.png"],
             REP_FIG / "compact_shap_global.png", height=1100)
side_by_side([OUT_FIG / "lime_case4_patient86.png", OUT_FIG / "shap_waterfall_case4_patient86.png"],
             REP_FIG / "compact_p86_lime_waterfall.png", height=1000)
side_by_side([REP_FIG / "ui_dashboard_window_overview.png", REP_FIG / "ui_whatif_p100_worst_area_500.png"],
             REP_FIG / "compact_ui_window_whatif.png", height=1100)
