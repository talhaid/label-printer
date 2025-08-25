# Koli Window - CSV Data Viewer Guide

## Overview
The **Koli Window** is a new feature that provides a comprehensive view of all CSV data logged by the Zebra GC420T printing system. It offers advanced filtering, searching, and export capabilities for data analysis.

## Accessing the Koli Window

### Opening the Window
1. **Menu Access**: `Windows → Koli`
2. **Window Management**: The window can be opened multiple times, but only one instance will be active
3. **Independent Operation**: Works alongside the main printer interface

## Features

### Data Display
- **Complete CSV View**: Shows all records from `device_log.csv`
- **Sortable Columns**: Data sorted by timestamp (most recent first)
- **Comprehensive Information**: All device data fields displayed in organized columns

### Columns Displayed
| Column | Description |
|--------|-------------|
| Timestamp | Date and time of processing |
| Serial Number | Device serial number |
| IMEI | Device IMEI number |
| IMSI | Device IMSI number |
| CCID | Device CCID number |
| MAC Address | Device MAC address |
| STC | Serial Tracking Code assigned |
| Status | Print operation status (SUCCESS/FAILED/etc.) |
| ZPL File | Generated ZPL filename |
| Raw Data | Original serial data received |

### Search and Filter
- **Real-time Search**: Type in search box to filter results instantly
- **Multi-field Search**: Searches across all relevant columns
- **Case-insensitive**: Search terms are not case-sensitive
- **Live Counter**: Shows current number of displayed records

### Data Management
- **Refresh Data**: Update table with latest CSV entries
- **Export Filtered Data**: Save current view to new CSV file
- **Status Information**: Real-time feedback on operations

## Usage Instructions

### Basic Operations
1. **Open Koli Window**: Use `Windows → Koli` from menu
2. **View Data**: Scroll through all logged device records
3. **Search**: Type in search box to find specific records
4. **Refresh**: Click "Refresh Data" to update with latest entries

### Searching Data
```
Search Examples:
- "ATS542" - Find devices with serial starting with ATS542
- "SUCCESS" - Show only successful print operations
- "2025-08-25" - Show records from specific date
- "6000" - Find records with STC 6000
```

### Exporting Data
1. **Filter First**: Use search to narrow down desired records
2. **Click Export**: Use "Export CSV" button
3. **Choose Location**: Select where to save the filtered data
4. **Confirmation**: Success message confirms export completion

## Data Structure

### CSV Format
The window displays data from `device_log.csv` with the following structure:
```csv
timestamp,serial_number,imei,imsi,ccid,mac_address,stc,print_status,zpl_file,raw_data
2025-08-25 12:05:40,ATS542912923728,866988074133496,286019876543210,8991101200003204510,AA:BB:CC:DD:EE:FF,6000,SUCCESS,ATS542912923728_20250825_120540.zpl,##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
```

### Status Values
- **SUCCESS**: Label printed successfully
- **FAILED**: Print operation failed
- **PARSE_ERROR**: Data parsing failed
- **TEMPLATE_ERROR**: Template validation failed
- **ERROR**: General system error

## Practical Use Cases

### Quality Control
- **Failed Print Review**: Search for "FAILED" to identify problem devices
- **Date Range Analysis**: Filter by specific dates to analyze daily production
- **Device Tracking**: Search by serial number to trace device history

### Production Monitoring
- **STC Verification**: Ensure sequential STC assignment
- **Status Distribution**: Review success/failure rates
- **Template Validation**: Identify template-related issues

### Data Analysis
- **Export for Analysis**: Save filtered data for external tools
- **Trend Identification**: Review patterns in device processing
- **Audit Trails**: Complete tracking of all processed devices

## Technical Details

### Performance
- **Optimized Loading**: Handles large CSV files efficiently
- **Real-time Filtering**: Instant search results
- **Memory Management**: Efficient data handling for large datasets

### File Handling
- **Automatic Detection**: Detects when CSV file is available
- **Error Handling**: Graceful handling of missing or locked files
- **Encoding Support**: UTF-8 encoding for international characters

## Troubleshooting

### Common Issues
1. **"CSV file not found"**: `device_log.csv` doesn't exist yet
   - **Solution**: Process some devices first to create the file

2. **Empty Window**: No data displayed
   - **Solution**: Click "Refresh Data" or check if CSV file has data

3. **Search Not Working**: Filter results seem incorrect
   - **Solution**: Clear search box and try again

4. **Export Failed**: Cannot save exported file
   - **Solution**: Ensure target directory is writable

### Error Messages
- **"Error loading CSV"**: File might be locked (close Excel if open)
- **"Error filtering data"**: Search term might contain special characters
- **"Failed to export data"**: Check file permissions and disk space

## Future Enhancements

The Koli window is designed for future expansion and could include:
- Advanced filtering options
- Data visualization charts
- Statistical summaries
- Integration with external databases
- Custom report generation

## Integration with Main System

### Data Synchronization
- **Real-time Updates**: New records appear automatically when refreshed
- **Consistent Data**: Same data source as main application
- **Independent Operation**: Doesn't interfere with printing operations

### Workflow Integration
- **Parallel Operation**: Use alongside normal printing workflow
- **Quality Assurance**: Monitor production quality in real-time
- **Historical Analysis**: Review past performance and identify improvements

The Koli window provides powerful data management capabilities that complement the main printing system, offering comprehensive insights into your device processing operations.