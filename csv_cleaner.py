#!/usr/bin/env python3
"""
CSV Cleaner for Box Labels
Cleans device_log.csv and prepares it for box label generation
"""

import pandas as pd
import os
from datetime import datetime

def clean_device_csv(input_file="device_log.csv", output_file="cleaned_devices.csv"):
    """Clean and prepare CSV file for box label generation"""
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        return False
    
    try:
        # Read the CSV file
        print(f"📖 Reading {input_file}...")
        df = pd.read_csv(input_file)
        
        print(f"📊 Original file: {len(df)} total rows")
        
        # Filter out PARSE_ERROR rows
        clean_df = df[df['serial_number'] != 'PARSE_ERROR'].copy()
        print(f"🧹 After removing PARSE_ERROR rows: {len(clean_df)} rows")
        
        # Filter out rows with empty serial numbers
        clean_df = clean_df[clean_df['serial_number'].notna() & (clean_df['serial_number'] != '')].copy()
        print(f"🧹 After removing empty serial numbers: {len(clean_df)} rows")
        
        # Create the box labels format with proper column names
        box_df = pd.DataFrame({
            'SERIAL_NUMBER': clean_df['serial_number'],
            'IMEI': clean_df['imei'],
            'MAC_ADDRESS': clean_df['mac_address'],
            'IMSI': clean_df['imsi'],  # Optional, might be useful
            'CCID': clean_df['ccid'],  # Optional, might be useful
            'STC': clean_df['stc'],    # Optional, might be useful
            'STATUS': 'Available',      # Default status
            'TIMESTAMP': clean_df['timestamp']  # Keep original timestamp
        })
        
        # Remove rows with missing essential data
        essential_columns = ['SERIAL_NUMBER', 'IMEI', 'MAC_ADDRESS']
        for col in essential_columns:
            before_count = len(box_df)
            box_df = box_df[box_df[col].notna() & (box_df[col] != '')].copy()
            after_count = len(box_df)
            if before_count != after_count:
                print(f"🧹 Removed {before_count - after_count} rows with missing {col}")
        
        # Sort by timestamp (newest first) or STC number
        if 'STC' in box_df.columns and box_df['STC'].notna().any():
            box_df = box_df.sort_values('STC', ascending=False)
            print("📋 Sorted by STC number (newest first)")
        else:
            box_df = box_df.sort_values('TIMESTAMP', ascending=False)
            print("📋 Sorted by timestamp (newest first)")
        
        # Save cleaned file
        box_df.to_csv(output_file, index=False)
        print(f"✅ Cleaned CSV saved as: {output_file}")
        print(f"📈 Final count: {len(box_df)} devices ready for box labels")
        
        # Show sample data
        print("\n📋 Sample of cleaned data:")
        print("=" * 80)
        for i, row in box_df.head(3).iterrows():
            print(f"{row['SERIAL_NUMBER']} | {row['IMEI']} | {row['MAC_ADDRESS']}")
        print("=" * 80)
        
        # Show statistics
        print(f"\n📊 Statistics:")
        print(f"   • Total devices: {len(box_df)}")
        print(f"   • Potential boxes: {len(box_df) // 20} full boxes")
        print(f"   • Remaining devices: {len(box_df) % 20}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return False

def check_csv_compatibility(csv_file):
    """Check if CSV file is compatible with box label system"""
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📖 Checking {csv_file}...")
        print(f"📊 Columns found: {list(df.columns)}")
        
        required_columns = ['SERIAL_NUMBER', 'IMEI', 'MAC_ADDRESS']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            
            # Check for alternative column names
            alt_mapping = {
                'SERIAL_NUMBER': ['serial_number', 'serialnumber', 'serial'],
                'IMEI': ['imei', 'IMEI'],
                'MAC_ADDRESS': ['mac_address', 'macaddress', 'mac', 'MAC']
            }
            
            print("🔍 Looking for alternative column names...")
            for req_col, alternatives in alt_mapping.items():
                found_alt = [alt for alt in alternatives if alt in df.columns]
                if found_alt:
                    print(f"   • {req_col} could be: {found_alt}")
            
            return False
        else:
            print("✅ All required columns present")
            return True
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def main():
    """Main function"""
    print("🧹 CSV Cleaner for Box Labels")
    print("=" * 50)
    
    # Check original file
    if not check_csv_compatibility("device_log.csv"):
        print("\n🔧 Cleaning and converting device_log.csv...")
        success = clean_device_csv("device_log.csv", "cleaned_devices.csv")
        
        if success:
            print("\n✅ CSV cleaned successfully!")
            print("💡 Use 'cleaned_devices.csv' in the Box Labels tab")
        else:
            print("\n❌ Failed to clean CSV file")
    else:
        print("\n✅ device_log.csv is already compatible!")

if __name__ == "__main__":
    main()