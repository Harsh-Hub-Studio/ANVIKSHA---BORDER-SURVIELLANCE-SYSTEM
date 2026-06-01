"""
generate_pdf.py
Generates a formatted PDF of all Anviksha project source code.
Run: python generate_pdf.py
Requires: pip install reportlab
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, PageBreak, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas

# ─── FILE LIST (in presentation order) ────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    # ── BACKEND ──
    ("BACKEND — Core Application",   None,                                                     None),
    ("main.py",                       "main.py",                                                "Python"),
    ("camera.py",                     "camera.py",                                              "Python"),
    ("detection.py",                  "detection.py",                                           "Python"),
    ("yolo.py",                       "yolo.py",                                                "Python"),
    ("risk.py",                       "risk.py",                                                "Python"),
    ("alerts.py",                     "alerts.py",                                              "Python"),

    # ── TRAINING ──
    ("BACKEND — Training & Dataset",  None,                                                     None),
    ("train_faces.py",                "train_faces.py",                                         "Python"),
    ("train_weapons.py",              "train_weapons.py",                                       "Python"),
    ("collect_dataset.py",            "collect_dataset.py",                                     "Python"),
    ("rename_dataset.py",             "rename_dataset.py",                                      "Python"),
    ("update_yolo.py",                "update_yolo.py",                                         "Python"),
    ("test_live.py",                  "test_live.py",                                           "Python"),

    # ── STARTUP ──
    ("STARTUP SCRIPT",                None,                                                     None),
    ("start_command_center.bat",      "start_command_center.bat",                               "Batch"),

    # ── FRONTEND ──
    ("FRONTEND — React Dashboard",    None,                                                     None),
    ("package.json",                  os.path.join("frontend", "package.json"),                 "JSON"),
    ("App.jsx",                       os.path.join("frontend", "src", "App.jsx"),               "JSX"),
    ("index.css",                     os.path.join("frontend", "src", "index.css"),             "CSS"),
    ("Homepage.jsx",                  os.path.join("frontend", "src", "pages", "Homepage.jsx"), "JSX"),
    ("Login.jsx",                     os.path.join("frontend", "src", "pages", "Login.jsx"),    "JSX"),
    ("Dashboard.jsx",                 os.path.join("frontend", "src", "pages", "Dashboard.jsx"),"JSX"),
]

OUTPUT_PDF = os.path.join(BASE, "Anviksha_Complete_Code.pdf")

# ─── COLOUR PALETTE ────────────────────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0d1117")   # very dark navy
PANEL     = colors.HexColor("#161b22")   # GitHub-dark panel
ACCENT    = colors.HexColor("#1f6feb")   # bright blue
GREEN     = colors.HexColor("#3fb950")
YELLOW    = colors.HexColor("#d29922")
TEXT_MAIN = colors.HexColor("#c9d1d9")
TEXT_DIM  = colors.HexColor("#8b949e")
WHITE     = colors.HexColor("#ffffff")
RED       = colors.HexColor("#f85149")

LANG_COLORS = {
    "Python": colors.HexColor("#3572A5"),
    "JSX":    colors.HexColor("#61dafb"),
    "CSS":    colors.HexColor("#563d7c"),
    "JSON":   colors.HexColor("#f59e0b"),
    "Batch":  colors.HexColor("#89e051"),
}


# ─── PAGE TEMPLATE WITH HEADER/FOOTER ─────────────────────────────────────────
class CodePDFCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        super().showPage()

    def save(self):
        num_pages = len(self.pages)
        for page_info in self.pages:
            self.__dict__.update(page_info)
            self._draw_page_deco(num_pages)
            super().showPage()
        super().save()

    def _draw_page_deco(self, total):
        w, h = A4
        # Top bar
        self.setFillColor(DARK_BG)
        self.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)
        self.setStrokeColor(ACCENT)
        self.setLineWidth(1)
        self.line(0, h - 22*mm, w, h - 22*mm)

        # Project name in header
        self.setFont("Helvetica-Bold", 9)
        self.setFillColor(ACCENT)
        self.drawString(14*mm, h - 13*mm, "ANVIKSHA")
        self.setFillColor(TEXT_DIM)
        self.setFont("Helvetica", 8)
        self.drawString(40*mm, h - 13*mm, "AI-Based Infiltration Risk Prediction & Surveillance System")

        # Page number right
        self.setFillColor(TEXT_DIM)
        self.setFont("Helvetica", 8)
        page_str = f"Page {self._pageNumber} / {total}"
        self.drawRightString(w - 14*mm, h - 13*mm, page_str)

        # Bottom bar
        self.setFillColor(DARK_BG)
        self.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        self.setStrokeColor(PANEL)
        self.setLineWidth(0.5)
        self.line(0, 12*mm, w, 12*mm)
        self.setFillColor(TEXT_DIM)
        self.setFont("Helvetica", 7)
        self.drawString(14*mm, 4*mm, "Confidential — For Project Guide Review Only")
        self.drawRightString(w - 14*mm, 4*mm, "Anviksha Sentinel v4.2.1")


# ─── BUILD PDF ────────────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=28*mm,
        bottomMargin=18*mm,
        title="Anviksha — Complete Source Code",
        author="Harsh Rathod",
        subject="AI-Based Infiltration Risk Prediction and Decision Support System",
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ProjectTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=WHITE,
        backColor=DARK_BG,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=32,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=ACCENT,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    meta_style = ParagraphStyle(
        "Meta",
        fontName="Helvetica",
        fontSize=9,
        textColor=TEXT_DIM,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    section_style = ParagraphStyle(
        "Section",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=ACCENT,
        backColor=PANEL,
        spaceAfter=4,
        spaceBefore=8,
        leftIndent=4,
        borderPadding=(4, 6, 4, 6),
    )
    file_title_style = ParagraphStyle(
        "FileTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=WHITE,
        backColor=DARK_BG,
        spaceAfter=2,
        spaceBefore=6,
        leftIndent=2,
        borderPadding=(3, 5, 3, 5),
    )
    code_style = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=7.2,
        textColor=TEXT_MAIN,
        backColor=DARK_BG,
        leftIndent=0,
        leading=10,
        spaceAfter=0,
        wordWrap="LTR",
    )

    story = []

    # ── COVER PAGE ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph("ANVIKSHA", title_style))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "AI-Based Infiltration Risk Prediction<br/>and Decision Support System",
        subtitle_style
    ))
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("COMPLETE SOURCE CODE", ParagraphStyle(
        "CoverSub", fontName="Helvetica-Bold", fontSize=13,
        textColor=YELLOW, alignment=TA_CENTER
    )))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("For Project Guide Review", meta_style))
    story.append(Spacer(1, 10*mm))

    # Table of contents data
    toc_data = [
        ["#", "File / Module", "Language", "Description"],
    ]
    descriptions = {
        "main.py":                   "Flask server, detection pipeline, API endpoints",
        "camera.py":                 "MJPEG streaming & auto-reconnect (Alg 5, 7)",
        "detection.py":              "Haar Cascade face + HSV ID card detection (Alg 1, 3)",
        "yolo.py":                   "YOLOv3 + YOLOv8 weapon inference (Alg 2)",
        "risk.py":                   "MCDA weighted risk scoring engine (Alg 4)",
        "alerts.py":                 "Socket.IO real-time alert push (Alg 6)",
        "train_faces.py":            "LBPH face recognizer — capture, augment, train, eval",
        "train_weapons.py":          "YOLOv8 weapon model training script",
        "collect_dataset.py":        "Dataset collection tool for faces & vehicles",
        "rename_dataset.py":         "Bulk rename utility for training images",
        "update_yolo.py":            "One-time migration script — adds weapon detection to yolo.py",
        "test_live.py":              "Live camera test — face + weapon detection",
        "start_command_center.bat":  "Batch launcher — starts Python API + React dashboard",
        "package.json":              "React project config & dependencies",
        "App.jsx":                   "Root React component — routing (Home → Login → Dashboard)",
        "index.css":                 "Global stylesheet",
        "Homepage.jsx":              "Landing page with feature showcase",
        "Login.jsx":                 "Animated authentication screen",
        "Dashboard.jsx":             "Live 8-camera surveillance command center",
    }
    file_num = 1
    for (label, rel_path, lang) in FILES:
        if rel_path is None:
            continue
        fname = os.path.basename(rel_path)
        toc_data.append([
            str(file_num),
            fname,
            lang or "",
            descriptions.get(fname, ""),
        ])
        file_num += 1

    toc_table = Table(
        toc_data,
        colWidths=[10*mm, 48*mm, 18*mm, None],
        repeatRows=1,
    )
    toc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  ACCENT),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("BACKGROUND",    (0, 1), (-1, -1), DARK_BG),
        ("TEXTCOLOR",     (0, 1), (-1, -1), TEXT_MAIN),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [DARK_BG, PANEL]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#30363d")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(Paragraph("TABLE OF CONTENTS", ParagraphStyle(
        "TOCHead", fontName="Helvetica-Bold", fontSize=10,
        textColor=GREEN, spaceAfter=4
    )))
    story.append(toc_table)
    story.append(PageBreak())

    # ── CODE PAGES ──────────────────────────────────────────────────────────
    file_num = 1
    for (label, rel_path, lang) in FILES:
        if rel_path is None:
            # Section header
            story.append(Spacer(1, 4*mm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=PANEL))
            story.append(Paragraph(f"▸  {label}", section_style))
            story.append(Spacer(1, 2*mm))
            continue

        full_path = os.path.join(BASE, rel_path)
        fname = os.path.basename(rel_path)

        if not os.path.exists(full_path):
            story.append(Paragraph(f"[FILE NOT FOUND: {rel_path}]", meta_style))
            continue

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            code_text = f.read()

        lines = code_text.splitlines()
        line_count = len(lines)

        # File header bar
        lang_color = LANG_COLORS.get(lang or "", ACCENT)
        header_data = [[
            Paragraph(f"<b>{file_num:02d}.</b>  {fname}", ParagraphStyle(
                "FH", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph(f"{lang}  •  {line_count} lines", ParagraphStyle(
                "FH2", fontName="Helvetica", fontSize=8, textColor=lang_color, alignment=1)),
        ]]
        header_table = Table(header_data, colWidths=["70%", "30%"])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -1), 1.5, lang_color),
        ]))
        story.append(header_table)

        # Code block — split into chunks for ReportLab
        MAX_CHARS = 105   # approx chars per line before wrap at 7.2pt Courier on A4

        def escape_code(line):
            line = line.replace("&", "&amp;")
            line = line.replace("<", "&lt;")
            line = line.replace(">", "&gt;")
            return line

        code_lines_escaped = []
        for i, line in enumerate(lines, 1):
            safe = escape_code(line)
            # Dim line numbers, normal code
            code_lines_escaped.append(
                f'<font color="#3d4451">{i:4d} </font>{safe}'
            )

        # Join into blocks of ~80 lines each (prevents huge single Paragraph)
        BLOCK = 80
        for start in range(0, len(code_lines_escaped), BLOCK):
            chunk = code_lines_escaped[start:start+BLOCK]
            block_text = "<br/>".join(chunk)
            story.append(Paragraph(block_text, code_style))

        story.append(Spacer(1, 4*mm))
        file_num += 1

    # ── FINAL PAGE ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 40*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("END OF SOURCE CODE DOCUMENT", ParagraphStyle(
        "End", fontName="Helvetica-Bold", fontSize=14,
        textColor=WHITE, alignment=TA_CENTER
    )))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Anviksha Sentinel — AI-Based Infiltration Risk Prediction and Decision Support System", ParagraphStyle(
        "EndSub", fontName="Helvetica", fontSize=9, textColor=TEXT_DIM, alignment=TA_CENTER
    )))

    # Build
    doc.build(story, canvasmaker=CodePDFCanvas)
    print(f"\nPDF generated successfully!")
    print(f"   File: {OUTPUT_PDF}")
    print(f"   Size: {os.path.getsize(OUTPUT_PDF) / 1024:.0f} KB")


if __name__ == "__main__":
    print("=" * 60)
    print("  Anviksha -- Generating Complete Source Code PDF")
    print("=" * 60)
    build_pdf()
