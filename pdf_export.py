"""PDF Export file"""
from datetime import datetime
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
import pandas as pd
import matplotlib.pyplot as plt


# Functions for styling text.
def format_heading1(c: canvas, page_height: float, title: str) -> float:
    """Formats a given text into a predefined heading style."""
    c.setFont("Times-Bold", 24)
    x_title = 0.5 * inch
    y_title = page_height - (0.75 * inch)
    c.drawString(x_title, y_title, title)

    return y_title

def format_paragraph(c: canvas, page_width: float, y_element_above: float, indent: bool, text: str):
    """Formats a given text and formats it into a predefined paragraph style."""
    font_name = "Times-Roman"
    font_size = 14
    c.setFont(font_name, font_size)
    leading = font_size * 1.2

    left_margin = 0.5 * inch
    right_margin = 0.75 * inch
    usable_width = page_width - (left_margin + right_margin)

    lines = simpleSplit(text, font_name, font_size, usable_width)

    current_y = y_element_above - (0.5 * inch)

    if indent:
        for idx, line in enumerate(lines):
            if idx == 0:
                x_pos = left_margin + (0.4 * inch)
            else:
                x_pos = left_margin

            c.drawString(x_pos, current_y, line)
            current_y -= leading
    else:
        for line in lines:
            c.drawString(left_margin, current_y, line)
            current_y -= leading

    return current_y

# Functions for creating individual pages.
def create_title_page(c: canvas, date_of_creation: str):
    """Forms and creates the title/cover page of the pdf export."""
    page_width, page_height = LETTER

    title_text = "Vulnerability Scan Analysis Report"
    c.setFont("Times-Bold", 26)
    title_width = c.stringWidth(title_text, "Times-Bold", 26)
    x_title = (page_width - title_width) / 2
    y_title = page_height - (3.5 * inch)
    c.drawString(x_title, y_title, title_text)

    date_text = f"Date of Creation: {date_of_creation}"
    c.setFont("Times-Roman", 14)
    date_width = c.stringWidth(date_text, "Times-Roman", 14)
    x_date = (page_width - date_width) / 2
    y_date = y_title - (0.5 * inch)
    c.drawString(x_date, y_date, date_text)

    paragraph_lines = [
        "This document provides a comprehensive overview and analysis",
        "of vulnerabilities identified through multiple security scans.",
        "The information herein is intended for authorized personnel",
        "and must be handled in accordance with the organization’s",
        "data classification policies."
    ]
    c.setFont("Times-Roman", 12)

    y_text = y_date - (0.5 * inch)

    leading = 14
    for line in paragraph_lines:
        line_width = c.stringWidth(line, "Times-Roman", 12)
        x_line = (page_width - line_width) / 2
        c.drawString(x_line, y_text, line)
        y_text -= leading

def create_disclosure_page(c: canvas):
    """Creates the layout for the disclosure page."""
    page_width, page_height = LETTER

    y_disclosure_title = format_heading1(c, page_height, "Disclosure Statement")

    disclosure_paragraph = (
        "This document contains sensitive security-related data derived from multiple "
        "vulnerability assessments and should be handled with the utmost discretion. "
        "The information presented within this report includes detailed findings on "
        "software and system vulnerabilities, including their severity, potential "
        "exploitability, and overall impact on confidentiality, integrity, and availability. "
        "Unauthorized disclosure, distribution, or replication of this document may "
        "significantly increase the risk exposure of the affected systems, potentially "
        "enabling malicious actors to exploit known weaknesses before mitigation efforts "
        "can be completed. As such, access to this document should be strictly limited to "
        "authorized personnel with a legitimate need to review and act upon the findings "
        "contained herein. The data enclosed is intended solely for internal use in "
        "cybersecurity risk assessment and remediation planning. Any sharing of this report, "
        "in whole or in part, with external parties or unauthorized individuals must be "
        "expressly approved by the appropriate security governance team within the organization. "
        "Failure to adhere to proper handling and distribution protocols may not only compromise "
        "the security posture of the organization but could also result in "
        "regulatory or compliance "
        "violations. It is imperative that all recipients of this report follow established "
        "data protection guidelines, including encryption, secure storage, and controlled access, "
        "to prevent accidental or intentional exposure. If this document has been received in "
        "error or is found in an unsecured location, it must be immediately reported to the "
        "security operations team for proper disposal or retrieval."
    )

    format_paragraph(c, page_width, y_disclosure_title, True, disclosure_paragraph)

def create_overview_page(c: canvas, date_of_creation: str, ):
    """Creates the layout for the overview page."""
    page_width, page_height = LETTER

    y_overview_title = format_heading1(c, page_height, "Overview")

# Functions for creating the entire pdf export.
def create_full_report(output_pdf_path):
    """Combines all of the pages together and saves it as a pdf."""
    date_of_creation = datetime.now().strftime("%B %d, %Y")

    c = canvas.Canvas(output_pdf_path, pagesize=LETTER)

    create_title_page(c, date_of_creation)
    c.showPage()

    create_disclosure_page(c)
    c.showPage()

    create_overview_page(c, date_of_creation)
    c.showPage()

    c.save()
