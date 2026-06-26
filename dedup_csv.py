import csv
import sys

def remove_duplicates(filepath):
    seen_ids = set()
    seen_links = set()
    unique_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            job_id = row.get('Job ID', '').strip()
            job_link = row.get('Job Link', '').strip()
            if job_id not in seen_ids and job_link not in seen_links:
                seen_ids.add(job_id)
                seen_links.add(job_link)
                unique_rows.append(row)
                
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in unique_rows:
            writer.writerow(row)

if __name__ == "__main__":
    remove_duplicates("all excels/company_website_jobs.csv")
    print("Deduplication complete.")
