"""This file includes all unit testing for all CVE processing functions."""
import sqlite3
from pathlib import Path
import pytest
from cve_processing import store_cves_from_csv


def query_db(db_path: str) -> list[str]:
    """Helper function to query the DB and return the list of CVE IDs."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cve_id FROM cves")
    rows = [row[0] for row in cursor.fetchall()]
    conn.close()
    return rows

def test_empty_csv(tmp_path: Path):
    """Test that an empty CSV file raises a ValueError."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")  # Create an empty file.
    db_file = tmp_path / "empty.db"

    with pytest.raises(ValueError, match="CSV file is empty."):
        store_cves_from_csv(str(csv_file), str(db_file))


def test_missing_cve_header(tmp_path: Path):
    """Test that a CSV with no header containing 'CVE' raises a ValueError."""
    csv_file = tmp_path / "missing_header.csv"
    # Header does not contain the word "CVE"
    csv_file.write_text("id,base_score\nsome_id,5.0")
    db_file = tmp_path / "missing_header.db"

    with pytest.raises(ValueError, match="No column containing 'CVE' was found in the CSV file."):
        store_cves_from_csv(str(csv_file), str(db_file))


def test_single_cve(tmp_path: Path):
    """Test processing of a CSV with a single valid CVE entry."""
    csv_file = tmp_path / "single.csv"
    csv_file.write_text("CVE,base_score\nCVE-1234,5.0")
    db_file = tmp_path / "single.db"

    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    assert rows == ["CVE-1234"]


def test_multiple_cves_in_one_cell(tmp_path: Path):
    """Test that a CSV cell containing multiple CVEs separated by commas is split correctly.
    
    Note: The cell is quoted so that the CSV reader does not pre-split the comma.
    """
    csv_file = tmp_path / "multiple.csv"
    csv_content = 'CVE,base_score\n"CVE-1234, CVE-5678",5.0'
    csv_file.write_text(csv_content)
    db_file = tmp_path / "multiple.db"

    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    # Order is not guaranteed so we sort before comparing.
    assert sorted(rows) == sorted(["CVE-1234", "CVE-5678"])


def test_duplicate_cves(tmp_path: Path):
    """Test that duplicate CVEs (separate rows or in 1 cell) are only inserted once."""
    # Test duplicate in separate rows.
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text("CVE,base_score\nCVE-1234,5.0\nCVE-1234,5.0")
    db_file = tmp_path / "duplicates.db"
    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    assert rows == ["CVE-1234"]

    # Test duplicate in one cell.
    csv_file2 = tmp_path / "duplicates2.csv"
    csv_content = 'CVE,base_score\n"CVE-1234, CVE-1234",5.0'
    csv_file2.write_text(csv_content)
    db_file2 = tmp_path / "duplicates2.db"
    store_cves_from_csv(str(csv_file2), str(db_file2))
    rows2 = query_db(str(db_file2))
    assert rows2 == ["CVE-1234"]


def test_nonexistent_csv(tmp_path: Path):
    """Test that trying to process a CSV file that does not exist raises FileNotFoundError."""
    db_file = tmp_path / "nonexistent.db"
    nonexistent_csv = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        store_cves_from_csv(str(nonexistent_csv), str(db_file))


def test_row_with_insufficient_columns(tmp_path: Path):
    """Test that a row that is empty (or does not have enough columns) is simply skipped."""
    csv_file = tmp_path / "insufficient.csv"
    # The first row is the header; second row is empty; third row is valid.
    csv_content = "CVE,base_score\n\nCVE-1234,5.0"
    csv_file.write_text(csv_content)
    db_file = tmp_path / "insufficient.db"

    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    # The empty row should not insert anything.
    assert rows == ["CVE-1234"]


def test_header_in_second_row(tmp_path: Path):
    """Test a CSV where the header (with the 'CVE' column) appears in the second row.
    
    In this case, the first row (which does not have 'CVE') will be processed as data.
    """
    csv_file = tmp_path / "header_second.csv"
    csv_content = "dummy1,dummy2\nCVE,base_score\nCVE-1234,5.0"
    csv_file.write_text(csv_content)
    db_file = tmp_path / "header_second.db"

    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    # The header row (second row in the file) gets processed as data, so "CVE" is also inserted.
    assert sorted(rows) == sorted(["CVE", "CVE-1234"])


def test_whitespace_handling(tmp_path: Path):
    """Test that extra whitespace in headers and data is trimmed appropriately."""
    csv_file = tmp_path / "whitespace.csv"
    csv_content = "  CVE  , base_score\n  CVE-1234  , 5.0\n , 5.0"
    csv_file.write_text(csv_content)
    db_file = tmp_path / "whitespace.db"

    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    # Only a nonempty, trimmed CVE should be inserted.
    assert rows == ["CVE-1234"]


def test_existing_db_file(tmp_path: Path):
    """Test that store_cves_from_csv works correctly when the database file already exists."""
    db_file = tmp_path / "existing.db"
    # Create a pre-existing DB with a table and one CVE.
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE cves (
            cve_id TEXT PRIMARY KEY,
            base_score REAL,
            severity TEXT,
            attack_vector TEXT,
            attack_complexity TEXT,
            privileges_required TEXT,
            user_interaction TEXT,
            confidentiality_impact TEXT,
            integrity_impact TEXT,
            availability_impact TEXT
        );
        """
    )
    cursor.execute("INSERT INTO cves (cve_id) VALUES (?)", ("CVE-0000",))
    conn.commit()
    conn.close()

    # Now process a CSV to add a new CVE.
    csv_file = tmp_path / "new_cve.csv"
    csv_file.write_text("CVE,base_score\nCVE-1234,5.0")
    store_cves_from_csv(str(csv_file), str(db_file))
    rows = query_db(str(db_file))
    # Both the preexisting CVE and the new one should be present.
    assert sorted(rows) == sorted(["CVE-0000", "CVE-1234"])
