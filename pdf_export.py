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

    total = sum(values)
    if total == 0:
        # If no data, display a single wedge indicating no data.
        values = [1]
        labels = ["No Data"]
        colors = ["#d3d3d3"]
        autopct = None
    else:
        autopct = '%1.1f%%'
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.pie(
        values, labels=labels, colors=colors, autopct=autopct, startangle=90,
        textprops={'fontsize': 14}
    )
    ax.set_title(chart_title, fontsize=16)
    plt.tight_layout()

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format="png", dpi=72)
    plt.close(fig)
    chart_buffer.seek(0)
    
    return chart_buffer

def create_scans_table(
    scans: list[SCAN], labels: list[str], values: list[list],
    kev_scan: SCAN = None, fig_width=12.0, fig_height=3.0
) -> io.BytesIO:
    """Given a list of scans, labels, and values, create a table of all scan data."""
    table_data = []
    if kev_scan is not None and len(values) == len(scans) + 1:
        for scan, row in zip(scans, values[:-1]):
            table_data.append([scan.get_name()] + row)
        table_data.append([kev_scan.get_name()] + values[-1])
    else:
        for scan, row in zip(scans, values):
            table_data.append([scan.get_name()] + row)
        if kev_scan is not None:
            placeholder_count = len(labels) - 1 if "Scanner" in labels[0] else len(labels)
            kev_row = [kev_scan.get_name()] + ["-" for _ in range(placeholder_count)]
            table_data.append(kev_row)

    if labels and "Scanner" not in labels[0]:
        col_labels = ["Scanner"] + labels
    else:
        col_labels = labels

    n_cols = len(col_labels)
    desired_col_width = 2.0 
    col_widths = [desired_col_width] * n_cols

    adjusted_fig_width = max(fig_width, desired_col_width * n_cols)

    fig, ax = plt.subplots(figsize=(adjusted_fig_width, fig_height))
    ax.axis('off')

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        colWidths=col_widths,
        bbox=[0, 0, 1, 1]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(14)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')

    table.scale(1, 1.0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

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

def draw_centered_image(
    c: canvas, page_width: float, page_height: float,
    page_height_percentage: float, y_element_above: float,
    img_buffer: list[io.BytesIO]
) -> float:
    """Given an image buffer and the width & height percentage the image buffer can take up,
    display it centered on the PDF and return the bottom y value of the drawn image.
    
    If a list is provided, the first image buffer is used.
    """
    if isinstance(img_buffer, list):
        image_buf = img_buffer[0]
    else:
        image_buf = img_buffer

    image_reader = ImageReader(image_buf)
    
    orig_width, orig_height = image_reader.getSize()
    
    available_height = page_height_percentage * page_height
    
    scale_factor = available_height / orig_height
    scaled_width = orig_width * scale_factor
    scaled_height = orig_height * scale_factor

    if scaled_width > page_width:
        scale_factor = page_width / orig_width
        scaled_width = orig_width * scale_factor
        scaled_height = orig_height * scale_factor
    
    x = (page_width - scaled_width) / 2
    y = y_element_above - scaled_height
    
    c.drawImage(image_reader, x, y, width=scaled_width, height=scaled_height)
    
    return y

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
    5) Review paragraph (data explanation)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_review_paragraph(
        total_parsed_vulns: int, kev_unique_vulns: int, 
        greatest_total_scan_name: str, greatest_unique_scan_name: str
    ) -> str:
        """Creates the review paragraph based on KEV existence."""
        if kev_scan is not None:
            review_paragraph = (
                f"Overall, the scans collectively parsed {total_parsed_vulns} CVEs over a specified duration for each scan. "
                f"The scan with the largest amount of total CVEs (excluding KEV) was {greatest_total_scan_name}, "
                f"and the scan with the largest amount of unique CVEs (excluding KEV) was {greatest_unique_scan_name}. "
                f"For reference, the KEV Catalog contained a total of {kev_unique_vulns} unique vulnerabilities."
            )
        else:
            review_paragraph = (
                f"Overall, the scans collectively parsed {total_parsed_vulns} CVEs over a specified duration for each scan. "
                f"The scan with the largest amount of total CVEs was {greatest_total_scan_name}, "
                f"and the scan with the largest amount of unique CVEs was {greatest_unique_scan_name}."
            )
        return review_paragraph

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    all_scans = scans[:]
    if kev_scan is not None:
        all_scans.append(kev_scan)

    scans_total_vulns = get_scan_values(all_scans, lambda s: s.return_total_vulns())
    scans_unique_vulns = get_scan_values(all_scans, lambda s: s.return_unique_vulns())
    total_parsed_vulns = return_total_scans_vulns(scans)

    if kev_scan is not None:
        kev_unique_vulns = kev_scan.return_unique_vulns()
    else:
        kev_unique_vulns = 0

    greatest_total_scan_name = get_greatest_scan_name(scans, lambda s: s.return_total_vulns())
    greatest_unique_scan_name = get_greatest_scan_name(scans, lambda s: s.return_unique_vulns())

    ### 3. TEXT DEFINITIONS (titles, headings, paragraph, text) ###
    document_title = "Overview"
    scan_names_list = get_scan_names_str(scans)
    intro_paragraph = (
        f"This page provides a high-level overview of the vulnerability assessments conducted on {date_of_creation} "
        f"using the following tools: {scan_names_list} and with the inclusion of CVSS metrics and data from the "
        f"National Vulnerability Database (NVD). The data analyzed includes: "
    )
    total_cve_title = "Total CVEs Parsed: "
    total_cve_paragraph = list_values(all_scans, scans_total_vulns)
    unique_cve_title = "Unique CVEs Parsed: "
    unique_cve_paragraph = list_values(scans, scans_unique_vulns)
    review_paragraph = create_review_paragraph(total_parsed_vulns, kev_unique_vulns,
                                               greatest_total_scan_name, greatest_unique_scan_name)

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
    y_intro_paragraph = format_paragraph(c, page_width, y_overview_title, True, intro_paragraph)
    
    # 3. List of Total CVEs Parsed (with bar chart)
    y_total_cve_title = format_heading3(c, page_width, y_intro_paragraph, False, total_cve_title)
    y_total_cve_paragraph = format_paragraph(c, page_width, y_total_cve_title, False, total_cve_paragraph)
    draw_right_image(c, page_width, y_total_cve_title, total_cves_barchart_buf)

    # 4. List of Unique CVEs Parsed (with bar chart)
    y_unique_cve_title = format_heading3(c, page_width, y_total_cve_paragraph - (1.6 * inch), False, unique_cve_title)
    format_paragraph(c, page_width, y_unique_cve_title, False, unique_cve_paragraph)
    draw_right_image(c, page_width, y_unique_cve_title, unique_cves_barchart_buf)

    # 5. Review Paragraph (data explination)
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

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
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
        lambda: greatest_scan.return_unique_vulns()
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

def create_severity_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Severity Disposition page for the PDF export.

    Expected page output:
    1) Severity Disposition Header
    2) Introduction paragraph
    3) Table of scanners to severity count
    4) Pie charts explination
    5) List of disposition pie charts
    6) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_severity_piechart_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, returns a list of severity disposition pie chart buffers."""
        piecharts = []
        labels = ["Critical", "High", "Medium", "Low"]
        for scan in scans:
            critical_ct = scan.return_severity("critical")
            high_ct = scan.return_severity("high")
            medium_ct = scan.return_severity("medium")
            low_ct = scan.return_severity("low")

            values = [critical_ct, high_ct, medium_ct, low_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            critical_ct = kev_scan.return_severity("critical")
            high_ct = kev_scan.return_severity("high")
            medium_ct = kev_scan.return_severity("medium")
            low_ct = kev_scan.return_severity("low")

            values = [critical_ct, high_ct, medium_ct, low_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None) -> list[list[int]]:
        """Given a list of scans, return the table values for each scan for severity."""
        scans_values = []

        for scan in scans:
            critical_val = scan.return_severity("critical")
            high_val = scan.return_severity("high")
            medium_val = scan.return_severity("medium")
            low_val = scan.return_severity("low")

            values = [critical_val, high_val, medium_val, low_val]
            scans_values.append(values)

        if kev_scan is not None:
            critical_val = kev_scan.return_severity("critical")
            high_val = kev_scan.return_severity("high")
            medium_val = kev_scan.return_severity("medium")
            low_val = kev_scan.return_severity("low")
            values = [critical_val, high_val, medium_val, low_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_crit_ct_scan_name = get_greatest_scan_name(scans, lambda s: s.return_severity("critical"))
    greatest_crit_ct_scan = call_scan_by_name(scans, greatest_crit_ct_scan_name)
    greatest_crit_ct_scan_ct = greatest_crit_ct_scan.return_severity("critical")

    severity_table_values = create_table_values(scans, kev_scan)

    greatest_crit_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_severity_percentage("critical"))
    greatest_crit_perc_scan = call_scan_by_name(scans, greatest_crit_perc_scan_name)
    greatest_crit_perc_scan_perc = greatest_crit_perc_scan.return_severity_percentage("critical")

    ### 3. TEXT DEFINITIONS (titles, headings, paragraph, text) ###
    document_title = "Severity Disposition"

    intro_paragraph = (
        "This page presents a comprehensive analysis of the severity disposition across all "
        "scans. The data is categorized into critical, high, medium, and low vulnerabilities. "
        "Understanding the distribution of severity levels is important in understanding the "
        "quality of scan data. "
    )

    severity_table_labels = ["Scanner", "Critical", "High", "Medium", "Low"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of severity throughout each scan "
        "and their relations to the overall unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest critical count (excluding KEV) was {greatest_crit_ct_scan_name}, "
        f"with a count of {greatest_crit_ct_scan_ct} critical vulnerabilities. "
        f"However, the scan with the highest critical disposition (excluding KEV) was {greatest_crit_perc_scan_name} "
        f"which has a percentage of {greatest_crit_perc_scan_perc}% of its vulnerabilities being "
        f"regarded as critical. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest critical count was {greatest_crit_ct_scan_name}, "
        f"with a count of {greatest_crit_ct_scan_ct} critical vulnerabilities. "
        f"However, the scan with the highest critical disposition was {greatest_crit_perc_scan_name} "
        f"which has a percentage of {greatest_crit_perc_scan_perc}% of its vulnerabilities being "
        f"regarded as critical. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    severity_table_buf = create_scans_table(scans, severity_table_labels, severity_table_values, kev_scan)
    severity_piechart_buffers = create_severity_piechart_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Severity Disposition Header
    y_severity_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_severity_title, True, intro_paragraph)

    # 3. Table of scanners to severity count
    y_severity_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, severity_table_buf)

    # 4. Pie chart explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_severity_table, False, disposition_paragraph)

    # 5. List of disposition pie charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, severity_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_attack_vector_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Attack Vector Disposition page for the PDF export.
    
    Expected page output:
    1) Attack Vector Disposition Header
    2) Introduction paragraph
    3) Table of scanners to attack vector count
    4) Pie charts explination
    5) List of disposition pie charts
    6) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_attack_vector_piechart_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of attack vector disposition pie chart buffers."""
        piecharts = []
        labels = ["Network", "Adjacent", "Local", "Physical"]
        for scan in scans:
            network_ct = scan.return_attack_vector("network")
            adj_network_ct = scan.return_attack_vector("adjacent_network")
            local_ct = scan.return_attack_vector("local")
            physical_ct = scan.return_attack_vector("physical")

            values = [network_ct, adj_network_ct, local_ct, physical_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            network_ct = kev_scan.return_attack_vector("network")
            adj_network_ct = kev_scan.return_attack_vector("adjacent_network")
            local_ct = kev_scan.return_attack_vector("local")
            physical_ct = kev_scan.return_attack_vector("physical")

            values = [network_ct, adj_network_ct, local_ct, physical_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for attack vector."""
        scans_values = []

        for scan in scans:
            network_val = scan.return_attack_vector("network")
            adj_network_val = scan.return_attack_vector("adjacent_network")
            local_val = scan.return_attack_vector("local")
            physical_val = scan.return_attack_vector("physical")

            values = [network_val, adj_network_val, local_val, physical_val]
            scans_values.append(values)

        if kev_scan is not None:
            network_val = kev_scan.return_attack_vector("network")
            adj_network_val = kev_scan.return_attack_vector("adjacent_network")
            local_val = kev_scan.return_attack_vector("local")
            physical_val = kev_scan.return_attack_vector("physical")

            values = [network_val, adj_network_val, local_val, physical_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMREICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_network_scan_name = get_greatest_scan_name(scans, lambda s: s.return_attack_vector("network"))
    greatest_network_scan = call_scan_by_name(scans, greatest_network_scan_name)
    greatest_network_scan_ct = greatest_network_scan.return_attack_vector("network")

    attack_vector_table_values = create_table_values(scans, kev_scan)

    greatest_network_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_attack_vector_percentage("network"))
    greatest_network_perc_scan = call_scan_by_name(scans, greatest_network_perc_scan_name)
    greatest_network_perc_scan_perc = greatest_network_perc_scan.return_attack_vector_percentage("network")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Attack Vector Disposition"

    intro_paragraph = (
        "The attack vector category describes how an attacker could access a vulnerability. "
        "This helps us understand how our vulnerabilities can be exploited and to have a better "
        "understanding of our overall risk . Vulnerabilities with a network attack vector pose the "
        "greatest immediate risk because they can be exploited remotely, while adjacent network "
        "attack vectors are limited to attackers on the same network segment. Local attack vectors "
        "require an attacker to have pre-existing access, and physical attack vectors involve direct " 
        "interaction with the hardware. The following is a table of the disposition of CVEs by "
        "attack vector and scan: "
    )

    attack_vector_table_labels = ["Scanner", "Network", "Adjacent", " Local", "Physical"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of attack vectors throughout each "
        "scan and their relations to their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that can be exploited "
        f"over the network (excluding KEV) was {greatest_network_scan_name} wich had a total of "
        f"{greatest_network_scan_ct} unique vulnerabilities with remote exploitation  "
        f"capabilities. However, the scan with the highest percentage of CVEs that can be "
        f"exploited over the network (excluding KEV) was {greatest_network_perc_scan_name} which "
        f"has a percentage of {greatest_network_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that can be exploited "
        f"over the network was {greatest_network_scan_name} wich had a total of "
        f"{greatest_network_scan_ct} unique vulnerabilities with remote exploitation  "
        f"capabilities. However, the scan with the highest percentage of CVEs that can be "
        f"exploited over the network was {greatest_network_perc_scan_name} which "
        f"has a percentage of {greatest_network_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    attack_vector_table_buf = create_scans_table(scans, attack_vector_table_labels, attack_vector_table_values, kev_scan)
    attack_vector_piechart_buffers = create_attack_vector_piechart_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Attack Vector Disposition Header
    y_attack_vector_title = format_heading1(c, page_height, document_title)

    #2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_attack_vector_title, True, intro_paragraph)

    #3. Table of scanners to attack vector count
    y_attack_vector_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, attack_vector_table_buf)

    #4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_attack_vector_table, False, disposition_paragraph)

    #5. List of disposition pie charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, attack_vector_piechart_buffers)

    #6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_attack_complexity_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Attack Complexity Disposition page of the export.

    Expected page output:
    1) Attack Complexity Disposition Header
    2) Introduction paragraph
    3) Tables of scanners to attack complexity count
    4) Pie charts explination
    5) List of disposition charts
    6) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_attack_complexity_piechart_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of attack vector disposition pie chart buffers."""
        piecharts = []
        labels = ["Low", "Medium", "High"]
        for scan in scans:
            low_ct = scan.return_attack_complexity("low")
            medium_ct = scan.return_attack_complexity("medium")
            high_ct = scan.return_attack_complexity("high")

            values = [low_ct, medium_ct, high_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            low_ct = kev_scan.return_attack_complexity("low")
            medium_ct = kev_scan.return_attack_complexity("medium")
            high_ct = kev_scan.return_attack_complexity("high")

            values = [low_ct, medium_ct, high_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table vlues for each scan for attack complexity."""
        scans_values = []

        for scan in scans:
            low_val = scan.return_attack_complexity("low")
            medium_val = scan.return_attack_complexity("medium")
            high_val = scan.return_attack_complexity("high")

            values = [low_val, medium_val, high_val]
            scans_values.append(values)

        if kev_scan is not None:
            low_val = kev_scan.return_attack_complexity("low")
            medium_val = kev_scan.return_attack_complexity("medium")
            high_val = kev_scan.return_attack_complexity("high")

            values = [low_val, medium_val, high_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_complexity_scan_name = get_greatest_scan_name(scans, lambda s: s.return_attack_complexity("high"))
    greatest_complexity_scan = call_scan_by_name(scans, greatest_complexity_scan_name)
    greatest_complexity_scan_ct = greatest_complexity_scan.return_attack_complexity("high")

    attack_complexity_table_values = create_table_values(scans, kev_scan)

    greatest_complexity_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_attack_complexity_percentage("high"))
    greatest_complexity_perc_scan = call_scan_by_name(scans, greatest_complexity_perc_scan_name)
    greatest_complexity_perc_scan_perc = greatest_complexity_perc_scan.return_attack_complexity_percentage("high")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Attack Complexity Disposition"

    intro_paragraph = (
        "The attack complexity category describes how difficult it is for an attacker to exploit "
        "a vulnerability. This helps us understand whether issues require advanced skills "
        "and specialized techniques (high complexity), can be exploited with moderate effort (medium "
        "complexity), or are straightforward to exploit with minimal knowledge (low complexity). "
        "Vulnerabilities with low attack complexity pose a greater immediate risk because they are "
        "easier to exploit, while those with high complexity demand more intricate and resource-"
        "intensive approaches. The following is a table of the disposition of CVEs by attack complexity "
        "and scan: "
    )

    attack_complexity_table_labels = ["Scanner", "Low", "Medium", "High"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of attack complexity through each "
        "scan and their relations to their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Overall, the scan with the highest count of CVEs that have a low attack complexity "
        f"(excluding KEV) was {greatest_complexity_scan_name} which had a total of "
        f"{greatest_complexity_scan_ct} unique vulnerabilities that have a low attack "
        f"complexity. However, the scan with the highest percentage of CVEs that have a low "
        f"attack complexity (excluding KEV) was {greatest_complexity_perc_scan_name} which has "
        f"a percentage of {greatest_complexity_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Overall, the scan with the highest count of CVEs that have a low attack complexity "
        f"was {greatest_complexity_scan_name} which had a total of "
        f"{greatest_complexity_scan_ct} unique vulnerabilities that have a low attack "
        f"complexity. However, the scan with the highest percentage of CVEs that have a low "
        f"attack complexity was {greatest_complexity_perc_scan_name} which has "
        f"a percentage of {greatest_complexity_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    attack_compexity_table_buf = create_scans_table(scans, attack_complexity_table_labels, attack_complexity_table_values, kev_scan)
    attack_complexity_piechart_buffers = create_attack_complexity_piechart_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Attack Complexity Disposition Header
    y_attack_complexity_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_attack_complexity_title, True, intro_paragraph)

    # 3. Tables of scanners to attack complexity count
    y_attack_complexity_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, attack_compexity_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_attack_complexity_table, False, disposition_paragraph)

    # 5. List of disposition Charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, attack_complexity_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_privileges_required_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Privileges Required Disposition page fo the PDF export.

    Expected page output:
    1) Privileges Required Disoposition Header
    2) Introduction paragraph
    3) Tables of scanners to privileges required count
    4) Pie charts explination
    5) List of disposition charts
    6) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_privileges_required_barechart_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of privileges required disposition pie chart buffers."""
        piecharts = []
        labels = ["None", "Low", "High"]
        for scan in scans:
            none_ct = scan.return_privileges_required("none")
            low_ct = scan.return_privileges_required("low")
            high_ct = scan.return_privileges_required("high")

            values = [none_ct, low_ct, high_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            none_ct = kev_scan.return_privileges_required("none")
            low_ct = kev_scan.return_privileges_required("low")
            high_ct = kev_scan.return_privileges_required("high")

            values = [none_ct, low_ct, high_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for privielges required."""
        scans_values = []

        for scan in scans:
            none_val = scan.return_privileges_required("none")
            low_val = scan.return_privileges_required("low")
            high_val = scan.return_privileges_required("high")

            values = [none_val, low_val, high_val]
            scans_values.append(values)

        if kev_scan is not None:
            none_val = kev_scan.return_privileges_required("none")
            low_val = kev_scan.return_privileges_required("low")
            high_val = kev_scan.return_privileges_required("high")

            values = [none_val, low_val, high_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_privilege_scan_name = get_greatest_scan_name(scans, lambda s: s.return_privileges_required("none"))
    greatest_privilege_scan = call_scan_by_name(scans, greatest_privilege_scan_name)
    greatest_privilege_scan_ct = greatest_privilege_scan.return_privileges_required("none")

    privileges_table_values = create_table_values(scans, kev_scan)

    greatest_privilege_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_privileges_required_percentage("none"))
    greatest_privilege_perc_scan = call_scan_by_name(scans, greatest_privilege_perc_scan_name)
    greatest_privileg_perc_scan_perc = greatest_privilege_perc_scan.return_privileges_required_percentage("none")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Privileges Required Disposition"

    intro_paragraph = (
        "The Privileges Required category describes the level of access an attacker must "
        "possess to successfully exploit a vulnerability. This CVSS metric differentiates "
        "between scenarios where no privileges, low privileges, or high "
        "privileges are required. Vulnerabilities requiring no privileges pose the greatest risk "
        "as they can be exploited without any authentication, while those demanding higher levels "
        "of access are generally more difficult to leverage. The following is a table of the "
        "disposition of CVEs by privileges required and scan: "
    )

    privileges_table_labels = ["Scanner", "None", "Low", "High"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of privileges required through each "
        "scan and their relations to their unique CVE count: "
    )

    reiview_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that require no privileges "
        f"to exploit (excluding KEV) was {greatest_privilege_scan_name} which had a total of "
        f"{greatest_privilege_scan_ct} unique vulnerabilities that require no privileges. However, "
        f"the scan with the highest percentage of CVEs that require no privileges (exlcuding KEV) "
        f"was {greatest_privilege_perc_scan_name} which has a percentage of "
        f"{greatest_privileg_perc_scan_perc}%. "
    )
    reiview_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that require no privileges "
        f"to exploit was {greatest_privilege_scan_name} which had a total of "
        f"{greatest_privilege_scan_ct} unique vulnerabilities that require no privileges. However, "
        f"the scan with the highest percentage of CVEs that require no privileges "
        f"was {greatest_privilege_perc_scan_name} which has a percentage of "
        f"{greatest_privileg_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    privileges_table_buf = create_scans_table(scans, privileges_table_labels, privileges_table_values, kev_scan)
    privileges_piechart_buffers = create_privileges_required_barechart_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Privileges Required Disposition Header
    y_privileges_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_privileges_title, True, intro_paragraph)

    # 3. Tables of scanners to privileges required count
    y_privileges_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, privileges_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_privileges_table, False, disposition_paragraph)

    # 5. List of disposition charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, privileges_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, reiview_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, reiview_paragraph)

def create_user_interaction_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the User Interaction Disposition page of the PDF export.

    Expected page output:
    1) User Interaction Disposition Header
    2) Introduction paragraph
    3) Tables of scanners to user interaction count
    4) Pie charts explination
    5) List of disposition charts
    6) Review paragraph (data explination)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_user_interaction_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of user interaction disposition pie chart buffers"""
        piecharts = []
        labels = ["None", "Required"]
        for scan in scans:
            none_ct = scan.return_user_interaction("none")
            required_ct = scan.return_user_interaction("required")

            values = [none_ct, required_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            none_ct = kev_scan.return_user_interaction("none")
            required_ct = kev_scan.return_user_interaction("required")

            values = [none_ct, required_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)      

        return piecharts
    
    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for user interaction."""
        scans_values = []

        for scan in scans:
            none_val = scan.return_user_interaction("none")
            required_val = scan.return_user_interaction("required")

            values = [none_val, required_val]
            scans_values.append(values)

        if kev_scan is not None:
            none_val = kev_scan.return_user_interaction("none")
            required_val = kev_scan.return_user_interaction("required")

            values = [none_val, required_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_interaction_scan_name = get_greatest_scan_name(scans, lambda s: s.return_user_interaction("none"))
    greatest_interaction_scan = call_scan_by_name(scans, greatest_interaction_scan_name)
    greatest_interaction_scan_ct = greatest_interaction_scan.return_user_interaction("none")

    interaction_table_values = create_table_values(scans, kev_scan)

    greatest_interaction_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_user_interaction_percentage("none"))
    greatest_interaction_perc_scan = call_scan_by_name(scans, greatest_interaction_perc_scan_name)
    greatest_interaction_perc_scan_perc = greatest_interaction_perc_scan.return_user_interaction_percentage("none")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "User Interaction Disposition"

    intro_paragraph = (
        "The User Interaction category describes the extent to which a user must participate "
        "in order for a vulnerability to be exploited. This CVSS metric differentiates between "
        "vulnerabilities that require no user interaction and those that require a user to take "
        "an action. Vulnerabilities requiring no user "
        "interaction pose a greater risk because they can be exploited automatically, whereas those "
        "requiring user interaction depend on additional factors. The following is a table of the "
        "disposition of CVEs by user interaction and scan: "
    )

    interaction_table_labels = ["Scanner", "None", "Required"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of user interaction through each "
        "scan and their relations of their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that require no user interaction "
        f"to exploit (excluding KEV) was {greatest_interaction_scan_name} which had a total of "
        f"{greatest_interaction_scan_ct} unique vulnerabilities that require no privileges. However, "
        f"the scan with the highest percentage of CVEs that require no user interaction (excluding Kev) "
        f"was {greatest_interaction_perc_scan_name} which has a percentage of "
        f"{greatest_interaction_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that require no user interaction "
        f"to exploit was {greatest_interaction_scan_name} which had a total of "
        f"{greatest_interaction_scan_ct} unique vulnerabilities that require no privileges. However, "
        f"the scan with the highest percentage of CVEs that require no user interaction "
        f"was {greatest_interaction_perc_scan_name} which has a percentage of "
        f"{greatest_interaction_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    interaction_table_buf = create_scans_table(scans, interaction_table_labels, interaction_table_values, kev_scan)
    interaction_piechart_buffers = create_user_interaction_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. User Interaction Disposition Header
    y_interaction_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_interaction_title, True, intro_paragraph)

    # 3. Tables of scanners to user interaction count
    y_interaction_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, interaction_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_interaction_table, False, disposition_paragraph)

    # 5. List of disposition charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, interaction_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_confidentiality_impact_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Confidentiality Impact Disposition page of the PDF export.

    Expected page output:
    1) Confidentiality Impact Disposition Header
    2) Introduction paragraph
    3) Tables of scanners to confidentiality count
    4) Pie charts explinaiton
    5) List of disposition charts
    6) Review paragraph (data explinatiion)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_confidentiality_impact_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of confidentiality impact disposition pie chart buffers."""
        piecharts = []
        labels = ["High", "Low", "None"]
        for scan in scans:
            high_ct = scan.return_confidentiality("high")
            low_ct = scan.return_confidentiality("low")
            none_ct = scan.return_confidentiality("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            high_ct = kev_scan.return_confidentiality("high")
            low_ct = kev_scan.return_confidentiality("low")
            none_ct = kev_scan.return_confidentiality("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)            

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for user interaction."""
        scans_values = []

        for scan in scans:
            high_val = scan.return_confidentiality("high")
            low_val = scan.return_confidentiality("low")
            none_val = scan.return_confidentiality("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        if kev_scan is not None:
            high_val = kev_scan.return_confidentiality("high")
            low_val = kev_scan.return_confidentiality("low")
            none_val = kev_scan.return_confidentiality("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_impact_scan_name = get_greatest_scan_name(scans, lambda s: s.return_confidentiality("high"))
    greatest_impact_scan = call_scan_by_name(scans, greatest_impact_scan_name)
    greatest_impact_scan_ct = greatest_impact_scan.return_confidentiality("high")

    impact_table_values = create_table_values(scans, kev_scan)

    greatest_impact_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_confidentiality_percentage("high"))
    greatest_impact_perc_scan = call_scan_by_name(scans, greatest_impact_perc_scan_name)
    greatest_impact_perc_scan_perc = greatest_impact_perc_scan.return_confidentiality_percentage("high")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Confidentiality Impact Disposition"

    intro_paragraph = (
        "The Confidentiality Impact metric measures the extent to which a vulnerability could "
        "compromise the confidentiality of information within a system. This metric evaluates "
        "whether sensitive data may be exposed to unauthorized users, leading to privacy breaches "
        "and data loss. Vulnerabilities with a high confidentiality impact can result in significant "
        "exposure of critical information, while those with lower impact might affect only less "
        "sensitive data. The following is a table of the disposition of CVEs by confidentiality impact and scan: "
    )

    impact_table_labels = ["Scanner", "High", "Low", "None"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of confidentiality impact through each "
        "scan and their relations to their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that have a high confidentiality "
        f"impact (excluding KEV) was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high confidentiality impact (excluding Kev) "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that have a high confidentiality "
        f"impact was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high confidentiality impact "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    impact_table_buf = create_scans_table(scans, impact_table_labels, impact_table_values, kev_scan)
    impact_piechart_buffers = create_confidentiality_impact_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Confidentiality Impact Disposition Header
    y_impact_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_impact_title, True, intro_paragraph)

    # 3. Tables of scanners to confidentiality count
    y_impact_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, impact_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_impact_table, False, disposition_paragraph)

    # 5. List of disposition charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, impact_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_integrity_impact_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Integrity Impact Disposition page of the PDF export.

    Expected page output:
    1) Integrity Impact Disposition Header
    2) Introduction paragraph
    3) Tables of scanners to integrity count
    4) Pie charts explinaiton
    5) List of disposition charts
    6) Review paragraph (data explinatiion)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_integrity_impact_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of integrity impact disposition pie chart buffers."""
        piecharts = []
        labels = ["High", "Low", "None"]
        for scan in scans:
            high_ct = scan.return_integrity("high")
            low_ct = scan.return_integrity("low")
            none_ct = scan.return_integrity("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            high_ct = kev_scan.return_integrity("high")
            low_ct = kev_scan.return_integrity("low")
            none_ct = kev_scan.return_integrity("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)            

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for user interaction."""
        scans_values = []

        for scan in scans:
            high_val = scan.return_integrity("high")
            low_val = scan.return_integrity("low")
            none_val = scan.return_integrity("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        if kev_scan is not None:
            high_val = kev_scan.return_integrity("high")
            low_val = kev_scan.return_integrity("low")
            none_val = kev_scan.return_integrity("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_impact_scan_name = get_greatest_scan_name(scans, lambda s: s.return_integrity("high"))
    greatest_impact_scan = call_scan_by_name(scans, greatest_impact_scan_name)
    greatest_impact_scan_ct = greatest_impact_scan.return_integrity("high")

    impact_table_values = create_table_values(scans, kev_scan)

    greatest_impact_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_integrity_percentage("high"))
    greatest_impact_perc_scan = call_scan_by_name(scans, greatest_impact_perc_scan_name)
    greatest_impact_perc_scan_perc = greatest_impact_perc_scan.return_integrity_percentage("high")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Integrity Impact Disposition"

    intro_paragraph = (
        "The Integrity Impact metric assesses the potential effect of a vulnerability on the integrity "
        "of data within a system. This metric determines whether unauthorized modifications to data can occur, "
        "which could lead to data corruption or manipulation. Vulnerabilities with a high integrity impact may allow "
        "for critical alterations to trusted data, while those with lower impact might permit only minor modifications. "
        "The following is a table of the disposition of CVEs by integrity impact and scan: "
    )

    impact_table_labels = ["Scanner", "High", "Low", "None"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of integrity impact through each "
        "scan and their relations to their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that have a high integrity "
        f"impact (excluding KEV) was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high integrity impact (excluding Kev) "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that have a high integrity "
        f"impact was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high integrity impact "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    impact_table_buf = create_scans_table(scans, impact_table_labels, impact_table_values, kev_scan)
    impact_piechart_buffers = create_integrity_impact_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Integrity Impact Disposition Header
    y_impact_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_impact_title, True, intro_paragraph)

    # 3. Tables of scanners to integrity count
    y_impact_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, impact_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_impact_table, False, disposition_paragraph)

    # 5. List of disposition charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, impact_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)

def create_availability_impact_page(c: canvas, scans: list[SCAN], kev_scan: SCAN):
    """
    Creates the Availability Impact Disposition page of the PDF export.

    Expected page output:
    1) Availability Impact Disposition Header
    2) Introduction paragraph
    3) Tables of scanners to availability count
    4) Pie charts explinaiton
    5) List of disposition charts
    6) Review paragraph (data explinatiion)
    """
    ### 0. NESTED FUNCTIONS ###
    def create_availability_impact_buffers(scans: list[SCAN], kev_scan: SCAN = None) -> list[io.BytesIO]:
        """Given a list of scans, return a list of availability impact disposition pie chart buffers."""
        piecharts = []
        labels = ["High", "Low", "None"]
        for scan in scans:
            high_ct = scan.return_availability("high")
            low_ct = scan.return_availability("low")
            none_ct = scan.return_availability("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)

        if kev_scan is not None:
            high_ct = kev_scan.return_availability("high")
            low_ct = kev_scan.return_availability("low")
            none_ct = kev_scan.return_availability("none")

            values = [high_ct, low_ct, none_ct]
            piechart_buf = create_pie_chart(kev_scan, labels, values, "Disposition")
            piecharts.append(piechart_buf)            

        return piecharts

    def create_table_values(scans: list[SCAN], kev_scan: SCAN = None):
        """Given a list of scans, return the table values for each scan for user interaction."""
        scans_values = []

        for scan in scans:
            high_val = scan.return_availability("high")
            low_val = scan.return_availability("low")
            none_val = scan.return_availability("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        if kev_scan is not None:
            high_val = kev_scan.return_availability("high")
            low_val = kev_scan.return_availability("low")
            none_val = kev_scan.return_availability("none")

            values = [high_val, low_val, none_val]
            scans_values.append(values)

        return scans_values

    ### 1. PAGE LAYOUT RELATED VALUES & FUNCTIONS ###
    page_width, page_height = LETTER

    ### 2. CALCULATE NUMERICAL VALUES & NUMERICAL BASED STRINGS ###
    greatest_impact_scan_name = get_greatest_scan_name(scans, lambda s: s.return_availability("high"))
    greatest_impact_scan = call_scan_by_name(scans, greatest_impact_scan_name)
    greatest_impact_scan_ct = greatest_impact_scan.return_availability("high")

    impact_table_values = create_table_values(scans, kev_scan)

    greatest_impact_perc_scan_name = get_greatest_scan_name(scans, lambda s: s.return_availability_percentage("high"))
    greatest_impact_perc_scan = call_scan_by_name(scans, greatest_impact_perc_scan_name)
    greatest_impact_perc_scan_perc = greatest_impact_perc_scan.return_availability_percentage("high")

    ### 3. TEXT DEFINITIONS (title, headings, paragraph, text) ###
    document_title = "Availability Impact Disposition"

    intro_paragraph = (
        "The Availability Impact metric measures the potential effect of a vulnerability on the accessibility "
        "and usability of a system. This metric indicates whether a vulnerability could disrupt operations, "
        "leading to service downtime or performance degradation. Vulnerabilities with a high availability impact can "
        "cause significant disruptions, while those with a lower impact might lead to only minor interruptions. "
        "The following is a table of the disposition of CVEs by availability impact and scan: "
    )

    impact_table_labels = ["Scanner", "High", "Low", "None"]

    disposition_paragraph = (
        "The following pie charts represent the disposition of availability impact through each "
        "scan and their relations to their unique CVE count: "
    )

    review_paragraph_with_kev = (
        f"Based on the results, the scan with the highest count of CVEs that have a high availability "
        f"impact (excluding KEV) was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high availability impact (excluding Kev) "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )
    review_paragraph = (
        f"Based on the results, the scan with the highest count of CVEs that have a high availability "
        f"impact was {greatest_impact_scan_name} which had a total of "
        f"{greatest_impact_scan_ct} unique vulnerabilities. However, "
        f"the scan with the highest percentage of CVEs that have a high availability impact "
        f"was {greatest_impact_perc_scan_name} which has a percentage of "
        f"{greatest_impact_perc_scan_perc}%. "
    )

    ### 4. CHART GENERATION (creating visual assets) ###
    impact_table_buf = create_scans_table(scans, impact_table_labels, impact_table_values, kev_scan)
    impact_piechart_buffers = create_availability_impact_buffers(scans, kev_scan)

    ### 5. RENDERING ON PDF (text & images in descending order) ###
    # 1. Availability Impact Disposition Header
    y_impact_title = format_heading1(c, page_height, document_title)

    # 2. Introduction paragraph
    y_intro_paragraph = format_paragraph(c, page_width, y_impact_title, True, intro_paragraph)

    # 3. Tables of scanners to availability count
    y_impact_table = draw_centered_image(c, page_width, page_height, 0.25, y_intro_paragraph, impact_table_buf)

    # 4. Pie charts explination
    y_disposition_paragraph = format_paragraph(c, page_width, y_impact_table, False, disposition_paragraph)

    # 5. List of disposition charts
    distribute_images(c, page_width, page_height, 0.26, y_disposition_paragraph, impact_piechart_buffers)

    # 6. Review paragraph (data explination)
    if kev_scan is not None:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph_with_kev)
    else:
        format_paragraph(c, page_width, page_height - (9 * inch), True, review_paragraph)













#Functions for creating the full report.
def create_full_report(output_pdf_path, scans: list[SCAN]):
    """Combines all of the pages together and saves it as a pdf."""
    date_of_creation = datetime.now().strftime("%B %d, %Y")

    kev_scan = return_kev(scans)

    c = canvas.Canvas(output_pdf_path, pagesize=LETTER)

    create_title_page(c, date_of_creation)
    c.showPage()

    create_disclosure_page(c)
    c.showPage()

    create_overview_page(c, date_of_creation, scans, kev_scan)
    c.showPage()

    create_kev_comparison_page(c, scans, kev_scan)
    c.showPage()

    create_severity_page(c, scans, kev_scan)
    c.showPage()

    create_attack_vector_page(c, scans, kev_scan)
    c.showPage()

    create_attack_complexity_page(c, scans, kev_scan)
    c.showPage()

    create_privileges_required_page(c, scans, kev_scan)
    c.showPage()

    create_user_interaction_page(c, scans, kev_scan)
    c.showPage()

    create_confidentiality_impact_page(c, scans, kev_scan)
    c.showPage()

    create_integrity_impact_page(c, scans, kev_scan)
    c.showPage()

    create_availability_impact_page(c, scans, kev_scan)
    c.showPage()

    c.save()
