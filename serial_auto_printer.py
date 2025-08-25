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
        # Default regex pattern for the specified data format
        # ##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
        self.data_pattern = re.compile(
            r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##'
        )
        
        # Field mapping
        self.field_names = [
            'SERIAL_NUMBER',
            'IMEI', 
            'IMSI',
            'CCID',
            'MAC_ADDRESS'
        ]
    
    def parse_data(self, raw_data: str) -> Optional[Dict[str, str]]:
        """
        Parse device data from raw serial input.
        
        Args:
            raw_data (str): Raw data from serial port
            
        Returns:
            Dict[str, str]: Parsed device data or None if no match
        """
        # Clean the data
        raw_data = raw_data.strip()
        
        # Try to find the pattern
        match = self.data_pattern.search(raw_data)
        if not match:
            logger.warning(f"No valid data pattern found in: {raw_data}")
            return None
        
        # Extract values
        values = match.groups()
        if len(values) != len(self.field_names):
            logger.error(f"Expected {len(self.field_names)} fields, got {len(values)}")
            return None
        
        # Create device data dictionary
        device_data = {}
        for i, field_name in enumerate(self.field_names):
            device_data[field_name] = values[i]
        
        # Add timestamp and default STC
        device_data['TIMESTAMP'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        device_data['STC'] = '6000'  # Default STC value as mentioned
        
        logger.info(f"Parsed device data: {device_data}")
        return device_data
    
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
        
        # Also replace direct field references (without braces) for your specific template
        for field_name, value in device_data.items():
            rendered_zpl = rendered_zpl.replace(field_name, value)
        
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
        """Main monitoring loop."""
        buffer = ""
        
        while self.is_running:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Read available data
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    data_str = data.decode('utf-8', errors='ignore')
                    buffer += data_str
                    
                    # Process complete lines
                    while '\n' in buffer or '\r' in buffer:
                        if '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        else:
                            line, buffer = buffer.split('\r', 1)
                        
                        line = line.strip()
                        if line and self.data_callback:
                            self.data_callback(line)
                
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
                 baudrate: int = 9600, printer_name: str = None):
        """
        Initialize the auto-printer system.
        
        Args:
            zpl_template (str): ZPL template string
            serial_port (str): Serial port name
            baudrate (int): Serial port baud rate
            printer_name (str): Zebra printer name
        """
        self.parser = DeviceDataParser()
        self.template = ZPLTemplate(zpl_template)
        self.printer = ZebraZPL(printer_name)
        self.serial_monitor = SerialPortMonitor(serial_port, baudrate) if serial_port else None
        
        # Create output directories
        self.zpl_output_dir = "zpl_outputs"
        self.csv_file_path = "device_log.csv"
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
        
        # Setup data callback
        if self.serial_monitor:
            self.serial_monitor.set_data_callback(self._handle_serial_data)
    
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
                # Create CSV file with headers
                headers = [
                    'timestamp',
                    'serial_number', 
                    'imei',
                    'imsi',
                    'ccid',
                    'mac_address',
                    'stc',
                    'print_status',
                    'zpl_file',
                    'raw_data'
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
            row_data = [
                device_data.get('TIMESTAMP', ''),
                device_data.get('SERIAL_NUMBER', ''),
                device_data.get('IMEI', ''),
                device_data.get('IMSI', ''),
                device_data.get('CCID', ''),
                device_data.get('MAC_ADDRESS', ''),
                device_data.get('STC', ''),
                print_status,
                zpl_filename,
                raw_data.strip()
            ]
            
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_data)
            
            logger.debug(f"Logged device data to CSV: {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")
    
    def _handle_serial_data(self, raw_data: str):
        """Handle incoming serial data."""
        logger.info(f"Received data: {raw_data}")
        
        # Parse device data
        device_data = self.parser.parse_data(raw_data)
        if not device_data:
            self.stats['parse_errors'] += 1
            # Log parse error to CSV
            self._log_to_csv({
                'TIMESTAMP': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'SERIAL_NUMBER': 'PARSE_ERROR',
                'IMEI': '',
                'IMSI': '',
                'CCID': '',
                'MAC_ADDRESS': '',
                'STC': ''
            }, 'PARSE_ERROR', '', raw_data)
            return
        
        self.stats['devices_processed'] += 1
        
        # Print label and save files
        success, zpl_filename = self.print_device_label_with_save(device_data, raw_data)
        if success:
            self.stats['successful_prints'] += 1
        else:
            self.stats['failed_prints'] += 1
        
        # Log statistics
        self._log_stats()
    
    def print_device_label_with_save(self, device_data: Dict[str, str], raw_data: str) -> tuple:
        """
        Print label for device data and save ZPL file and CSV log.
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            raw_data (str): Original raw data from serial port
            
        Returns:
            tuple: (success: bool, zpl_filename: str)
        """
        zpl_filename = ""
        print_status = "FAILED"
        
        try:
            # Validate template
            if not self.template.validate_template(device_data):
                logger.error("Template validation failed")
                print_status = "TEMPLATE_ERROR"
                self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
                return False, zpl_filename
            
            # Render ZPL
            zpl_commands = self.template.render(device_data)
            logger.debug(f"Rendered ZPL:\n{zpl_commands}")
            
            # Save ZPL file
            zpl_filename = self._save_zpl_file(device_data, zpl_commands)
            
            # Print
            success = self.printer.send_zpl(zpl_commands)
            
            if success:
                print_status = "SUCCESS"
                logger.info(f"Successfully printed label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            else:
                print_status = "PRINT_FAILED"
                logger.error(f"Failed to print label for device {device_data.get('SERIAL_NUMBER', 'UNKNOWN')}")
            
            # Log to CSV
            self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
            
            return success, zpl_filename
            
        except Exception as e:
            logger.error(f"Error printing device label: {e}")
            print_status = f"ERROR: {str(e)}"
            self._log_to_csv(device_data, print_status, zpl_filename, raw_data)
            return False, zpl_filename
    
    def print_device_label(self, device_data: Dict[str, str]) -> bool:
        """
        Print label for device data (legacy method for compatibility).
        
        Args:
            device_data (Dict[str, str]): Device data dictionary
            
        Returns:
            bool: True if printing successful
        """
        success, _ = self.print_device_label_with_save(device_data, "")
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


# Your specific ZPL template with placeholders
DEFAULT_ZPL_TEMPLATE = """^XA
^PW399
^LL240
^CI28
^MD15
~SD15

^FO0,25^BQN,2,4
^FDLA,STC:{STC};SN:{SERIAL_NUMBER};IMEI:{IMEI};IMSI:{IMSI};CCID:{CCID};MAC:{MAC_ADDRESS}^FS

^CF0,18,18
^FO155,2.5^FDSTC:^FS
^FO155,40^FDS/N:^FS
^FO155,77.5^FDIMEI:^FS
^FO155,115^FDIMSI:^FS
^FO155,152.5^FDCCID:^FS
^FO155,190^FDMAC:^FS

^CF0,22,16
^FO195,2.5^FD{STC}^FS
^FO195,40^FD{SERIAL_NUMBER}^FS
^FO195,77.5^FD{IMEI}^FS
^FO195,115^FD{IMSI}^FS
^FO195,152.5^FD{CCID}^FS
^FO195,190^FD{MAC_ADDRESS}^FS

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