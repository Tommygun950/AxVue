"""PDF Export file"""
from datetime import datetime
import math
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
    get_greatest_scan_name, call_scan_by_name,
    return_relation_percentage, get_scan_values,
)

#Functions for kev identificaiton.
def return_kev(
    scans: list[SCAN]
) -> SCAN:
    """Returns a seperate kev scan obj and removes it from the list."""
    for i, scan in enumerate(scans):
        if scan.get_name().lower() == 'kev':
            return scans.pop(i)
    return None

#Functions for creating charts.
def create_vertical_bar_chart(
    scans_list: list[SCAN], scan_method: callable,
    y_axis: str, chart_title: str, bar_color: str,
    kev_scan: SCAN = None, fig_width=5.0, fig_height=4.0
) -> io.BytesIO:
    """Creates a vertical bar chart using a scan list."""
    data = {"Scanner": [], chart_title: []}

    for scan in scans_list:
        data["Scanner"].append(scan.get_name())
        data[chart_title].append(scan_method(scan))

    if kev_scan is not None:
        data["Scanner"].append(kev_scan.get_name())
        data[chart_title].append(scan_method(kev_scan))

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

def create_pie_chart(
    scan: SCAN, labels: list[str], values: list[float],
    chart_subject: str, fig_width=5.0, fig_height=4.0
) -> io.BytesIO:
    """Creates a pie chart using a scan object with larger labels."""
    chart_title = f"{chart_subject} ({scan.get_name()})"
    predefined_colors = [
        "#FF4C4C", "#FFD54F", "#FFA726", "#66BB6A", "#42A5F5", "#5C6BC0", "#AB47BC",
        "#FF6F61", "#FFB74D", "#FFEB3B", "#81C784", "#64B5F6", "#7986CB", "#BA68C8",
        "#FF8A80", "#FF9800", "#FFF59D", "#A5D6A7", "#90CAF9", "#9FA8DA", "#CE93D8"
    ]
    colors = [predefined_colors[i % len(predefined_colors)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.pie(
        values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 14}
    )
    ax.set_title(chart_title, fontsize=16)
    plt.tight_layout()

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format="png", dpi=72)
    plt.close(fig)
    chart_buffer.seek(0)

    return chart_buffer

#Functions for positioning charts.
def draw_right_image(
    c: canvas, page_width: float, y_element_above: float,
    img_buffer: io.BytesIO
    ) -> float:
    """Moves the image to the right side of the page."""
    image_reader = ImageReader(img_buffer)

    image_width = page_width / 2
    image_height = page_width / 3

    x_left = (page_width - 0.5 * inch) - image_width
    y_bottom = y_element_above + (0.25 * inch) - image_height

    c.drawImage(image_reader, x_left, y_bottom, width=image_width, height=image_height)

    return y_bottom

def distribute_images(
    c: canvas, page_width: float, page_height: float,
    page_height_percentage: float, y_element_above: float,
    img_buffers: list[io.BytesIO]
) -> float:
    """Distributes multiple charts evenly on the pdf page."""
    n = len(img_buffers)
    if n == 0:
        return y_element_above
    vertical_spacing = 0.25 * inch
    available_width = 0.95 * page_width
    left_margin = (page_width - available_width) / 2
    max_total_image_height = page_height_percentage * page_height
    best_size = 0
    best_images_per_row = n
    for rows in range(1, n + 1):
        images_per_row = math.ceil(n / rows)
        h_max = available_width / images_per_row
        v_max = (max_total_image_height - (rows - 1) * vertical_spacing) / rows
        size = min(h_max, v_max)
        if size > best_size:
            best_size = size
            best_images_per_row = images_per_row
    current_y = y_element_above - 0.5 * inch
    image_size = best_size
    rows_list = []
    for i in range(0, n, best_images_per_row):
        rows_list.append(img_buffers[i:i + best_images_per_row])
    for row in rows_list:
        num_images_this_row = len(row)
        row_total_width = num_images_this_row * image_size
        start_x = left_margin + (available_width - row_total_width) / 2
        for j, buf in enumerate(row):
            x = start_x + j * image_size
            c.drawImage(ImageReader(buf), x, current_y - image_size,
                        width=image_size, height=image_size)
        current_y -= (image_size + vertical_spacing)
    return current_y

# Functions for styling text.
def format_title(
    c: canvas, title: str, page_width: float,
    page_height: float
) -> float:
    """Formats the title of the document on a page."""
    c.setFont("Times-Bold", 26)
    title_width = c.stringWidth(title, "Times-Bold", 26)
    x_title = (page_width - title_width) / 2
    y_title = page_height - (3.5 * inch)
    c.drawString(x_title, y_title, title)

    return y_title

def format_heading1(
    c: canvas, page_height: float, title: str
) -> float:
    """Formats a given text into a predefined heading style."""
    c.setFont("Times-Bold", 24)
    x_title = 0.5 * inch
    y_title = page_height - (0.75 * inch)
    c.drawString(x_title, y_title, title)

    return y_title

def format_heading3(
    c: canvas, page_width: float, y_element_above: float,
    indent: bool, text: str
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

def format_paragraph(
    c: canvas, page_width: float, y_element_above: float,
    indent: bool, text: str
):
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

def format_centered_paragraph(
    c: canvas, paragraph: list[str], page_width: float,
    y_element_above: float
) -> float:
    """Given a paragraph of text, it will center it on the page in paragraph style."""
    c.setFont("Times-Roman", 12)

    y_paragraph = y_element_above - (4.5 * inch)

    leading = 14
    for line in paragraph:
        line_width = c.stringWidth(line, "Times-Roman", 12)
        x_line = (page_width - line_width) / 2
        c.drawString(x_line, y_paragraph, line)
        y_paragraph -= leading

    return y_paragraph

def list_values(
    scans: list[SCAN], scan_values: list
) -> str:
    """Lists out each scan's name and their values in a bullet point format."""
    bullet_points = []
    for i, scan in enumerate(scans):
        bullet_points.append(f"• {scan.get_name()}: {scan_values[i]}")

    return "\n".join(bullet_points)

def format_date_text(
    c: canvas, date_of_creation: str, page_width: float,
    y_element_above: float
) -> float:
    """Given the date of creating, it will place the text in the correct space."""
    date_text = f"Date of Creation: {date_of_creation}"
    c.setFont("Times-Roman", 14)
    date_width = c.stringWidth(date_text, "Times-Roman", 14)
    x_date = (page_width - date_width) / 2
    y_date = y_element_above - (0.5 * inch)
    c.drawString(x_date, y_date, date_text)

    return y_date

#Functions for creating individual pages.
def create_title_page(c: canvas, date_of_creation: str):
    """
    Creates the title page of the pdf export.

    Expected page output: 
    1) Title
    2) Date Created
    3) Document Overview
    """
    ### 0. NESTED FUNCTIONS ###

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS###

    ### 3. TEXT DEFINITIONS (titles, headings, paragraphs, text) ###
    document_title = "Vulnerability Scan Analysis Report"

    overview_paragraph = [
        "This document provides a comprehensive overview and analysis",
        "of vulnerabilities identified through multiple security scans.",
        "The information herein is intended for authorized personnel",
        "and must be handled in accordance with the organization’s",
        "data classification policies."
    ]

    ### 4. CHART GENERATION (creating visual assets) ###

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    y_title = format_title(c, document_title, page_width, page_height)

    y_date = format_date_text(c, date_of_creation, page_width, y_title)

    format_centered_paragraph(c, overview_paragraph, page_width, y_date)

def create_disclosure_page(c: canvas):
    """
    Creates the layout for the disclosure page.
    
    Expected page output:
    1) Disclosure Header
    2) Disclosure statement/paragraph
    """
    ### 0. NESTED FUNCTIONS ###

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS###

    ### 3. TEXT DEFINITIONS (titles, headings, paragraph, text) ###
    document_title = "Disclosure Statement"

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

    ### 4. CHART GENERATION (creating visual assets) ###

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    #1. Disclosure Header
    y_disclosure_title = format_heading1(c, page_height, document_title)

    #2. Disclosure statement/paragraph
    format_paragraph(c, page_width, y_disclosure_title, True, disclosure_paragraph)

def create_overview_page(c: canvas, date_of_creation: str, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the overview page of the pdf export.

    Expected page output:
    1) Overview Header
    2) Intro Paragraph
    3) List of Total CVEs Parsed (with bar chart)
    4) List of Unique CVEs Parsed (with bar chart)    
    5) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_review_paragraph(
        total_parsed_vulns: int, kev_unique_vulns: int, greatest_total_scan_name: str,
        greatest_unique_scan_name: str
    ) -> str:
        """Creates the review paragraph based off kev existance."""
        if kev_scan is not None:
            review_paragraph = (
                f"Overall, the scans collectively parsed {total_parsed_vulns} CVEs over a "
                f"specified duration for each scan. The scan with the largest amount of "
                f"total CVEs (excluding KEV) was {greatest_total_scan_name}, and the scan "
                f"with the largest amount of unique CVEs (excluding KEV) was "
                f"{greatest_unique_scan_name}. For reference, the KEV Catalog contained a "
                f"a total of {kev_unique_vulns} unique vulnerabilities."
            )
        else:
            review_paragraph = (
                f"Overall, the scans collectively parsed {total_parsed_vulns} CVEs over a "
                f"specified duration for each scan. The scan with the largest amount of "
                f"total CVEs was {greatest_total_scan_name}, and the scan with the largest "
                f"amount of unique CVEs was {greatest_unique_scan_name}."
            )

        return review_paragraph

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS###
    scans_total_vulns = get_scan_values(scans, lambda s: s.return_total_vulns())
    scans_unique_vulns = get_scan_values(scans, lambda s: s.return_unique_vulns())

    total_parsed_vulns = return_total_scans_vulns(scans)
    kev_unique_vulns = kev_scan.return_unique_vulns()
    greatest_total_scan_name = get_greatest_scan_name(scans, lambda s: s.return_total_vulns())
    greatest_unique_scan_name = get_greatest_scan_name(scans, lambda s: s.return_unique_vulns())

    ### 3. TEXT DEFINITIONS (titles, headings, paragraph, text) ###
    document_title = "Overview"

    scan_names_list = get_scan_names_str(scans)
    intro_paragraph = (
        f"This page provides a high-level overview of the vulnerability assessments "
        f"conducted on {date_of_creation} using the following tools: "
        f"{scan_names_list} and with "
        f"the inclusion of CVSS metrics and data from the National Vulnerability Database (NVD)."
        f" The data analyzed includes: "
    )

    total_cve_title = "Total CVEs Parsed: "
    total_cve_paragraph = list_values(scans, scans_total_vulns)

    unique_cve_title = "Unique CVEs Parsed: "
    unique_cve_paragraph = list_values(scans, scans_unique_vulns)

    review_paragraph = create_review_paragraph(
        total_parsed_vulns, kev_unique_vulns,
        greatest_total_scan_name, greatest_unique_scan_name
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    total_cves_barchart_buf = create_vertical_bar_chart(
        scans, lambda s: s.return_total_vulns(),
        "Total CVEs", "Total CVEs", "skyblue", kev_scan
    )

    unique_cves_barchart_buf = create_vertical_bar_chart(
        scans, lambda s: s.return_unique_vulns(),
        "Unique CVEs", "Unique CVEs", "skyblue"
    )

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Overview Header
    y_overview_title = format_heading1(c, page_height, document_title)

    # 2. Intro Paragraph
    y_intro_paragraph = format_paragraph(
        c, page_width, y_overview_title, True, intro_paragraph
    )

    # 3. List of Total CVEs Parsed (with bar chart)
    y_total_cve_title = format_heading3(
        c, page_width, y_intro_paragraph, False, total_cve_title
    )
    y_total_cve_paragraph = format_paragraph(
        c, page_width, y_total_cve_title,
        False, total_cve_paragraph
    )
    draw_right_image(c, page_width, y_total_cve_title, total_cves_barchart_buf)

    # 4. List of Unique CVEs Parsed (with bar chart)
    y_unique_cve_title = format_heading3(
        c, page_width, y_total_cve_paragraph - (1.6 * inch), False, unique_cve_title
    )
    format_paragraph(
        c, page_width, y_unique_cve_title,
        False, unique_cve_paragraph
    )
    draw_right_image(c, page_width, y_unique_cve_title, unique_cves_barchart_buf)

    # 5. Review paragraph (data explination)
    format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_kev_comparison_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the KEV comparison page for the PDF export.
    
    Expected page output:
    1) KEV Comparison Header
    2) Intro Paragraph
    3) List of CVEs in KEV
    4) List of disposition pie charts
    5) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_kev_piechart_buffers(
        scans: list[SCAN]
    ) -> list[io.BytesIO]:
        """Given a list of scans, returns a list of kev disposition pie chart buffers."""
        piecharts = []

        labels = ["In KEV", "Not in KEV"]
        for scan in scans:
            in_kev = scan.return_kev_intersection(kev_scan)
            not_in_kev = scan.return_unique_vulns() - in_kev
            values = [in_kev, not_in_kev]

            piechart_buff = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buff)

        return piecharts

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS###
    scans_kev_intersection = get_scan_values(
        scans, lambda s: s.return_kev_intersection(kev_scan)
    )

    greatest_scan_name = get_greatest_scan_name(
        scans, lambda s: s.return_kev_intersection(kev_scan)
    )
    greatest_scan = call_scan_by_name(
        scans, greatest_scan_name
    )
    greatest_scan_vuln_overlap = greatest_scan.return_kev_intersection(kev_scan)
    greatest_scan_percentage = return_relation_percentage(
        lambda: greatest_scan.return_kev_intersection(kev_scan),
        greatest_scan.return_unique_vulns()
    )
    greatest_scan_intersection = greatest_scan.return_unique_vulns()

    kev_unique_vuln_ct = kev_scan.return_unique_vulns()

    ### 3. TEXT DEFINITIONS (titles, headings, paragraph, text) ###
    document_title = "KEV Catalog Comparison"

    intro_paragraph = (
        "The Known Exploited Vulnerabilities (KEV) Catalog, maintained by the Cybersecurity and "
        "Infrastructure Security Agency (CISA), is a curated list of vulnerabilities that have "
        "been confirmed to be exploited in the wild. Comparing scan results against the KEV "
        "catalog helpsmeasure how well each scanner detects vulnerabilities with known real-world "
        "exploitation. The following table shows the number of vulnerabilities detected by each "
        "scanner that are also listed in the KEV catalog: "
    )

    cves_in_kev_title = "CVEs in KEV: "
    cves_in_kev_paragraph = list_values(scans, scans_kev_intersection)

    review_paragraph = (
        f"In this KEV Catalog comparison, the scan that stood out was "
        f"{greatest_scan_name}, which identified "
        f"{greatest_scan_vuln_overlap} vulnerabilities listed in the KEV Catalog — "
        f"representing approximately {greatest_scan_percentage}% of its total "
        f"{greatest_scan_intersection} reported CVEs. By comparison, the other "
        f"scanners recorded lower KEV overlaps, highlighting differences in detection "
        f"capabilities among the tools. Overall, with the KEV Catalog containing "
        f"{kev_unique_vuln_ct} unique vulnerabilities. These results underscore the importance "
        f"of prioritizing vulnerabilities that have been actively exploited in the wild. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    kev_barchart_buf = create_vertical_bar_chart(
        scans, lambda s: s.return_kev_intersection(kev_scan),
        "CVEs in KEV", "CVEs in KEV", "plum"
    )

    piechart_buffers = create_kev_piechart_buffers(scans)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. KEV Comparison Header
    y_kev_title = format_heading1(c, page_height, document_title)

    #2. Intro Paragraph
    y_overview_paragraph = format_paragraph(c, page_width, y_kev_title, True, intro_paragraph)

    #3. List of CVEs in KEV
    y_comparison_title = format_heading3(
        c, page_width, y_overview_paragraph, False, cves_in_kev_title
    )
    format_paragraph(
        c, page_width, y_comparison_title, False,
        cves_in_kev_paragraph
    )
    y_kev_barchart = draw_right_image(c, page_width, y_comparison_title, kev_barchart_buf)

    #4. List of disposition pie charts
    distribute_images(
        c, page_width, page_height, 0.26,
        y_kev_barchart, piechart_buffers
    )

    #5. Review paragraph (data explination)
    format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

#Functions for creating the full report.
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

    create_kev_comparison_page(c, scans_list, kev_scan)
    c.showPage()

    c.save()
