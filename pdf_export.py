"""PDF Export file"""
from datetime import datetime
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
import pandas as pd
import matplotlib.pyplot as plt
from scan_class import SCAN
from scans_processing import (
    get_scan_names_str, return_total_scans_vulns,
    get_greatest_scan_name
)

#Functions for kev identificaiton.
def return_kev(scans: list[SCAN]) -> SCAN:
    """Returns a seperate kev scan obj and removes it from the list."""
    for i, scan in enumerate(scans):
        if scan.get_name().lower() == 'kev':
            return scans.pop(i)
    return None

#Functions for creating charts.
def create_vertical_bar_chart(
    scans_list: list[SCAN], scan_method: callable, y_axis: str, chart_title: str,
    bar_color: str, fig_width=5.0, fig_height=4.0
) -> io.BytesIO:
    """Creates a vertical bar chart using a scan method to retrieve values."""
    data = {"Scanner": [], chart_title: []}

    for scan in scans_list:
        data["Scanner"].append(scan.get_name())
        data[chart_title].append(scan_method(scan))

    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    df.plot(kind="bar", x="Scanner", y=chart_title, ax=ax, color=bar_color)

    ax.set_xlabel("Scanner")
    ax.set_ylabel(y_axis)
    ax.set_title(chart_title)

    plt.tight_layout()

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format="png", dpi=72)
    plt.close(fig)
    chart_buffer.seek(0)

    return chart_buffer

#Functions for positioning charts.
def draw_right_image(
    c: canvas, page_width: float, y_element_above: float, img_buffer: io.BytesIO
    ) -> float:
    """Moves the image to the right side of the page."""
    image_reader = ImageReader(img_buffer)

    image_width = page_width / 2
    image_height = page_width / 3

    x_left = (page_width - 0.5 * inch) - image_width
    y_bottom = y_element_above + (0.25 * inch) - image_height

    c.drawImage(image_reader, x_left, y_bottom, width=image_width, height=image_height)

    return y_bottom

# Functions for styling text.
def format_heading1(c: canvas, page_height: float, title: str) -> float:
    """Formats a given text into a predefined heading style."""
    c.setFont("Times-Bold", 24)
    x_title = 0.5 * inch
    y_title = page_height - (0.75 * inch)
    c.drawString(x_title, y_title, title)

    return y_title

def format_heading3(
    c: canvas, page_width: float, y_element_above: float, indent: bool, text: str
    ) -> float:
    """Formats a given text into a predefined heading3 style."""
    font_name = "Times-Bold"
    font_size = 16
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

    return current_y + (0.4 * inch)

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

def list_values(scans: list[SCAN], scan_method: callable) -> str:
    """Lists out each scan's name and the value returned by scan_method in a bullet point format."""
    bullet_points = []

    for scan in scans:
        value = scan_method(scan)
        bullet_points.append(f"• {scan.get_name()}: {value}")

    return "\n".join(bullet_points)

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

def create_overview_page(c: canvas, date_of_creation: str, scans_list: list[SCAN], kev_scan: SCAN):
    """Creates the overview page of the pdf export."""
    page_width, page_height = LETTER

    y_overview_title = format_heading1(c, page_height, "Overview")

    overview_paragraph = (
        "This page provides a high-level overview of the vulnerability assessments "
        f"conducted on {date_of_creation} using the following tools: "
        f"{get_scan_names_str(scans_list)} and with "
        "the inclusion of CVSS metrics and data from the National Vulnerability Database (NVD)."
        " The data analyzed includes: "
    )
    y_overview_paragraph = format_paragraph(
        c, page_width, y_overview_title, True, overview_paragraph
    )
    y_total_cve_title = format_heading3(
        c, page_width, y_overview_paragraph, False, "Total CVEs Parsed: "
    )
    y_total_cve_paragraph = format_paragraph(
        c, page_width, y_total_cve_title, False, list_values(scans_list, lambda s: s.return_total_vulns())
    )

    total_cves_barchart_buf = create_vertical_bar_chart(
        scans_list, lambda s: s.return_total_vulns(), "Total CVEs", "Total CVEs", "skyblue"
    )
    draw_right_image(c, page_width, y_total_cve_title, total_cves_barchart_buf)

    y_unique_cve_title = format_heading3(
        c, page_width, y_total_cve_paragraph - (1.6 * inch), False, "Unique CVEs Parsed: "
    )
    y_unique_cve_paragraph = format_paragraph(
        c, page_width, y_unique_cve_title, False, list_values(scans_list, lambda s: s.return_unique_vulns())
    )

    unique_cves_barchart_buf = create_vertical_bar_chart(
        scans_list, lambda s: s.return_unique_vulns(), "Unique CVEs", "Unique CVEs", "skyblue"
    )
    draw_right_image(c, page_width, y_unique_cve_title, unique_cves_barchart_buf)

    if kev_scan is not None:
        review_paragraph = (
            f"Overall, the scans collectively parsed "
            f"{return_total_scans_vulns(scans_list)} CVEs over an equal "
            f"and specified duration for each scan. The scan with the largest amount of "
            f"total CVEs (excluding KEV) was {get_greatest_scan_name(scans_list, lambda s: s.return_total_vulns())} "
            f"and the scan with the largest amount of unique CVEs (excluding KEV) was "
            f"{get_greatest_scan_name(scans_list, lambda s: s.return_unique_vulns())}. For reference, "
            f"{kev_scan.get_name()} contained a total of "
            f"{kev_scan.return_unique_vulns()} unique vulnerabilities."
        )
    else:
        review_paragraph = (
            f"Overall, the scans collectively parsed "
            f"{return_total_scans_vulns(scans_list)} CVEs over an equal "
            f"and specified duration for each scan. The scan with the largest amount of "
            f"total CVEs was {get_greatest_scan_name(scans_list, lambda s: s.return_total_vulns())} and "
            f"the scan with the largest amount of unique CVEs was "
            f"{get_greatest_scan_name(scans_list, lambda s: s.return_unique_vulns())}. "
        )
    format_paragraph(c, page_width, page_height - (8.5 * inch), True, review_paragraph)

###############################################################################FIX THIS and use SQL!!!!!
# def create_kev_comparison_page(c: canvas, scans_list):
#     page_width, page_height = LETTER

#     y_kev_title = format_heading1(c, page_height, "KEV Catalog Comparison")

#     overview_paragraph = (
#         "The Known Exploited Vulnerabilities (KEV) Catalog, maintained by the Cybersecurity and "
#         "Infrastructure Security Agency (CISA), is a curated list of vulnerabilities that have been "
#         "confirmed to be exploited in the wild. Comparing scan results against the KEV catalog helps "
#         "measure how well each scanner detects vulnerabilities with known real-world exploitation. "
#         "The following table shows the number of vulnerabilities detected by each scanner that are also listed in "
#         "the KEV catalog: "
#     )
#     y_overview_paragraph = format_paragraph(c, page_width, y_kev_title, True, overview_paragraph)

#     y_comparison_title = format_heading3(c, page_width, y_overview_paragraph, False, "CVEs in KEV: ")
#     y_comparison_paragraph = format_paragraph(c, page_width, y_comparison_title, False, list_values(scans_list, "kev_vulns"))

#     kev_barchart_buf = create_vertical_bar_chart(
#         scans_list, "kev_vulns", "CVEs in KEV", "CVEs in KEV", "lightcoral"
#     )
#     draw_right_image(c, page_width, y_comparison_title, kev_barchart_buf)

# Functions for creating the entire pdf export.
###############################################################################FIX THIS and use SQL!!!!!
def create_full_report(output_pdf_path, scans_list: list[SCAN]):
    """Combines all of the pages together and saves it as a pdf."""
    date_of_creation = datetime.now().strftime("%B %d, %Y")
    
    kev_scan = return_kev(scans_list)

    c = canvas.Canvas(output_pdf_path, pagesize=LETTER)

    create_title_page(c, date_of_creation)
    c.showPage()

    create_disclosure_page(c)
    c.showPage()

    create_overview_page(c, date_of_creation, scans_list, kev_scan)
    c.showPage()

    # create_kev_comparison_page(c, scans_list)
    # c.showPage()

    c.save()
