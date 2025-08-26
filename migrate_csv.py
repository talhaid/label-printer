#!/usr/bin/env python3
"""
CSV Migration Script
Converts old CSV format to new organized save folder structure
"""

import pandas as pd
import os
from datetime import datetime

def migrate_csv_data():
    """Migrate CSV data from old format to new format in save folder"""
    
    print("🔄 CSV Migration & Format Update")
    print("=" * 50)
    
    old_csv_path = "device_log.csv"
    new_csv_path = os.path.join("save", "csv", "device_log.csv")
    
    # Ensure save directory exists
    save_dir = os.path.dirname(new_csv_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"✅ Created directory: {save_dir}")
    
    if os.path.exists(old_csv_path):
        print(f"📖 Reading old CSV format from: {old_csv_path}")
        
        try:
            # Read old CSV
            old_df = pd.read_csv(old_csv_path)
            print(f"   Found {len(old_df)} records")
            
            # Convert to new format
            new_data = []
            
            for _, row in old_df.iterrows():
                # Skip parse errors for clean migration
                if row.get('serial_number', '') == 'PARSE_ERROR':
                    continue
                    
                # Convert old format to new format
                new_row = {
                    'STC': row.get('stc', ''),
                    'SERIAL_NUMBER': row.get('serial_number', ''),
                    'IMEI': row.get('imei', ''),
                    'IMSI': row.get('imsi', ''),
                    'CCID': row.get('ccid', ''),
                    'MAC_ADDRESS': row.get('mac_address', ''),
                    'STATUS': 'Printed' if str(row.get('print_status', '')).startswith('SUCCESS') else 'Error',
                    'TIMESTAMP': row.get('timestamp', '')
                }
                new_data.append(new_row)
            
            # Create new DataFrame
            new_df = pd.DataFrame(new_data)
            
            if len(new_df) > 0:
                # Save to new location
                new_df.to_csv(new_csv_path, index=False)
                print(f"✅ Migrated {len(new_df)} valid records to: {new_csv_path}")
                
                # Show sample of migrated data
                print("\n📋 Sample migrated data:")
                print("=" * 60)
                print(new_df.head(3).to_string(index=False))
                
            else:
                print("⚠️ No valid records found to migrate")
                
        except Exception as e:
            print(f"❌ Error migrating CSV: {e}")
            
    else:
        print("⚠️ No old CSV file found, creating fresh CSV")
        
        # Create fresh CSV with headers only
        headers_df = pd.DataFrame(columns=[
            'STC', 'SERIAL_NUMBER', 'IMEI', 'IMSI', 
            'CCID', 'MAC_ADDRESS', 'STATUS', 'TIMESTAMP'
        ])
        headers_df.to_csv(new_csv_path, index=False)
        print(f"✅ Created fresh CSV file: {new_csv_path}")
    
    print(f"\n📊 Final status:")
    print(f"   📂 Save folder: {os.path.exists('save')}")
    print(f"   📂 CSV folder: {os.path.exists(os.path.join('save', 'csv'))}")
    print(f"   📄 New CSV file: {os.path.exists(new_csv_path)}")
    print(f"   📂 ZPL folder: {os.path.exists(os.path.join('save', 'zpl_output'))}")
    
    print(f"\n🎉 Migration complete! System ready for organized logging.")

if __name__ == "__main__":
    migrate_csv_data()