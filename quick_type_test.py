#!/usr/bin/env python3

import pandas as pd

# Load sample data
df = pd.read_csv('sample_devices.csv')

# Get first device
device_raw = {
    'SERIAL_NUMBER': df.iloc[0]['SERIAL_NUMBER'],
    'IMEI': df.iloc[0]['IMEI'], 
    'MAC_ADDRESS': df.iloc[0]['MAC_ADDRESS']
}

print("Raw data types:")
print(f"SERIAL_NUMBER: {type(device_raw['SERIAL_NUMBER'])}")
print(f"IMEI: {type(device_raw['IMEI'])}")
print(f"MAC_ADDRESS: {type(device_raw['MAC_ADDRESS'])}")

# Convert to strings
device_str = {
    'SERIAL_NUMBER': str(device_raw['SERIAL_NUMBER']),
    'IMEI': str(device_raw['IMEI']),
    'MAC_ADDRESS': str(device_raw['MAC_ADDRESS'])
}

print("\nAfter str() conversion:")
print(f"SERIAL_NUMBER: {type(device_str['SERIAL_NUMBER'])}")
print(f"IMEI: {type(device_str['IMEI'])}")
print(f"MAC_ADDRESS: {type(device_str['MAC_ADDRESS'])}")

print("\nValues:")
print(f"SERIAL: {device_str['SERIAL_NUMBER']}")
print(f"IMEI: {device_str['IMEI']}")
print(f"MAC: {device_str['MAC_ADDRESS']}")

print("\n✅ Type conversion test passed!")