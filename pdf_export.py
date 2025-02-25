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

    y_text = y_date - (4.5 * inch)

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

def create_overview_page(c: canvas, date_of_creation: str, scans_list: list):
    """Creates the overview page of the pdf export."""
    page_width, page_height = LETTER

    y_overview_title = format_heading1(c, page_height, "Overview")

    scan_name_string = ""
    scan_total_cve_string = ""
    scan_unique_cve_string = ""
    total_cves_collected = 0

    # Initialize counters for greatest totals.
    greatest_total_cve = 0
    greatest_total_cve_name = ""
    greatest_unique_cve = 0
    greatest_unique_cve_name = ""

    for scan in scans_list:
        # Concatenate scan names.
        scan_name_string += scan.Get_Name() + ", "

        # Get the numbers for this scan.
        total_cves = scan.Return_Total_CVE_ID_List_Length()
        unique_cves = scan.Return_CVE_Object_List_Length()

        # Build the strings for printing each scan's results.
        scan_total_cve_string += f"• {scan.Get_Name()}: {total_cves}\n"
        scan_unique_cve_string += f"• {scan.Get_Name()}: {unique_cves}\n"

        # Add to the overall total.
        total_cves_collected += total_cves

        # Check if this scan has the greatest total CVEs so far.
        if total_cves > greatest_total_cve:
            greatest_total_cve = total_cves
            greatest_total_cve_name = scan.Get_Name()

        # Check if this scan has the greatest unique CVEs so far.
        if unique_cves > greatest_unique_cve:
            greatest_unique_cve = unique_cves
            greatest_unique_cve_name = scan.Get_Name()

    # Adds KEV data to the strings.
    scan_total_cve_string += f"• {kev_scan.Get_Name()}: {kev_scan.Return_Total_CVE_ID_List_Length()}"
    scan_unique_cve_string += f"• {kev_scan.Get_Name()}: {kev_scan.Return_CVE_Object_List_Length()}"

    overview_paragraph = (
        "This page provides a high-level overview of the vulnerability assessment "
        f"conducted on {date_of_creation} using the following tools: {scan_name_string}and with "
        f"the inclusion of CVSS metrics and data from the National Vulnerability Database (NVD)."
        " The data analyzed includes: "
    )
    y_overview_paragraph = format_paragraph(c, page_width, y_overview_title, True, overview_paragraph)

    y_total_cve_title = format_paragraph(c, page_width, y_overview_paragraph, False, "Total CVEs Parsed: ")
    y_total_cve_paragraph = format_paragraph(c, page_width, y_total_cve_title, False, scan_total_cve_string)

    bar_chart_width = 4
    bar_chart_height = 3
    bar_chart_buffer = Create_Vertical_Bar_Chart_Total_CVES(scans_object_list, kev_scan, bar_chart_width, bar_chart_height)
    Draw_Right_Image(c, page_width, y_total_cve_title, bar_chart_width, bar_chart_height, bar_chart_buffer)

    y_unique_cve_title = Format_Heading3(c, page_width, y_total_cve_paragraph - (1.6 * inch), False,
                                         "Unique CVEs Parsed: ")
    y_unique_cve_paragraph = Format_Paragraph(c, page_width, y_unique_cve_title, False, scan_unique_cve_string)

    bar_chart_buffer = Create_Vertical_Bar_Chart_Unique_CVES(scans_object_list, kev_scan, bar_chart_width, bar_chart_height)
    Draw_Right_Image(c, page_width, y_unique_cve_title, bar_chart_width, bar_chart_height, bar_chart_buffer)

    review_paragraph = (
        f"Overall, the scans collectively parsed {total_cves_collected} CVEs over an equal and specified duration for each scan. "
        f"The scan with the largest amount of total CVEs was {greatest_total_cve_name} and the scan with the largest amount of "
        f"unique CVEs was {greatest_unique_cve_name}. For reference, {kev_scan.Get_Name()} contained a total of {kev_scan.Return_Total_CVE_ID_List_Length()} "
        f"which were all unique."
    )
    y_review_paragraph = format_paragraph(c, page_width, y_unique_cve_paragraph - (1.6 * inch), True, review_paragraph)

# Functions for creating the entire pdf export.
def create_full_report(output_pdf_path):
    """Combines all of the pages together and saves it as a pdf."""
    date_of_creation = datetime.now().strftime("%B %d, %Y")

    c = canvas.Canvas(output_pdf_path, pagesize=LETTER)

    create_title_page(c, date_of_creation)
    c.showPage()

    create_disclosure_page(c)
    c.showPage()

    c.save()
