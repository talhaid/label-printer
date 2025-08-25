#!/usr/bin/env python3
"""
XPrinter XP-470B PCB Label Printer
==================================

Module for printing simple PCB labels containing only serial numbers
on XPrinter XP-470B thermal printer using ESC/POS commands.

Paper size: 4cm x 2cm
Content: Serial Number only

Author: XPrinter PCB Label Module
Date: August 2025
"""

import win32print
import logging
import time

logger = logging.getLogger(__name__)


class XPrinterPCB:
    """XPrinter XP-470B PCB label printer class."""
    
    def __init__(self):
        """Initialize the XPrinter PCB printer."""
        self.printer_name = None
        self.find_xprinter()
        
        # TSPL commands (TSC Printer Language) - XPrinter XP-470B uses TSPL, not ESC/POS
        # No need for ESC/POS commands since XPrinter uses TSPL
        
    def find_xprinter(self):
        """Find XPrinter in the system."""
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            logger.info(f"Available printers: {printers}")
            
            # Look for XPrinter
            for printer in printers:
                if 'xprinter' in printer.lower() or 'xp-470b' in printer.lower():
                    self.printer_name = printer
                    logger.info(f"Found XPrinter: {self.printer_name}")
                    return True
            
            logger.warning("XPrinter XP-470B not found")
            return False
            
        except Exception as e:
            logger.error(f"Error finding XPrinter: {e}")
            return False
    
    def print_pcb_label_custom_position(self, serial_number, production_date=None, x_pos1=65, x_pos2=100, y1_pos=40, y2_pos=90):
        """Print PCB label with custom positioning for manual adjustment."""
        if not self.printer_name:
            logger.error("XPrinter not found")
            return False
        
        if not serial_number:
            logger.error("Serial number is required")
            return False
        
        # Use current date if production date not provided
        if not production_date:
            from datetime import datetime
            production_date = datetime.now().strftime('%d/%m/%Y')
        
        try:
            # Create TSPL command sequence for 4cm x 2cm PCB label
            commands = b''
            commands += b'SIZE 40 mm, 20 mm\n'  # Set label size to 4cm x 2cm
            commands += b'GAP 2 mm, 0 mm\n'     # Gap between labels
            commands += b'DIRECTION 1,0\n'       # Print direction
            commands += b'REFERENCE 0,0\n'       # Reference point
            commands += b'OFFSET 0 mm\n'         # Offset
            commands += b'SET TEAR ON\n'         # Tear mode
            commands += b'CLS\n'                 # Clear buffer
            
            # Custom positioned text fields
            # Serial number line - without header
            commands += f'TEXT {x_pos1},{y1_pos},"3",0,1,1,"{serial_number}"\n'.encode('utf-8')
            
            # Production date line - without header
            commands += f'TEXT {x_pos2},{y2_pos},"3",0,1,1,"{production_date}"\n'.encode('utf-8')
            
            commands += b'PRINT 1,1\n'           # Print 1 copy
            
            # Send to printer
            success = self._send_to_printer(commands)
            
            if success:
                logger.info(f"Successfully printed PCB label for: {serial_number} at position ({x_pos1}, {y1_pos}) and ({x_pos2}, {y2_pos})")
            else:
                logger.error(f"Failed to print PCB label for: {serial_number}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error printing PCB label: {e}")
            return False

    def print_pcb_label(self, serial_number, production_date=None):
        """Print PCB label with serial number and production date using TSPL commands."""
        if not self.printer_name:
            logger.error("XPrinter not found")
            return False
        
        if not serial_number:
            logger.error("Serial number is required")
            return False
        
        # Use current date if production date not provided
        if not production_date:
            from datetime import datetime
            production_date = datetime.now().strftime('%d/%m/%Y')
        
        try:
            # Create TSPL command sequence for 4cm x 2cm PCB label
            commands = b''
            commands += b'SIZE 40 mm, 20 mm\n'  # Set label size to 4cm x 2cm
            commands += b'GAP 2 mm, 0 mm\n'     # Gap between labels
            commands += b'DIRECTION 1,0\n'       # Print direction
            commands += b'REFERENCE 0,0\n'       # Reference point
            commands += b'OFFSET 0 mm\n'         # Offset
            commands += b'SET TEAR ON\n'         # Tear mode
            commands += b'CLS\n'                 # Clear buffer
            
            # Center-aligned text fields for 4cm x 2cm label with optimized positioning
            # Serial number positioned at X=65, Date at X=100 for better alignment
            
            # Serial number line - positioned at X=65 for optimal placement
            commands += b'TEXT 65,40,"3",0,1,1,"' + serial_number.encode('utf-8') + b'"\n'
            
            # Production date line - positioned at X=100 for optimal placement
            commands += b'TEXT 100,90,"3",0,1,1,"' + production_date.encode('utf-8') + b'"\n'
            
            commands += b'PRINT 1,1\n'           # Print 1 copy
            
            # Send to printer
            success = self._send_to_printer(commands)
            
            if success:
                logger.info(f"Successfully printed PCB label for: {serial_number}")
            else:
                logger.error(f"Failed to print PCB label for: {serial_number}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error printing PCB label: {e}")
            return False
    
    def _send_to_printer(self, data):
        """Send raw data to printer."""
        try:
            # Open printer
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                # Start print job
                job_info = ("PCB Label", None, None)
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Send raw data
                    win32print.WritePrinter(hprinter, data)
                    
                    win32print.EndPagePrinter(hprinter)
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during print operation: {e}")
                    return False
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Error sending to XPrinter: {e}")
            return False
    
    def test_print(self):
        """Test print functionality."""
        return self.print_pcb_label("TEST12345")
    
    def is_available(self):
        """Check if XPrinter is available."""
        return self.printer_name is not None
    
    def print_simple_text(self, text):
        """Print simple text for testing using TSPL."""
        if not self.printer_name:
            return False
            
        try:
            commands = b''
            commands += b'SIZE 40 mm, 20 mm\n'  # Set label size
            commands += b'CLS\n'                 # Clear buffer
            commands += b'TEXT 10,10,"3",0,1,1,"' + text.encode('utf-8') + b'"\n'  # Print text
            commands += b'PRINT 1\n'             # Print 1 copy
            
            return self._send_to_printer(commands)
            
        except Exception as e:
            logger.error(f"Error printing simple text: {e}")
            return False


def main():
    """Test the XPrinter PCB functionality."""
    logging.basicConfig(level=logging.INFO)
    
    printer = XPrinterPCB()
    
    if printer.is_available():
        print(f"XPrinter found: {printer.printer_name}")
        
        # Test print
        test_serial = "ATS123456789"
        print(f"Testing print with serial: {test_serial}")
        success = printer.print_pcb_label(test_serial)
        print(f"Print test result: {'Success' if success else 'Failed'}")
    else:
        print("XPrinter XP-470B not found")


if __name__ == "__main__":
    main()