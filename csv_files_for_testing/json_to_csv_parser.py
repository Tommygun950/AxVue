import json
import csv
import os

def json_to_csv(json_file, csv_file):
    # Open and load the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the list of CVE items
    items = data.get("CVE_Items", [])
    
    # Define the CSV columns
    fieldnames = [
        "CVE_ID", 
        "Assigner", 
        "PublishedDate", 
        "LastModifiedDate", 
        "Description", 
        "ProblemType", 
        "FirstReferenceURL"
    ]
    
    # Open the CSV file for writing
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Iterate over each CVE item and extract details
        for item in items:
            cve_data = item.get("cve", {})
            meta = cve_data.get("CVE_data_meta", {})
            cve_id = meta.get("ID", "")
            assigner = meta.get("ASSIGNER", "")
            published_date = item.get("publishedDate", "")
            last_modified_date = item.get("lastModifiedDate", "")
            
            # Get the English description (if available)
            description_data = cve_data.get("description", {}).get("description_data", [])
            description = ""
            for desc in description_data:
                if desc.get("lang", "") == "en":
                    description = desc.get("value", "")
                    break

            # Get the problem type if available (join multiple descriptions if present)
            problemtype_data = cve_data.get("problemtype", {}).get("problemtype_data", [])
            problem_type = ""
            if problemtype_data:
                descriptions = problemtype_data[0].get("description", [])
                if descriptions:
                    problem_type = ", ".join([d.get("value", "") for d in descriptions if "value" in d])
            
            # Get the first reference URL if available
            references = cve_data.get("references", {}).get("reference_data", [])
            first_reference_url = references[0].get("url", "") if references else ""
            
            # Create a row dictionary for CSV output
            row = {
                "CVE_ID": cve_id,
                "Assigner": assigner,
                "PublishedDate": published_date,
                "LastModifiedDate": last_modified_date,
                "Description": description,
                "ProblemType": problem_type,
                "FirstReferenceURL": first_reference_url
            }
            writer.writerow(row)

if __name__ == "__main__":
    # Prompt for the JSON file path.
    json_file = input("Please enter the JSON file path: ").strip()
    # Prompt for just a file name for the CSV output.
    output_filename = input("Please enter the output CSV file name (e.g., output.csv): ").strip()
    
    # Determine the directory where the script is located.
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    
    # Build the output CSV file path in the same directory as the script.
    csv_file = os.path.join(script_dir, output_filename)
    
    try:
        json_to_csv(json_file, csv_file)
        print(f"CSV file '{csv_file}' has been created in the script's directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
