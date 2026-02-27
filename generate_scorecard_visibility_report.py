"""
Generate Consolidated Scorecard Visibility Report as PDF.
Top 55 accounts, organized by IFM. Accounts with multiple IFMs appear under each.
Requires: pip install reportlab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime


# Data: (Account, AD, IFMs, Jan notes, Feb notes)
# Accounts repeated under each IFM per user Option B
RAW_ENTRIES = [
    ("Deutsche Bank – NY", "Peggy Shum", ["CBRE"], "January SCR (held Feb 2/4): In Person – Score 5", "February SCR (scheduled 3/4): In Person"),
    ("Wells Fargo", "Colleen Doles", ["JLL"], "January SCR (held 2/6)", "February SCR: TBD (RFP cycle in progress)"),
    ("Citi Bank – San Antonio", "Berenday Escamilla", ["C&W"], "January SCR (held 2/4): Virtual – Score 5", "February SCR (3/4): Virtual"),
    ("USAA", "Berenday Escamilla", ["CBRE"], "January SCR (held 1/27): Virtual – Score 5", "February SCR (3/24): Virtual"),
    ("Charles Schwab", "Tiffany Purifoy", ["Direct"], "January SCR (held 2/5)", "February SCR: TBD"),
    ("Fidelity", "Tiffany Purifoy", ["CBRE"], "January SCR (held 2/6)", "February SCR: TBD"),
    ("State Farm", "Tiffany Purifoy", ["CBRE"], "January SCR (held 2/6)", "February SCR: TBD"),
    ("T. Rowe Price", "Tiffany Purifoy", ["JLL"], "January SCR (February meeting; brief due to transition)", "February SCR: TBD"),
    ("Geico", "Corey Wallace", ["CBRE"], "January SCR (held 2/11): Score 5", "February SCR: TBD"),
    ("Eli Lilly", "Chad Boulton", ["CBRE"], "January SCR (held 2/5–2/13): In Person – All locations scored 5", "February SCR (scheduled 3/5 + 1st week March sites): In Person"),
    ("Medtronic", "Giselle Langelier", ["Direct"], "January SCR (held 2/4–2/10): In Person – All 5's. Carlsbad = Quarterly cadence", "February SCR (3/5–3/6): In Person"),
    ("Bayer", "Isaac Calderon", ["Direct", "EMCOR", "JLL"], "January SCR (held 2/3–2/6): In Person – Scores 4–5. Cambridge = Quarterly", "February SCR (3/2–3/6): In Person"),
    ("Millipore Sigma", "Isaac Calderon", ["Direct"], "January SCR (held 2/4): Virtual – 4.5", "February SCR: TBD"),
    ("IQVIA", "Patrick Murtha", ["CBRE"], "January SCR (held 2/12): Virtual", "February SCR (3/12): Virtual"),
    ("Biogen", "Rafaed Ortiz", ["CBRE"], "January SCR (held 2/5): Virtual – Cambridge: 5.0, Pharma: 4.75, Bio: 4.25", "February SCR: To be scheduled (Virtual; within first 5 business days)"),
    ("Google", "Paul Rhodes", ["JLL"], "January SCR (February review): Bay: 4.75, America: 4.77", "February SCR: America 3/27 (Virtual); Bay: Monthly (In Person preferred). Bi-Annual SBR: Tentative 3/18"),
    ("Microsoft Puget Sound", "Taylor Wattenberg", ["CBRE"], "January SCR (held 2/5): In Person – Score 5", "February SCR (3/6): In Person"),
    ("NVIDIA", "Stuart Kelloff", ["CBRE"], "January SCR (delivered with QBR in Feb): Score 5", "February SCR (3/19): In Person"),
    ("Lockheed Martin", "Benjamin Ehrenberg", ["Direct", "EMCOR"], "January SCR (held 1/28–2/5): In Person", "February SCR (3/3–3/4): In Person"),
    ("Northrop Grumman", "Jennifer Segovia", ["JLL"], "January SCR (held 2/6): Phone", "February SCR (3/6 recurring): Monthly cadence"),
    ("General Dynamics", "Jennifer Segovia", ["Direct"], "January SCR (held 2/11): In Person", "February SCR (3/6 recurring): Monthly cadence"),
    ("GE Vernova Hitachi", "Logan Newman", ["JLL"], "January SCR (held 2/12)", "February SCR (3/5 or 3/12): In Person"),
    ("GE Aerospace", "Logan Newman", ["Direct"], "January SCR (held 2/13)", "February SCR (3/13): Virtual"),
    ("Amentum / GE Vernova", "Logan Newman", ["Amentum"], "January SCR (held 2/24)", "February SCR (3/10): Virtual"),
    ("GE Healthcare", "Kimberly Wittekind", ["Direct"], "January SCR (held 2/3–2/13): In Person", "February SCR (3/3): In Person"),
    ("Ball / Mars", "Aaron Simpson", ["CBRE"], "January SCR (held 2/9)", "February SCR (3/9): Virtual (QBR in person expected)"),
    ("Nike", "Jack Thornton", ["CBRE", "Direct"], "January SCR (February review): In Person – Score 5", "February SCR (Before 3/10): In Person"),
    ("Nestlé", "Kimberly Wittekind", ["Direct"], "January SCR (held 2/9–2/12): Virtual", "February SCR: Partially confirmed; some TBD"),
    ("P&G", "Nicholas Trenkamp", ["JLL"], "January SCR (held 2/6)", "February SCR: TBD"),
    ("Cigna", "Julie Bianchi", ["CBRE", "Direct"], "January SCR (held 2/5): Virtual – Score 4.88", "February SCR (3/5): Virtual"),
    ("Elevance", "Julie Bianchi", ["C&W", "Direct"], "January SCR (held 2/6): Virtual – Score 4.92", "February SCR (3/6): Virtual"),
    ("Cardinal Health", "Patrick Murtha", ["Direct", "JLL"], "January SCR (held 2/5): Virtual", "February SCR (3/5): Virtual"),
    ("McKesson", "Patrick Murtha", ["C&W"], "January SCR: Quarterly (last held 12/8)", "February SCR: Next review first week April"),
]

def build_ifm_sections():
    """Group entries by IFM. Each account appears under every IFM it belongs to."""
    ifm_order = ["CBRE", "Direct", "JLL", "C&W", "Amentum", "EMCOR"]
    sections = {ifm: [] for ifm in ifm_order}
    for account, ad, ifms, jan, feb in RAW_ENTRIES:
        for ifm in ifms:
            if ifm in sections:
                sections[ifm].append((account, ad, jan, feb))
    return sections

def create_pdf(output_path="Consolidated_Scorecard_Visibility_Report.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e3a5f"),
    )
    subtitle_style = ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#64748b"),
    )
    ifm_style = ParagraphStyle(
        name="IFMHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=22,
        spaceAfter=12,
        textColor=colors.HexColor("#1e40af"),
        borderPadding=4,
    )
    sub_style = ParagraphStyle(
        name="AccountName",
        parent=styles["Normal"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=3,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
    )
    body_style = ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=9,
        spaceAfter=2,
        leftIndent=14,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # Title block
    story.append(Paragraph("Consolidated Scorecard Visibility Report", title_style))
    story.append(Paragraph(
        f"Top 55 Accounts &middot; January Reviews held in February &middot; February Reviews held in March",
        subtitle_style
    ))
    story.append(Paragraph(
        f"Report Date: {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    story.append(Spacer(1, 0.25*inch))

    sections = build_ifm_sections()
    for ifm in ["CBRE", "Direct", "JLL", "C&W", "Amentum", "EMCOR"]:
        entries = sections.get(ifm, [])
        if not entries:
            continue
        story.append(Paragraph(f"IFM: {ifm}", ifm_style))
        for account, ad, jan, feb in entries:
            story.append(Paragraph(f"{account}", sub_style))
            story.append(Paragraph(f"<b>AD:</b> {ad}", body_style))
            story.append(Paragraph(f"<b>January SCR:</b> {jan}", body_style))
            story.append(Paragraph(f"<b>February SCR:</b> {feb}", body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"SUCCESS: PDF saved to {output_path}")

if __name__ == "__main__":
    create_pdf()
