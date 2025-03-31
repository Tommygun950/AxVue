# AxVue

A Python-based GUI application for comparing vulnerability scan results to aid security teams visualize performance differences.

## Table of Contents
- [About](#-about)
- [Features](#-features)
- [Setup](#-setup)
- [Feedback](#-feedback)
- [Usage](#-usage)

## 🚀 About

AxVue is a desktop appplication designed to help security teams analyze and compare vulnerability scan results. It processes CSV reports from vulnerability
scanners, extracts CVE-ID information, and generates detailed reports showing trends between the results. The project leverages the NVD (National Vulnerability Database)
API by collecting CVSS metric data for each parsed CVE-ID in order to make a fully comprehensive report. This program can either be used as comparing vulnerability scans
of similar scope from various sources or analyzing performance trends in a single vulnerability scanner.

## ✨ Features
- Ability to import and compare multiple vulnerability scan results to compare products or track security improvements over time.
- Automatically parses CSV exports without the user having to specifcy the CVE-ID index or formatting.
- Pulls base and temportal CVSS metric data from the NVD API for detailed vulnerability analysis and reporting.
- Functional API key management that allows user to add multiple API keys for continuity as well as automated key validation.
- CVE caching to reduce API calls and improve performance time, which is toggleable for each scan for security reasons.
- Customizable reports which allows the user to export to Excel or PDF and can select which data is included.
- Automatic KEV Catalog recognition if user wanted to visualize attack surface in reference to CVEs in the KEV.

## ⚙️ Setup

### Prerequisites
- Python 3.8 or higher
- A NVD API Key -> https://nvd.nist.gov/developers/request-an-api-key

### Installation
1. Clone the repository:
```shell
git clone https://github.com/Tommygun950/AxVue
```

2. Install dependencies:
```shell
pip install -r requirements.txt
```

3. Run the application:
```shell
python main.py
```

## 📃 Feedback
This project is still in developement. While currently not functional through the GUI, the backend code for the PDF creation has been tested and works. The initial
prototype of this project solely worked through the CLI, and converting everything to a GUI has resulted in functional delay and a lot of additional code. This README
will continue to be updated and will be more encompasing once the program has reached MVP status.

## 🌐 Usage
All contributions are welcom, and if you identify any issues with the code please feel free to create an issue on this repository. My aspiration is to make this repository
open sourced and useful to security teams looking to analyze their security posture from a holistic viewpoint, so feel free to use this project as you wish.
