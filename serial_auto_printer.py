#!/usr/bin/env python3
"""
Optimized Serial Port Auto-Printer for XPrinter XP-470B
========================================================

This module monitors a serial port for device data and automatically prints
labels using ZPL templates and TSPL commands for PCB labels.

Data Format Expected: ##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
Fields: ##SERIAL_NUMBER|IMEI|IMSI|CCID|MAC_ADDRESS##

Features:
- Serial port monitoring with robust parsing
- Automatic ZPL template processing
- PCB label printing using TSPL commands
- Real-time data logging to CSV
- Queue management for manual printing

Author: Optimized Serial Auto-Printer
Date: October 2025
"""

import os
import re
import time
import logging
import threading
import csv
from typing import Dict, Optional, Callable, List
from datetime import datetime

# Optional imports with graceful fallback
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
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
    """Optimized device data parser with simplified regex patterns."""
    
    def __init__(self):
        self.packet_buffer = ""
        
        # Primary pattern for complete 5-field data
        self.primary_pattern = re.compile(
            r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\s*\|([0-9A-F]+)\|([A-F0-9:]+)##'
        )
        
        # Single flexible pattern for incomplete data
        self.flexible_pattern = re.compile(
            r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)(?:\s*\|([0-9A-F]*))?\|?([A-F0-9:]*)?##?'
        )
        
        self.field_names = ['SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS']
    
    def _clean_data(self, data: str) -> str:
        """Simplified data cleaning - remove non-printable characters."""
        # Keep only alphanumeric, space, and essential punctuation
        cleaned = ''.join(char for char in data 
                         if char.isalnum() or char in ' #|:-')
        return cleaned.strip()

    def parse_data(self, raw_data: str) -> Optional[Dict[str, str]]:
        """Parse device data from raw serial input."""
        raw_data = self._clean_data(raw_data)
        logger.info(f"Parsing: {raw_data}")
        
        # Try primary pattern first
        match = self.primary_pattern.search(raw_data)
        if not match:
            # Try flexible pattern for incomplete data
            match = self.flexible_pattern.search(raw_data)
        
        if not match:
            logger.warning(f"No valid pattern found: {raw_data}")
            return None
        
        # Extract and pad values
        values = [v or "" for v in match.groups()]
        
        # Pad missing fields with defaults
        while len(values) < 5:
            if len(values) == 3:
                values.extend(["UNKNOWN_CCID", "00:00:00:00:00:00"])
            elif len(values) == 4:
                values.append("00:00:00:00:00:00")
            else:
                values.append("UNKNOWN")
        
        # Create device data dictionary
        device_data = {}
        for i, field_name in enumerate(self.field_names):
            value = values[i].strip()
            # Remove ATS prefix from serial number
            if field_name == 'SERIAL_NUMBER' and value.upper().startswith('ATS'):
                value = value[3:].strip()
            device_data[field_name] = value
        
        device_data['TIMESTAMP'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Parsed: {device_data['SERIAL_NUMBER']}")
        return device_data
    
    def process_streaming_data(self, new_data: str) -> List[Dict[str, str]]:
        """Process streaming data with packet buffering."""
        complete_packets = []
        self.packet_buffer += new_data
        
        # Extract complete packets
        while '##' in self.packet_buffer:
            start_pos = self.packet_buffer.find('##')
            if start_pos == -1:
                break
                
            end_pos = self.packet_buffer.find('##', start_pos + 2)
            if end_pos == -1:
                break
                
            packet = self.packet_buffer[start_pos:end_pos + 2]
            parsed_data = self.parse_data(packet)
            if parsed_data:
                complete_packets.append(parsed_data)
            
            self.packet_buffer = self.packet_buffer[end_pos + 2:]
        
        # Prevent buffer overflow
        if len(self.packet_buffer) > 500:
            self.packet_buffer = self.packet_buffer[-200:]
        
        return complete_packets


class ZPLTemplate:
    """Simplified ZPL template handler."""
    
    def __init__(self, template: str):
        self.template = template
        self.placeholders = re.findall(r'\{([A-Z_]+)\}', template)
        logger.info(f"Template loaded with placeholders: {self.placeholders}")
    
    def render(self, device_data: Dict[str, str]) -> str:
        """Render ZPL template with device data."""
        rendered = self.template
        for placeholder in self.placeholders:
            value = device_data.get(placeholder, f'MISSING_{placeholder}')
            rendered = rendered.replace(f'{{{placeholder}}}', value)
        return rendered
    
    def validate_template(self, device_data: Dict[str, str]) -> bool:
        """Validate that all required placeholders have data."""
        missing = [p for p in self.placeholders if p not in device_data]
        if missing:
            logger.warning(f"Missing data: {missing}")
            return False
        return True


class SerialPortMonitor:
    """Simplified serial port monitor."""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_running = False
        self.data_callback = None
        
    def set_data_callback(self, callback: Callable[[str], None]):
        self.data_callback = callback
    
    def connect(self) -> bool:
        """Connect to serial port."""
        if not SERIAL_AVAILABLE:
            logger.error("pyserial not available")
            return False
        
        try:
            self.serial_connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout,
                bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            logger.info(f"Connected to {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Serial connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info(f"Disconnected from {self.port}")
    
    def start_monitoring(self) -> bool:
        """Start monitoring in background thread."""
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Serial port not connected")
            return False
        
        self.is_running = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Serial monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_running = False
    
    def _monitor_loop(self):
        """Optimized monitoring loop."""
        buffer = ""
        last_data_time = time.time()
        
        while self.is_running:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    data_str = data.decode('utf-8', errors='ignore')
                    buffer += data_str
                    last_data_time = time.time()
                
                # Process complete lines
                for line_ending in ['\n', '\r\n', '\r']:
                    while line_ending in buffer:
                        line, buffer = buffer.split(line_ending, 1)
                        if line.strip() and self.data_callback:
                            self.data_callback(line.strip())
                
                # Handle timeout for incomplete data
                if buffer and (time.time() - last_data_time) > 2.0:
                    if self.data_callback:
                        self.data_callback(buffer.strip())
                    buffer = ""
                    last_data_time = time.time()
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(1)
    
    @staticmethod
    def list_serial_ports() -> List[Dict[str, str]]:
        """List available serial ports."""
        if not SERIAL_AVAILABLE:
            return []
        
        return [{'device': port.device, 'name': port.name, 'description': port.description}
                for port in serial.tools.list_ports.comports()]


class DeviceAutoPrinter:
    """Optimized main auto-printer class."""
    
    def __init__(self, zpl_template: str, serial_port: str = None, 
                 baudrate: int = 9600, printer_name: str = None, 
                 pcb_printer_name: str = None, initial_stc: int = 60000,
                 zpl_output_dir: str = None, csv_file_path: str = None, 
                 debug_mode: bool = False):
        
        self.debug_mode = debug_mode
        self.parser = DeviceDataParser()
        self.template = ZPLTemplate(zpl_template)
        self.printer = ZebraZPL(printer_name, debug_mode=debug_mode)
        self.pcb_printer = ZebraZPL(pcb_printer_name, debug_mode=debug_mode) if pcb_printer_name else None
        self.serial_monitor = SerialPortMonitor(serial_port, baudrate) if serial_port else None
        
        # File paths
        self.zpl_output_dir = zpl_output_dir or os.path.join("save", "zpl_outputs")
        self.csv_file_path = csv_file_path or os.path.join("save", "csv", "device_log.csv")
        
        # STC management
        self.current_stc = self._get_next_stc_from_csv(initial_stc)
        self.auto_increment_stc = True
        
        # Queue management
        self.pending_devices = []
        self.device_queue_callback = None
        
        # Statistics
        self.stats = {
            'devices_processed': 0, 'successful_prints': 0, 'failed_prints': 0,
            'parse_errors': 0, 'start_time': None
        }
        
        # PCB settings
        self.pcb_printing_enabled = True
        self.pcb_stats = {
            'pcb_prints_attempted': 0, 'pcb_prints_successful': 0, 'pcb_prints_failed': 0
        }
        
        # Initialize
        self._ensure_directories()
        self._initialize_csv()
        if self.serial_monitor:
            self.serial_monitor.set_data_callback(self._handle_serial_data)
    
    def _get_next_stc_from_csv(self, fallback_stc: int = 60000) -> int:
        """Get next STC from CSV history."""
        try:
            if not os.path.exists(self.csv_file_path):
                return fallback_stc
            
            max_stc = 0
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stc_value = row.get('stc') or row.get('STC', '0')
                    if stc_value.isdigit():
                        max_stc = max(max_stc, int(stc_value))
            
            return max_stc + 1 if max_stc > 0 else fallback_stc
                
        except Exception as e:
            logger.warning(f"Error reading STC from CSV: {e}")
            return fallback_stc
    
    def _ensure_directories(self):
        """Create required directories."""
        for directory in [self.zpl_output_dir, os.path.dirname(self.csv_file_path)]:
            os.makedirs(directory, exist_ok=True)
    
    def _initialize_csv(self):
        """Initialize CSV with headers if needed."""
        if not os.path.exists(self.csv_file_path):
            headers = ['STC', 'SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS', 'STATUS', 'TIMESTAMP']
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv.writer(csvfile).writerow(headers)
            logger.info(f"Created CSV file: {self.csv_file_path}")
    
    def get_next_stc(self) -> int:
        """Get next STC and increment if enabled."""
        stc = self.current_stc
        if self.auto_increment_stc:
            self.current_stc += 1
        return stc
    
    def set_stc_value(self, stc_value: int):
        """Set current STC value."""
        self.current_stc = stc_value
        logger.info(f"STC set to: {stc_value}")
    
    def set_auto_increment(self, enabled: bool):
        """Enable/disable STC auto-increment."""
        self.auto_increment_stc = enabled
    
    def set_device_queue_callback(self, callback):
        """Set callback for queue updates."""
        self.device_queue_callback = callback
    
    def add_device_to_queue(self, device_data: Dict[str, str], raw_data: str) -> int:
        """Add device to queue and return assigned STC."""
        stc_assigned = self.get_next_stc()
        device_entry = {
            'device_data': device_data, 'raw_data': raw_data,
            'stc_assigned': stc_assigned, 'status': 'PENDING',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.pending_devices.append(device_entry)
        
        if self.device_queue_callback:
            self.device_queue_callback(device_entry)
        
        logger.info(f"Device {device_data.get('SERIAL_NUMBER')} queued with STC {stc_assigned}")
        return stc_assigned
    
    def print_device_from_queue(self, device_index: int, custom_stc: int = None) -> bool:
        """Print device from queue."""
        if device_index >= len(self.pending_devices):
            return False
        
        device_entry = self.pending_devices[device_index]
        device_data = device_entry['device_data'].copy()
        device_data['STC'] = str(custom_stc or device_entry['stc_assigned'])
        
        success, _, _, pcb_success = self.print_device_label_with_save(device_data, device_entry['raw_data'])
        device_entry['status'] = 'PRINTED' if success else 'FAILED'
        
        if success:
            self.stats['successful_prints'] += 1
        else:
            self.stats['failed_prints'] += 1
        
        return success
    
    def clear_queue(self):
        """Clear device queue."""
        self.pending_devices.clear()
    
    def _save_zpl_file(self, device_data: Dict[str, str], zpl_commands: str) -> str:
        """Save ZPL commands to file."""
        try:
            serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{serial_number}_{timestamp}.zpl"
            filepath = os.path.join(self.zpl_output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(zpl_commands)
            
            return filename
        except Exception as e:
            logger.error(f"ZPL save error: {e}")
            return ""
    
    def _log_to_csv(self, device_data: Dict[str, str], print_status: str, 
                    zpl_filename: str, raw_data: str):
        """Log to CSV file."""
        try:
            row_data = [
                device_data.get('TIMESTAMP', ''),
                device_data.get('STC', ''),
                device_data.get('SERIAL_NUMBER', ''),
                device_data.get('IMEI', ''),
                device_data.get('IMSI', ''),
                device_data.get('CCID', ''),
                device_data.get('MAC_ADDRESS', ''),
                'Printed' if print_status.startswith('SUCCESS') else 'Error',
                'Parsed', raw_data, zpl_filename, ''
            ]
            
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                csv.writer(csvfile).writerow(row_data)
                
        except Exception as e:
            logger.error(f"CSV log error: {e}")
    
    def _handle_serial_data(self, raw_data: str):
        """Handle incoming serial data."""
        logger.info(f"Received: {raw_data}")
        
        device_data = self.parser.parse_data(raw_data)
        if not device_data:
            self.stats['parse_errors'] += 1
            return None
        
        self.stats['devices_processed'] += 1
        success, _, stc_assigned, pcb_success = self.print_device_label_with_save(device_data, raw_data)
        
        if success:
            self.stats['successful_prints'] += 1
            return device_data, stc_assigned, pcb_success
        else:
            self.stats['failed_prints'] += 1
            return None
    
    def print_device_label_with_save(self, device_data: Dict[str, str], raw_data: str) -> tuple:
        """Print label and save files."""
        try:
            # Assign STC if needed
            if 'STC' not in device_data or not device_data['STC']:
                stc_assigned = str(self.get_next_stc())
                device_data['STC'] = stc_assigned
            else:
                stc_assigned = device_data['STC']
            
            # Validate and render template
            if not self.template.validate_template(device_data):
                self._log_to_csv(device_data, "TEMPLATE_ERROR", "", raw_data)
                return False, "", stc_assigned, False
            
            zpl_commands = self.template.render(device_data)
            zpl_filename = self._save_zpl_file(device_data, zpl_commands)
            
            # Print main label
            success = self.printer.send_zpl(zpl_commands)
            
            # Print PCB label
            pcb_success = False
            if self.pcb_printing_enabled and self.pcb_printer:
                try:
                    pcb_data = self._create_pcb_label_data(device_data)
                    pcb_success = self.pcb_printer.send_tspl(pcb_data)
                    
                    self.pcb_stats['pcb_prints_attempted'] += 1
                    if pcb_success:
                        self.pcb_stats['pcb_prints_successful'] += 1
                    else:
                        self.pcb_stats['pcb_prints_failed'] += 1
                        
                except Exception as e:
                    logger.error(f"PCB print error: {e}")
                    self.pcb_stats['pcb_prints_failed'] += 1
            
            # Log results
            status = "SUCCESS" if success else "PRINT_FAILED"
            self._log_to_csv(device_data, status, zpl_filename, raw_data)
            
            if success:
                logger.info(f"Printed: {device_data.get('SERIAL_NUMBER')}")
            
            return success, zpl_filename, stc_assigned, pcb_success
            
        except Exception as e:
            logger.error(f"Print error: {e}")
            self._log_to_csv(device_data, f"ERROR: {e}", "", raw_data)
            return False, "", "", False
    
    def _create_pcb_label_data(self, device_data: Dict[str, str]) -> str:
        """Create optimized PCB label using TSPL."""
        serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
        stc = device_data.get('STC', 'UNKNOWN')
        
        return f"""SIZE 40 mm, 20 mm
GAP 2 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 100, 55, "2", 0, 2, 2, "{serial_number}"
TEXT 100, 105, "2", 0, 2, 2, "STC:{stc}"
PRINT 1, 1
"""
    
    def start(self) -> bool:
        """Start the auto-printer system."""
        if not self.printer.printer_name:
            logger.error("No printer found")
            return False
        
        if self.serial_monitor:
            if not self.serial_monitor.connect() or not self.serial_monitor.start_monitoring():
                logger.error("Serial monitor failed to start")
                return False
        
        self.stats['start_time'] = datetime.now()
        logger.info("Auto-printer started")
        return True
    
    def stop(self):
        """Stop the auto-printer system."""
        if self.serial_monitor:
            self.serial_monitor.stop_monitoring()
            self.serial_monitor.disconnect()
        logger.info("Auto-printer stopped")
    
    def set_pcb_printer(self, pcb_printer_name: str):
        """Set PCB printer."""
        self.pcb_printer = ZebraZPL(pcb_printer_name, debug_mode=self.debug_mode) if pcb_printer_name else None
    
    def enable_pcb_printing(self, enabled: bool):
        """Enable/disable PCB printing."""
        self.pcb_printing_enabled = enabled
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        return self.stats.copy()
    
    def get_pcb_stats(self) -> Dict:
        """Get PCB printing statistics."""
        return self.pcb_stats.copy()




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
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-print device labels from serial port data')
    parser.add_argument('--port', '-p', help='Serial port (e.g., COM3)')
    parser.add_argument('--baudrate', '-b', type=int, default=9600, help='Baud rate')
    parser.add_argument('--printer', help='Printer name')
    parser.add_argument('--list-ports', action='store_true', help='List serial ports')
    parser.add_argument('--list-printers', action='store_true', help='List printers')
    parser.add_argument('--test-data', help='Test with sample data')
    
    args = parser.parse_args()
    
    if args.list_ports:
        print("Available serial ports:")
        for port in SerialPortMonitor.list_serial_ports():
            print(f"  {port['device']} - {port['description']}")
        return
    
    if args.list_printers:
        printer = ZebraZPL()
        print("Available printers:")
        for p in printer.list_printers():
            print(f"  {p}")
        return
    
    # Create and run auto-printer
    auto_printer = DeviceAutoPrinter(
        zpl_template=DEFAULT_ZPL_TEMPLATE,
        serial_port=args.port,
        baudrate=args.baudrate,
        printer_name=args.printer
    )
    
    if args.test_data:
        print(f"Testing with: {args.test_data}")
        auto_printer._handle_serial_data(args.test_data)
        return
    
    if not args.port:
        print("Error: Serial port required. Use --port or --list-ports")
        return
    
    try:
        if auto_printer.start():
            print(f"Monitoring {args.port}... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        auto_printer.stop()


if __name__ == "__main__":
    main()