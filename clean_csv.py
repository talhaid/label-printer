#!/usr/bin/env python3
"""
Clean CSV Script - Remove PARSE_ERROR entries and invalid data from device_log.csv
"""

import csv
import os
from datetime import datetime

def clean_csv_file():
    """Clean the CSV file by removing PARSE_ERROR entries and invalid data."""
    csv_path = os.path.join("save", "csv", "device_log.csv")
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    # Read the original data
    valid_rows = []
    total_rows = 0
    removed_rows = 0
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        
        for row in reader:
            total_rows += 1
            
            # Check if this is a valid row (not PARSE_ERROR)
            serial_number = row.get('SERIAL_NUMBER', '').strip()
            
            if serial_number and serial_number != 'PARSE_ERROR' and serial_number != '':
                # This is a valid device entry
                valid_rows.append(row)
            else:
                # This is an invalid entry to remove
                removed_rows += 1
                print(f"Removing invalid row: {serial_number}")
    
    print(f"\nCleaning Summary:")
    print(f"Total rows read: {total_rows}")
    print(f"Valid rows kept: {len(valid_rows)}")
    print(f"Invalid rows removed: {removed_rows}")
    
    # Write the cleaned data back
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        if headers:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(valid_rows)
    
    print(f"\nCleaned CSV saved to: {csv_path}")
    
    # Show the cleaned content
    if valid_rows:
        print(f"\nCleaned CSV content ({len(valid_rows)} valid entries):")
        for i, row in enumerate(valid_rows, 1):
            stc = row.get('STC', '')
            sn = row.get('SERIAL_NUMBER', '')
            status = row.get('STATUS', '')
            timestamp = row.get('TIMESTAMP', '')
            print(f"  {i:2d}. STC:{stc} | SN:{sn} | Status:{status} | Time:{timestamp}")
    else:
        print("\nNo valid entries found in CSV.")

if __name__ == "__main__":
    print("🧹 Cleaning CSV file...")
    clean_csv_file()
    print("✅ CSV cleaning completed!")