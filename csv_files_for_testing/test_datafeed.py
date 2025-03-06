"""
Enhanced test program to display available NVD data feed options with file sizes and CVE counts.
This script fetches metadata about NVD data feeds and provides more detailed information.
"""

import requests
from bs4 import BeautifulSoup
import re
import gzip
import json
import time
from datetime import datetime
import humanize

def format_size(size_bytes):
    """Format bytes into a human-readable format."""
    if not size_bytes or not size_bytes.isdigit():
        return "Unknown size"
    return humanize.naturalsize(int(size_bytes))

def check_json_feeds_by_year():
    """Check which years have JSON feeds available and get their file sizes."""
    print("\n=== NVD JSON Feeds by Year ===")
    
    current_year = datetime.now().year
    available_years = []
    
    print(f"Checking for JSON feeds from 2002 to {current_year}...")
    for year in range(2002, current_year + 1):
        url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"
        try:
            # Use HEAD request to check availability and get size
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                size = response.headers.get('Content-Length', 'Unknown')
                available_years.append((year, size))
                print(f"✓ {year} feed is available ({format_size(size)})")
            else:
                print(f"✗ {year} feed is not available (status code: {response.status_code})")
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"✗ {year} check failed: {e}")
    
    return available_years

def sample_cve_count(year, sample_size=1024*1024):
    """
    Estimate the number of CVEs in a feed by downloading a sample of the file.
    """
    url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"
    
    try:
        print(f"Sampling {year} feed to estimate CVE count...")
        
        # Stream the file and read only the beginning to estimate structure
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code != 200:
            return "Error accessing feed"
        
        # Get the first chunk of data
        chunk = next(response.iter_content(chunk_size=sample_size))
        response.close()
        
        # Decompress the chunk
        try:
            decompressed = gzip.decompress(chunk)
            
            # Try to find the CVE_Items array and count items
            # This is a heuristic and might not be completely accurate
            items_match = re.search(b'"CVE_Items"\\s*:\\s*\\[', decompressed)
            if items_match:
                # Count the occurrences of CVE IDs to estimate
                cve_id_matches = re.findall(b'"ID"\\s*:\\s*"CVE-[0-9]+-[0-9]+"', decompressed)
                
                # If we found some CVEs, try to extrapolate based on file size
                if cve_id_matches:
                    content_length = int(response.headers.get('Content-Length', 0))
                    if content_length > 0:
                        # Approximate ratio of CVEs in the whole file
                        sample_ratio = min(sample_size / content_length, 1.0)
                        estimated_count = int(len(cve_id_matches) / sample_ratio)
                        return f"~{estimated_count:,} CVEs (estimated)"
            
            return "Could not estimate count"
            
        except Exception as e:
            return f"Error parsing data: {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"
        
def get_detailed_feed_info():
    """Get detailed information about NVD feeds including sizes and CVE counts."""
    print("\n==================================================")
    print("NVD Data Feeds - Detailed Information")
    print("==================================================")
    
    # Get available feeds and their sizes
    available_feeds = check_json_feeds_by_year()
    
    if not available_feeds:
        print("No feeds found or could not access the NVD website.")
        return
    
    # Create a table with detailed information
    print("\n=== Detailed Feed Information ===")
    print(f"{'Year':<6} {'File Size':<15} {'Estimated CVEs':<20} {'Status':<10}")
    print(f"{'-'*6} {'-'*15} {'-'*20} {'-'*10}")
    
    # Get CVE counts for a subset of the feeds to save time (modify as needed)
    years_to_sample = [feed[0] for feed in available_feeds[-5:]]  # Last 5 years
    # Add some older years for comparison
    if len(available_feeds) > 10:
        years_to_sample.extend([feed[0] for feed in available_feeds[-10:-5:2]])  # Every other year from the past
    
    for year, size in available_feeds:
        status = "Available"
        
        # Get CVE count estimate for selected years
        cve_count = "Not sampled"
        if str(year) in years_to_sample:
            cve_count = sample_cve_count(year)
        
        print(f"{year:<6} {format_size(size):<15} {cve_count:<20} {status:<10}")
    
    # Check special feeds
    print("\n=== Special Feeds ===")
    special_feeds = [
        ("modified", "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.json.gz"),
        ("recent", "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz")
    ]
    
    print(f"{'Feed':<10} {'File Size':<15} {'Description':<50}")
    print(f"{'-'*10} {'-'*15} {'-'*50}")
    
    for feed_name, url in special_feeds:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                size = response.headers.get('Content-Length', 'Unknown')
                description = "Last 8 days of updates" if feed_name == "modified" else "Last 120 days of updates"
                print(f"{feed_name:<10} {format_size(size):<15} {description:<50}")
            else:
                print(f"{feed_name:<10} Not available (status code: {response.status_code})")
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"{feed_name:<10} Error: {e}")

if __name__ == "__main__":
    try:
        # Use humanize for better file size formatting
        import humanize
    except ImportError:
        print("Note: For better file size formatting, install humanize: pip install humanize")
        # Create a basic implementation if humanize is not available
        def format_size(size_bytes):
            if not size_bytes or not size_bytes.isdigit():
                return "Unknown size"
            size = int(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024 or unit == 'GB':
                    return f"{size:.1f} {unit}"
                size /= 1024
    
    get_detailed_feed_info()
    
    print("\n==================================================")
    print("Test completed.")
    print("==================================================")