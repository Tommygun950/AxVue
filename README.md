# Axiom Perspective

A vulnerability scan analysis tool for cybersecurity professionals to process, analyze, and report on CVE (Common Vulnerabilities and Exposures) data.

## Overview

Axiom Perspective is a PyQt5-based desktop application designed to streamline the workflow of cybersecurity analysts. The tool provides a comprehensive suite of functionality for managing vulnerability scan data, interfacing with the National Vulnerability Database (NVD), and generating detailed reports.

## Key Features

- **Scan Import**: Import vulnerability scan data from CSV files
- **NVD API Integration**: Retrieve detailed CVE information using NVD API keys
- **Local Caching**: Store CVE data locally to reduce API calls and improve performance
- **Data Visualization**: View and analyze vulnerability metrics and trends
- **Report Generation**: Export comprehensive vulnerability reports in multiple formats

## Application Structure

The application is organized into five main sections:

1. **Scans**: Import and manage vulnerability scan data from CSV files
2. **API Keys**: Configure NVD API keys for retrieving CVE data
3. **Cache**: Manage locally cached CVE data
4. **Create Report**: Generate detailed vulnerability reports
5. **Exports**: View and manage previously exported reports

## Technical Architecture

### GUI Components

The application uses a modular approach with the following components for each section:

- **GUI Files**: Implementation of visual elements and user interactions
- **Backend Files**: Database operations and business logic
- **Dialog Files**: Modal windows for user input
- **Style Files**: Visual styling and theming

### Key Modules

- **database_processing.py**: Database initialization and schema management
- **cve_processing.py**: CVE data retrieval and processing from NVD API
- **scans_processing.py**: CSV parsing and scan data processing

### Database Structure

The application uses SQLite3 with the following main tables:

- **cves**: Stores detailed CVE information including CVSS metrics
- **nvd_api_key**: Manages NVD API keys
- **scan_data**: Stores imported scan information
- **stored_nvd_data_feed**: Tracks cached NVD data
- **past_exports**: Records export history

## Development

### Testing

The project includes comprehensive unit tests for all major components:

- **test_backend_api_keys.py**: Tests for API key management
- **test_dialogs_api_keys.py**: Tests for API key dialog functionality
- **test_gui_api_keys.py**: Tests for API key GUI components
- **test_style_api_keys.py**: Tests for API key styling
- **test_backend_scans.py**: Tests for scan processing
- **test_dialogs_scans.py**: Tests for scan dialog functionality 
- **test_style_scans.py**: Tests for scan styling
- **test_cve_processing.py**: Tests for CVE data handling
- **test_database_processing.py**: Tests for database operations
- **test_scans_processing.py**: Tests for scan file processing

### Dependencies

- **PyQt5**: GUI framework
- **sqlite3**: Local database
- **requests**: HTTP requests for NVD API
- **pytest**: Testing framework

## Installation

1. Ensure Python 3.6+ is installed
2. Install required dependencies:
   ```
   pip install PyQt5 requests pytest
   ```
3. Run the application:
   ```
   python -m gui
   ```

## Usage

1. **Import Scans**: Add vulnerability scan CSV files through the Scans page
2. **Configure API Keys**: Add your NVD API keys on the API Keys page
3. **Manage Cache**: View and update cached CVE data
4. **Generate Reports**: Select scans and create detailed vulnerability reports
5. **View Exports**: Access and manage previously generated reports

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]