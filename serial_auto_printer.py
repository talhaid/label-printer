#!/usr/bin/env python3
"""
Zebra GC420T Serial Port Auto-Printer
=====================================

This module monitors a serial port for device data and automatically prints
labels using ZPL templates with placeholders.

Data Format Expected: ##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
Fields: ##SERIAL_NUMBER|IMEI|IMSI|CCID|MAC_ADDRESS##

Features:
- Serial port monitoring
- Automatic data parsing with regex
- ZPL template processing with placeholders
- Real-time printing
- Data logging
- Error handling and recovery

Author: Serial Auto-Printer for Zebra GC420T
Date: August 2025
"""

import os
import sys
import re
import time
import logging
import threading
import csv
from typing import Dict, Optional, Callable
from datetime import datetime
import json

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    print("Warning: pyserial not available. Install pyserial for serial port support.")
    SERIAL_AVAILABLE = False
    serial = None

from zebra_zpl import ZebraZPL

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_printer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeviceDataParser:
    """Parse device data from serial port using regex patterns."""
    
    def __init__(self):
        self.packet_buffer = ""  # Buffer for incomplete packets
        
        # Primary pattern - complete 5 fields (handle ANY whitespace characters)
        self.primary_pattern = re.compile(
            r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\s*\|([0-9A-F]+)\|([A-F0-9:]+)##'
        )
        
        # Flexible patterns for incomplete data (handle ANY whitespace)
        self.flexible_patterns = [
            # 3 fields: SERIAL|IMEI|IMSI (with any whitespace after)
            re.compile(r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)(?:\s*\|?|##?)'),
            # 4 fields: SERIAL|IMEI|IMSI|CCID (handle whitespace after IMSI)
            re.compile(r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\s*\|([0-9A-F]+)(?:\s*\|?|##?)'),
            # 5 fields but may have whitespace: SERIAL|IMEI|IMSI|CCID|MAC
            re.compile(r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\s*\|([0-9A-F]+)\|([A-F0-9:]+)(?:##?)'),
            # Ultra flexible - any characters after IMSI
            re.compile(r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)(.*)'),
        ]
        
        # Backup patterns for different formats
        self.backup_patterns = [
            # Pattern without ## delimiters
            re.compile(r'([A-Z0-9]+)\|([0-9]+)\|([0-9\s]+)\|([0-9A-F]+)\|([A-F0-9:]+)'),
            # Pattern with different delimiters
            re.compile(r'#([A-Z0-9]+)\|([0-9]+)\|([0-9\s]+)\|([0-9A-F]+)\|([A-F0-9:]+)#'),
            # Pattern with comma separators
            re.compile(r'##([A-Z0-9]+),([0-9]+),([0-9\s]+),([0-9A-F]+),([A-F0-9:]+)##'),
        ]
        
        # Field mapping
        self.field_names = [
            'SERIAL_NUMBER',
            'IMEI', 
            'IMSI',
            'CCID',
            'MAC_ADDRESS'
        ]
    
    def _clean_special_characters(self, data: str) -> str:
        """
        Clean special whitespace, control characters, and any non-printable characters.
        Only keeps letters, numbers, and safe punctuation characters.
        
        Args:
            data (str): Raw data string
            
        Returns:
            str: Cleaned data string with only safe characters
        """
        # First, replace known problematic Unicode characters with spaces
        replacements = {
            '\u00A0': ' ',  # Non-breaking space
            '\u2002': ' ',  # En space
            '\u2003': ' ',  # Em space
            '\u2004': ' ',  # Three-per-em space
            '\u2005': ' ',  # Four-per-em space
            '\u2006': ' ',  # Six-per-em space
            '\u2007': ' ',  # Figure space
            '\u2008': ' ',  # Punctuation space
            '\u2009': ' ',  # Thin space
            '\u200A': ' ',  # Hair space
            '\u202F': ' ',  # Narrow no-break space
            '\u3000': ' ',  # Ideographic space
            '\u0009': ' ',  # Tab
            '\u000B': ' ',  # Vertical tab
            '\u000C': ' ',  # Form feed
            '\u000D': '',   # Carriage return
            '\u0085': ' ',  # Next line
        }
        
        cleaned = data
        for char, replacement in replacements.items():
            cleaned = cleaned.replace(char, replacement)
        
        # Now filter out ALL non-printable ASCII characters
        # Keep only: letters, numbers, space, and safe punctuation: # | : -
        filtered_chars = []
        for char in cleaned:
            ascii_code = ord(char)
            
            # Keep safe characters:
            if (
                (48 <= ascii_code <= 57) or    # 0-9 numbers
                (65 <= ascii_code <= 90) or    # A-Z uppercase  
                (97 <= ascii_code <= 122) or   # a-z lowercase
                ascii_code == 32 or            # space
                ascii_code == 35 or            # # (hash)
                ascii_code == 124 or           # | (pipe)
                ascii_code == 58 or            # : (colon)
                ascii_code == 45               # - (hyphen)
            ):
                filtered_chars.append(char)
            else:
                # Log the problematic character for debugging
                if ascii_code != 32:  # Don't log every space
                    logger.warning(f"Filtered out non-printable character: ASCII {ascii_code} (0x{ascii_code:02X}) = {repr(char)}")
        
        final_cleaned = ''.join(filtered_chars)
        
        # Log if we found special characters
        if final_cleaned != data:
            logger.info(f"Cleaned problematic characters: {repr(data)} -> {repr(final_cleaned)}")
            
        return final_cleaned

    def parse_data(self, raw_data: str) -> Optional[Dict[str, str]]:
        """
        Parse device data from raw serial input.
        
        Args:
            raw_data (str): Raw data from serial port
            
        Returns:
            Dict[str, str]: Parsed device data or None if no match
        """
        # Clean the data - remove special characters
        raw_data = self._clean_special_characters(raw_data.strip())
        logger.info(f"Parsing data: {repr(raw_data)}")
        
        # Try primary pattern first (complete 5 fields)
        match = self.primary_pattern.search(raw_data)
        pattern_used = "primary"
        fields_found = 5
        
        # If no match with complete data, try flexible patterns
        if not match:
            for i, pattern in enumerate(self.flexible_patterns):
                match = pattern.search(raw_data)
                if match:
                    pattern_used = f"flexible_{i+1}"
                    fields_found = len(match.groups())
                    break
        
        # If still no match, try backup patterns
        if not match:
            for i, pattern in enumerate(self.backup_patterns):
                match = pattern.search(raw_data)
                if match:
                    pattern_used = f"backup_{i+1}"
                    fields_found = len(match.groups())
                    break
        
        if not match:
            logger.warning(f"No valid data pattern found in: {raw_data}")
            # Try to extract any data that looks like device info
            self._log_failed_parsing_attempt(raw_data)
            return None
        
        logger.info(f"Matched using {pattern_used} pattern, found {fields_found} fields")
        
        # Extract values
        values = list(match.groups())
        
        # Handle incomplete data by filling missing fields
        while len(values) < len(self.field_names):
            if len(values) == 3:  # Missing CCID and MAC (like your current data)
                values.append("UNKNOWN_CCID")
                values.append("00:00:00:00:00:00")
            elif len(values) == 4:  # Missing MAC only
                values.append("00:00:00:00:00:00")
            else:
                values.append("UNKNOWN")
        
        logger.info(f"Final values after padding: {values}")
        
        # Create device data dictionary
        device_data = {}
        for i, field_name in enumerate(self.field_names):
            if i < len(values):
                # Clean the value (remove extra spaces)
                clean_value = values[i].strip()
                
                # Special handling for SERIAL_NUMBER - remove ATS prefix
                if field_name == 'SERIAL_NUMBER':
                    clean_value = self._normalize_serial_number(clean_value)
                
                device_data[field_name] = clean_value
            else:
                device_data[field_name] = "UNKNOWN"
        
        # Add timestamp (STC will be assigned later during printing)
        device_data['TIMESTAMP'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Note: STC will be assigned during print_device_label_with_save method
        
        logger.info(f"Parsed device data: {device_data}")
        return device_data
    
    def process_streaming_data(self, new_data: str) -> list:
        """
        Process streaming data that might come in chunks.
        Buffers incomplete packets until complete ones are received.
        
        Args:
            new_data (str): New data chunk from serial port
            
        Returns:
            list: List of complete device data dictionaries
        """
        complete_packets = []
        
        # Add new data to buffer
        self.packet_buffer += new_data
        
        # Look for complete packets (##...##)
        while '##' in self.packet_buffer:
            start_pos = self.packet_buffer.find('##')
            if start_pos == -1:
                break
                
            # Look for end marker after start
            end_pos = self.packet_buffer.find('##', start_pos + 2)
            if end_pos == -1:
                # No complete packet yet, keep in buffer
                break
                
            # Extract complete packet
            packet = self.packet_buffer[start_pos:end_pos + 2]
            logger.info(f"Found complete packet: {packet}")
            
            # Try to parse the complete packet
            parsed_data = self.parse_data(packet)
            if parsed_data:
                complete_packets.append(parsed_data)
            
            # Remove processed packet from buffer
            self.packet_buffer = self.packet_buffer[end_pos + 2:]
        
        # Keep buffer manageable (prevent memory issues)
        if len(self.packet_buffer) > 1000:
            logger.warning("Packet buffer too large, clearing old data")
            # Keep only the last 200 characters
            self.packet_buffer = self.packet_buffer[-200:]
        
        return complete_packets
    
    def get_buffered_data(self) -> str:
        """Get current buffered data for debugging."""
        return self.packet_buffer
    
    def clear_buffer(self):
        """Clear the packet buffer."""
        self.packet_buffer = ""
        logger.info("Packet buffer cleared")
    
    def _log_failed_parsing_attempt(self, raw_data: str):
        """Log details about failed parsing attempts for debugging."""
        logger.debug(f"Failed parsing analysis for: '{raw_data}'")
        logger.debug(f"Data length: {len(raw_data)}")
        logger.debug(f"Contains ##: {'##' in raw_data}")
        logger.debug(f"Contains |: {'|' in raw_data}")
        logger.debug(f"Hex representation: {raw_data.encode('utf-8').hex()}")
        
        # Look for potential data segments
        potential_segments = raw_data.split('|')
        if len(potential_segments) >= 5:
            logger.debug(f"Found {len(potential_segments)} pipe-separated segments")
            for i, segment in enumerate(potential_segments[:5]):
                logger.debug(f"Segment {i+1}: '{segment.strip()}'")
        
        # Check for other common separators
        for sep in [',', ';', '\t', ' ']:
            segments = raw_data.split(sep)
            if len(segments) >= 5:
                logger.debug(f"Alternative: {len(segments)} segments with '{sep}' separator")
    
    def _normalize_serial_number(self, serial_number: str) -> str:
        """
        Normalize serial number to just the numeric part (remove ATS prefix).
        
        Args:
            serial_number (str): Raw serial number from data
            
        Returns:
            str: Normalized serial number without ATS prefix
        """
        # Remove any extra spaces
        serial_number = serial_number.strip()
        
        # If starts with ATS, remove it and keep just the numeric part
        if serial_number.upper().startswith('ATS'):
            numeric_part = serial_number[3:].strip()  # Remove 'ATS' prefix
            logger.info(f"Removed ATS prefix: {serial_number} → {numeric_part}")
            return numeric_part
        
        # If it's just numeric, return as is
        if serial_number.isdigit():
            return serial_number
        
        # Extract just the numeric part from any format
        numeric_part = ''.join(filter(str.isdigit, serial_number))
        if numeric_part:
            logger.info(f"Extracted numeric part: {serial_number} → {numeric_part}")
            return numeric_part
        
        # Fallback: keep original if no numeric part found
        logger.warning(f"Could not normalize serial number: {serial_number}")
        return serial_number
    
    def set_pattern(self, pattern: str, field_names: list):
        """
        Set custom regex pattern and field names.
        
        Args:
            pattern (str): Regex pattern string
            field_names (list): List of field names in order
        """
        try:
            self.data_pattern = re.compile(pattern)
            self.field_names = field_names
            logger.info(f"Updated pattern: {pattern}")
            logger.info(f"Field names: {field_names}")
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")


class ZPLTemplate:
    """Handle ZPL template processing with placeholders."""
    
    def __init__(self, template: str):
        """
        Initialize with ZPL template.
        
        Args:
            template (str): ZPL template string with placeholders
        """
        self.template = template
        self.placeholders = self._extract_placeholders()
        logger.info(f"Template loaded with placeholders: {self.placeholders}")
    
    def _extract_placeholders(self) -> list:
        """Extract placeholder names from template."""
        # Look for patterns like {FIELD_NAME} in the template
        placeholder_pattern = re.compile(r'\{([A-Z_]+)\}')
        placeholders = placeholder_pattern.findall(self.template)
        return list(set(placeholders))
    
    def render(self, device_data: Dict[str, str]) -> str:
        """
        Render ZPL template with device data.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            
        Returns:
            str: Rendered ZPL commands
        """
        rendered_zpl = self.template
        
        # Replace placeholders with actual data
        for placeholder in self.placeholders:
            placeholder_pattern = '{' + placeholder + '}'
            value = device_data.get(placeholder, f'MISSING_{placeholder}')
            rendered_zpl = rendered_zpl.replace(placeholder_pattern, value)
        
        return rendered_zpl
    
    def validate_template(self, device_data: Dict[str, str]) -> bool:
        """
        Validate that all required placeholders have data.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            
        Returns:
            bool: True if all placeholders can be filled
        """
        missing_fields = []
        for placeholder in self.placeholders:
            if placeholder not in device_data:
                missing_fields.append(placeholder)
        
        if missing_fields:
            logger.warning(f"Missing data for placeholders: {missing_fields}")
            return False
        
        return True


class SerialPortMonitor:
    """Monitor serial port for device data."""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize serial port monitor.
        
        Args:
            port (str): Serial port name (e.g., 'COM3')
            baudrate (int): Baud rate for serial communication
            timeout (float): Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_running = False
        self.data_callback = None
        
    def set_data_callback(self, callback: Callable[[str], None]):
        """Set callback function for received data."""
        self.data_callback = callback
    
    def connect(self) -> bool:
        """
        Connect to serial port.
        
        Returns:
            bool: True if connection successful
        """
        if not SERIAL_AVAILABLE:
            logger.error("pyserial not available")
            return False
        
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            logger.info(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info(f"Disconnected from {self.port}")
    
    def start_monitoring(self):
        """Start monitoring serial port in a separate thread."""
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Serial port not connected")
            return False
        
        self.is_running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("Serial port monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop monitoring serial port."""
        self.is_running = False
        logger.info("Serial port monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop with enhanced buffering and timeout handling."""
        buffer = ""
        last_data_time = time.time()
        timeout_threshold = 2.0  # Process incomplete data after 2 seconds
        
        while self.is_running:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Read available data
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    data_str = data.decode('utf-8', errors='ignore')
                    buffer += data_str
                    last_data_time = time.time()
                    
                    logger.debug(f"Received data: {repr(data_str)}")
                
                # Process complete lines (handle various line endings)
                lines_processed = False
                for line_ending in ['\n', '\r\n', '\r']:
                    while line_ending in buffer:
                        line, buffer = buffer.split(line_ending, 1)
                        line = line.strip()
                        if line and self.data_callback:
                            logger.debug(f"Processing line: {repr(line)}")
                            self.data_callback(line)
                        lines_processed = True
                
                # Handle timeout - process incomplete data if no new data for a while
                current_time = time.time()
                if not lines_processed and buffer and (current_time - last_data_time) > timeout_threshold:
                    line = buffer.strip()
                    if line and self.data_callback:
                        logger.debug(f"Processing timeout data: {repr(line)}")
                        self.data_callback(line)
                    buffer = ""
                    last_data_time = current_time
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Longer delay on error
    
    @staticmethod
    def list_serial_ports() -> list:
        """List available serial ports."""
        if not SERIAL_AVAILABLE:
            return []
        
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'name': port.name,
                'description': port.description
            })
        return ports


class DeviceAutoPrinter:
    """Main class that coordinates serial monitoring and printing."""
    
    def __init__(self, zpl_template: str, serial_port: str = None, 
                 baudrate: int = 9600, printer_name: str = None, pcb_printer_name: str = None, initial_stc: int = 60000,
                 zpl_output_dir: str = None, csv_file_path: str = None, debug_mode: bool = False):
        """
        Initialize the auto-printer system.
        
        Args:
            zpl_template (str): ZPL template string
            serial_port (str): Serial port name
            baudrate (int): Serial port baud rate
            printer_name (str): Zebra printer name
            initial_stc (int): Starting STC value (default: 60000)
            zpl_output_dir (str): Custom ZPL output directory
            csv_file_path (str): Custom CSV file path
            debug_mode (bool): Enable debug mode (simulates printing without physical printer)
        """
        self.debug_mode = debug_mode
        self.parser = DeviceDataParser()
        self.template = ZPLTemplate(zpl_template)
        self.printer = ZebraZPL(printer_name, debug_mode=debug_mode)
        self.pcb_printer = ZebraZPL(pcb_printer_name, debug_mode=debug_mode) if pcb_printer_name else None
        self.serial_monitor = SerialPortMonitor(serial_port, baudrate) if serial_port else None
        
        # Initialize file paths first
        self.zpl_output_dir = zpl_output_dir or os.path.join("save", "zpl_outputs")
        self.csv_file_path = csv_file_path or os.path.join("save", "csv", "device_log.csv")
        
        # STC counter management (depends on csv_file_path)
        self.current_stc = self._get_next_stc_from_csv(initial_stc)
        self.auto_increment_stc = True
        
        # Pending devices for manual print confirmation
        self.pending_devices = []
        self.device_queue_callback = None
        
        # Create output directories and initialize CSV
        self._create_output_directories()
        self._initialize_csv_file()
        
        # Statistics
        self.stats = {
            'devices_processed': 0,
            'successful_prints': 0,
            'failed_prints': 0,
            'parse_errors': 0,
            'start_time': None
        }
        
        # PCB printing settings
        self.pcb_printing_enabled = True  # Enable PCB printing by default
        self.pcb_stats = {
            'pcb_prints_attempted': 0,
            'pcb_prints_successful': 0,
            'pcb_prints_failed': 0
        }
        
        # Setup data callback
        if self.serial_monitor:
            self.serial_monitor.set_data_callback(self._handle_serial_data)
    
    def _get_next_stc_from_csv(self, fallback_stc: int = 60000) -> int:
        """
        Get the next STC number by reading the latest from CSV file.
        
        Args:
            fallback_stc (int): Fallback STC if CSV is empty or doesn't exist
            
        Returns:
            int: Next STC number to use
        """
        try:
            if not os.path.exists(self.csv_file_path):
                logger.info(f"CSV file doesn't exist, starting with STC {fallback_stc}")
                return fallback_stc
            
            max_stc = 0
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        # Try both 'stc' and 'STC' column names
                        stc_value = row.get('stc') or row.get('STC', '0')
                        if stc_value and stc_value.isdigit():
                            max_stc = max(max_stc, int(stc_value))
                    except (ValueError, TypeError):
                        continue
            
            if max_stc == 0:
                logger.info(f"No valid STC found in CSV, starting with STC {fallback_stc}")
                return fallback_stc
            else:
                next_stc = max_stc + 1
                logger.info(f"Found latest STC {max_stc} in CSV, next STC will be {next_stc}")
                return next_stc
                
        except Exception as e:
            logger.warning(f"Error reading STC from CSV: {e}, using fallback STC {fallback_stc}")
            return fallback_stc
    
    def set_device_queue_callback(self, callback):
        """Set callback for when new devices are added to the queue."""
        self.device_queue_callback = callback
    
    def set_stc_value(self, stc_value: int):
        """Set the current STC value."""
        self.current_stc = stc_value
        logger.info(f"STC value set to: {stc_value}")
    
    def get_next_stc(self) -> int:
        """Get the next STC value and increment if auto-increment is enabled."""
        stc = self.current_stc
        if self.auto_increment_stc:
            self.current_stc += 1
        return stc
    
    def set_auto_increment(self, enabled: bool):
        """Enable or disable auto-increment of STC values."""
        self.auto_increment_stc = enabled
        logger.info(f"STC auto-increment {'enabled' if enabled else 'disabled'}")
    
    def add_device_to_queue(self, device_data: Dict[str, str], raw_data: str) -> int:
        """Add device to pending queue for manual print confirmation. Returns assigned STC."""
        stc_assigned = self.get_next_stc()
        device_entry = {
            'device_data': device_data,
            'raw_data': raw_data,
            'stc_assigned': stc_assigned,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'PENDING'
        }
        self.pending_devices.append(device_entry)
        
        # Notify GUI of new device
        if self.device_queue_callback:
            self.device_queue_callback(device_entry)
        
        logger.info(f"Device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')} added to queue with STC {stc_assigned}")
        return stc_assigned
    
    def print_device_from_queue(self, device_index: int, custom_stc: int = None) -> bool:
        """Print a device from the pending queue."""
        if device_index >= len(self.pending_devices):
            logger.error(f"Invalid device index: {device_index}")
            return False
        
        device_entry = self.pending_devices[device_index]
        device_data = device_entry['device_data'].copy()
        
        # Use custom STC if provided
        if custom_stc is not None:
            device_data['STC'] = str(custom_stc)
        else:
            device_data['STC'] = str(device_entry['stc_assigned'])
        
        # Print the device
        success, zpl_filename, _, pcb_success = self.print_device_label_with_save(device_data, device_entry['raw_data'])
        
        # Update device status
        device_entry['status'] = 'PRINTED' if success else 'FAILED'
        device_entry['actual_stc'] = device_data['STC']
        device_entry['print_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if success:
            self.stats['successful_prints'] += 1
            logger.info(f"Successfully printed device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')} with STC {device_data['STC']}")
        else:
            self.stats['failed_prints'] += 1
            logger.error(f"Failed to print device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
        
        return success
    
    def remove_device_from_queue(self, device_index: int):
        """Remove a device from the pending queue."""
        if device_index < len(self.pending_devices):
            device = self.pending_devices.pop(device_index)
            logger.info(f"Removed device {device['device_data'].get('SERIAL_NUMBER', 'UNKNOWN')} from queue")
    
    def clear_queue(self):
        """Clear all pending devices."""
        self.pending_devices.clear()
        logger.info("Cleared device queue")
    
    def _create_output_directories(self):
        """Create output directories if they don't exist."""
        try:
            if not os.path.exists(self.zpl_output_dir):
                os.makedirs(self.zpl_output_dir)
                logger.info(f"Created ZPL output directory: {self.zpl_output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {e}")
    
    def _initialize_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            # Check if CSV file exists
            file_exists = os.path.exists(self.csv_file_path)
            
            if not file_exists:
                # Ensure save directory exists
                save_dir = os.path.dirname(self.csv_file_path)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                    logger.info(f"Created save directory: {save_dir}")
                
                # Create CSV file with headers (matching GUI format)
                headers = [
                    'STC',
                    'SERIAL_NUMBER', 
                    'IMEI',
                    'IMSI',
                    'CCID',
                    'MAC_ADDRESS',
                    'STATUS',
                    'TIMESTAMP'
                ]
                
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                
                logger.info(f"Created CSV log file: {self.csv_file_path}")
            else:
                logger.info(f"Using existing CSV log file: {self.csv_file_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize CSV file: {e}")
    
    def _save_zpl_file(self, device_data: Dict[str, str], zpl_commands: str) -> str:
        """
        Save ZPL commands to a file named with the serial number.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            zpl_commands (str): ZPL command string
            
        Returns:
            str: Filename of saved ZPL file
        """
        try:
            serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{serial_number}_{timestamp}.zpl"
            filepath = os.path.join(self.zpl_output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(zpl_commands)
            
            logger.info(f"Saved ZPL file: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save ZPL file: {e}")
            return ""
    
    def _log_to_csv(self, device_data: Dict[str, str], print_status: str, 
                    zpl_filename: str, raw_data: str):
        """
        Log device information to CSV file.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            print_status (str): Print status (SUCCESS/FAILED)
            zpl_filename (str): Name of saved ZPL file
            raw_data (str): Original raw data from serial port
        """
        try:
            # CSV format to match GUI expectations: 
            # timestamp, stc, serial_number, imei, imsi, ccid, mac_address, print_status, parse_status, raw_data, zpl_filename, notes
            row_data = [
                device_data.get('TIMESTAMP', ''),
                device_data.get('STC', ''),
                device_data.get('SERIAL_NUMBER', ''),
                device_data.get('IMEI', ''),
                device_data.get('IMSI', ''),
                device_data.get('CCID', ''),
                device_data.get('MAC_ADDRESS', ''),
                'Printed' if print_status.startswith('SUCCESS') else 'Error',
                'Parsed',
                raw_data,
                zpl_filename,
                ''  # notes column
            ]
            
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_data)
            
            logger.debug(f"Logged device data to CSV: {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")
    
    def _handle_serial_data(self, raw_data: str):
        """Handle incoming serial data. Returns (device_data, stc_assigned, pcb_success) if successful, None if failed."""
        logger.info(f"Received data: {raw_data}")
        
        # Parse device data
        device_data = self.parser.parse_data(raw_data)
        if not device_data:
            self.stats['parse_errors'] += 1
            # Don't log parse errors to CSV - only log valid device data
            logger.warning(f"No valid data pattern found in: {raw_data}")
            return None
        
        self.stats['devices_processed'] += 1
        
        # Print label and save files immediately
        success, zpl_filename, stc_assigned, pcb_success = self.print_device_label_with_save(device_data, raw_data)
        if success:
            self.stats['successful_prints'] += 1
            # Return device data, STC, and PCB status for GUI display
            return device_data, stc_assigned, pcb_success
        else:
            self.stats['failed_prints'] += 1
            return None
        
        # Log statistics
        self._log_stats()
    
    def print_device_label_with_save(self, device_data: Dict[str, str], raw_data: str) -> tuple:
        """
        Print label for device data and save ZPL file and CSV log.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            raw_data (str): Original raw data from serial port
            
        Returns:
            tuple: (success: bool, zpl_filename: str, stc_assigned: str, pcb_success: bool)
        """
        zpl_filename = ""
        print_status = "FAILED"
        stc_assigned = ""
        
        try:
            # Assign STC value if not already present
            if 'STC' not in device_data or not device_data['STC']:
                stc_assigned = str(self.get_next_stc())
                device_data['STC'] = stc_assigned
            else:
                stc_assigned = device_data['STC']
            
            # Validate template
            if not self.template.validate_template(device_data):
                logger.error("Template validation failed")
                print_status = "TEMPLATE_ERROR"
                self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
                return False, zpl_filename, stc_assigned, False
            
            # Render ZPL
            zpl_commands = self.template.render(device_data)
            logger.debug(f"Rendered ZPL:\n{zpl_commands}")
            
            # Save ZPL file
            zpl_filename = self._save_zpl_file(device_data, zpl_commands)
            
            # Print main label on Zebra/XPrinter
            success = self.printer.send_zpl(zpl_commands)
            
            # PCB printing functionality
            pcb_success = False
            if self.pcb_printing_enabled and self.pcb_printer:
                try:
                    # Create PCB label data using TSPL
                    pcb_data = self._create_pcb_label_data(device_data)
                    logger.info(f"PCB TSPL data created: {pcb_data}")
                    
                    # Use TSPL for XPrinter instead of ZPL
                    pcb_success = self.pcb_printer.send_tspl(pcb_data)
                    
                    self.pcb_stats['pcb_prints_attempted'] += 1
                    if pcb_success:
                        self.pcb_stats['pcb_prints_successful'] += 1
                        logger.info(f"Successfully printed PCB label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
                    else:
                        self.pcb_stats['pcb_prints_failed'] += 1
                        logger.error(f"Failed to print PCB label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
                        
                except Exception as e:
                    self.pcb_stats['pcb_prints_failed'] += 1
                    logger.error(f"Error printing PCB label: {e}")
                    pcb_success = False
            elif self.pcb_printing_enabled:
                logger.warning("PCB printing enabled but no PCB printer configured")
            else:
                logger.debug("PCB printing is disabled")
            
            if success:
                print_status = "SUCCESS"
                logger.info(f"Successfully printed label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            else:
                print_status = "PRINT_FAILED"
                logger.error(f"Failed to print label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            
            # Log to CSV
            self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
            
            return success, zpl_filename, stc_assigned, pcb_success
            
        except Exception as e:
            logger.error(f"Error printing device label: {e}")
            print_status = f"ERROR: {str(e)}"
            self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
            return False, zpl_filename, stc_assigned, False
    
    def _create_pcb_label_data(self, device_data: Dict[str, str]) -> str:
        """
        Create PCB label data using TSPL commands for XPrinter XP-470B.
        40mm x 20mm label size using TSPL (TSC Printer Language)
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            
        Returns:
            str: TSPL commands optimized for XPrinter XP-470B
        """
        # Extract essential data
        serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
        stc = device_data.get('STC', 'UNKNOWN')
        
        # TSPL commands for 40mm x 20mm label - EXTRA LARGE FONTS WITH SCALING
        # Using font scaling to make text even bigger than Font "5"
        tspl_commands = f"""SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 70, 40, "5", 0, 2, 2, "{serial_number}"
TEXT 80, 90, "5", 0, 2, 2, "STC: {stc}"
PRINT 1, 1
"""
        
        return tspl_commands
    
    def print_device_label(self, device_data: Dict[str, str]) -> bool:
        """
        Print label for device data (legacy method for compatibility).
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            
        Returns:
            bool: True if printing successful
        """
        success, _, _, _ = self.print_device_label_with_save(device_data, "")
        return success
    
    def start(self) -> bool:
        """Start the auto-printer system."""
        if not self.printer.printer_name:
            logger.error("No Zebra printer found")
            return False
        
        if self.serial_monitor:
            if not self.serial_monitor.connect():
                logger.error("Failed to connect to serial port")
                return False
            
            if not self.serial_monitor.start_monitoring():
                logger.error("Failed to start serial monitoring")
                return False
        
        self.stats['start_time'] = datetime.now()
        logger.info("Device auto-printer system started")
        return True
    
    def stop(self):
        """Stop the auto-printer system."""
        if self.serial_monitor:
            self.serial_monitor.stop_monitoring()
            self.serial_monitor.disconnect()
        
        logger.info("Device auto-printer system stopped")
        self._log_final_stats()
    
    def set_pcb_printer(self, pcb_printer_name: str):
        """Set the PCB printer."""
        if pcb_printer_name:
            self.pcb_printer = ZebraZPL(pcb_printer_name, debug_mode=self.debug_mode)
            logger.info(f"PCB printer set to: {pcb_printer_name}")
        else:
            self.pcb_printer = None
            logger.info("PCB printer disabled")
    
    def enable_pcb_printing(self, enabled: bool):
        """Enable or disable PCB printing."""
        self.pcb_printing_enabled = enabled
        logger.info(f"PCB printing {'enabled' if enabled else 'disabled'}")
    
    def get_pcb_stats(self) -> Dict[str, int]:
        """Get PCB printing statistics."""
        return self.pcb_stats.copy()
    
    def _log_stats(self):
        """Log current statistics."""
        logger.info(f"Stats - Processed: {self.stats['devices_processed']}, "
                   f"Printed: {self.stats['successful_prints']}, "
                   f"Failed: {self.stats['failed_prints']}, "
                   f"Parse Errors: {self.stats['parse_errors']}")
    
    def _log_final_stats(self):
        """Log final statistics."""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            logger.info(f"Final Stats - Runtime: {runtime}, "
                       f"Total Processed: {self.stats['devices_processed']}, "
                       f"Success Rate: {self.stats['successful_prints']}/{self.stats['devices_processed']} "
                       f"({100 * self.stats['successful_prints'] / max(1, self.stats['devices_processed']):.1f}%)")

    def enable_pcb_printing(self, enabled: bool = True):
        """Enable or disable PCB printing."""
        self.pcb_printing_enabled = enabled
        logger.info(f"PCB printing {'enabled' if enabled else 'disabled'}")
    
    def get_pcb_stats(self):
        """Get PCB printing statistics."""
        return {'pcb_prints_attempted': 0, 'pcb_prints_successful': 0, 'pcb_prints_failed': 0}


# Your specific ZPL template with placeholders
DEFAULT_ZPL_TEMPLATE = """^XA
^PW399
^LL240
^CI28
^MD15
~SD15

^FO20,50^BQN,2,4
^FDLA,STC:{STC};SN:ATS{SERIAL_NUMBER};IMEI:{IMEI};IMSI:{IMSI};CCID:{CCID};MAC:{MAC_ADDRESS}^FS

^CF0,18,18
^FO185,32.5^FDSTC:^FS
^FO185,70^FDS/N:^FS
^FO185,107.5^FDIMEI:^FS
^FO185,145^FDIMSI:^FS
^FO185,182.5^FDCCID:^FS
^FO185,220^FDMAC:^FS

^CF0,22,16
^FO225,32.5^FD{STC}^FS
^FO225,70^FD{SERIAL_NUMBER}^FS
^FO225,107.5^FD{IMEI}^FS
^FO225,145^FD{IMSI}^FS
^FO225,182.5^FD{CCID}^FS
^FO225,220^FD{MAC_ADDRESS}^FS

^XZ
"""


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-print device labels from serial port data')
    parser.add_argument('--port', '-p', help='Serial port (e.g., COM3)')
    parser.add_argument('--baudrate', '-b', type=int, default=9600, help='Baud rate (default: 9600)')
    parser.add_argument('--printer', help='Printer name (will auto-detect if not specified)')
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports')
    parser.add_argument('--list-printers', action='store_true', help='List available printers')
    parser.add_argument('--test-data', help='Test with sample data instead of serial port')
    parser.add_argument('--template-file', help='Load ZPL template from file')
    
    args = parser.parse_args()
    
    if args.list_ports:
        print("Available serial ports:")
        ports = SerialPortMonitor.list_serial_ports()
        for port in ports:
            print(f"  {port['device']} - {port['description']}")
        return
    
    if args.list_printers:
        printer = ZebraZPL()
        print("Available printers:")
        for p in printer.list_printers():
            marker = " <- Zebra" if any(x in p.lower() for x in ['zebra', 'gc420', 'zdesigner']) else ""
            print(f"  {p}{marker}")
        return
    
    # Load template
    template = DEFAULT_ZPL_TEMPLATE
    if args.template_file:
        try:
            with open(args.template_file, 'r') as f:
                template = f.read()
            print(f"Loaded template from {args.template_file}")
        except FileNotFoundError:
            print(f"Template file not found: {args.template_file}")
            return
    
    # Create auto-printer
    auto_printer = DeviceAutoPrinter(
        zpl_template=template,
        serial_port=args.port,
        baudrate=args.baudrate,
        printer_name=args.printer
    )
    
    # Test mode
    if args.test_data:
        print(f"Testing with data: {args.test_data}")
        auto_printer._handle_serial_data(args.test_data)
        return
    
    if not args.port:
        print("Error: Serial port required. Use --port or --list-ports")
        return
    
    # Start the system
    try:
        if auto_printer.start():
            print(f"Auto-printer started. Monitoring {args.port} for device data...")
            print("Press Ctrl+C to stop")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping auto-printer...")
    finally:
        auto_printer.stop()


if __name__ == "__main__":
    main()