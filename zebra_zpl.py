#!/usr/bin/env python3
"""
Zebra GC420T ZPL Printing Module
===============================

A Python module for sending ZPL (Zebra Programming Language) commands 
to your Zebra GC420T thermal printer.

ZPL is the native language for Zebra printers and provides:
- Fast, direct printing without image conversion
- Precise control over layout and formatting
- Support for barcodes, text, and graphics
- Efficient memory usage
- Professional label printing

Author: ZPL Printer for Zebra GC420T
Date: August 2025
"""

import os
import sys
import logging
from typing import Optional, List, Dict
import datetime

try:
    import win32print
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    print("Warning: win32print not available. Install pywin32 for Windows printer support.")
    WIN32_AVAILABLE = False
    win32print = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ZebraZPL:
    """
    A class to handle ZPL command generation and printing to Zebra GC420T printer.
    
    The Zebra GC420T supports ZPL II commands for creating professional labels
    with text, barcodes, graphics, and precise formatting.
    """
    
    def __init__(self, printer_name: str = None, debug_mode: bool = False):
        """
        Initialize the Zebra ZPL interface.
        
        Args:
            printer_name (str): Name of the printer as it appears in Windows.
                              If None, will attempt to find Zebra printer automatically.
            debug_mode (bool): If True, simulates printing without sending to actual printer.
        """
        self.printer_name = printer_name
        self.available_printers = []
        self.printer_handle = None
        self.debug_mode = debug_mode
        self.last_print_data = None  # Store last print data for debugging
        
        # Default settings for GC420T
        self.dpi = 203  # GC420T resolution
        self.label_width = 832  # pixels at 203 DPI (4 inches)
        self.label_height = 609  # pixels at 203 DPI (3 inches)
        
        if self.debug_mode:
            logger.info("🔧 DEBUG MODE: ZPL printer initialized in debug mode (no actual printing)")
            self.printer_name = "DEBUG_PRINTER"
            self.available_printers = ["DEBUG_PRINTER", "Simulated Zebra GC420T"]
        elif WIN32_AVAILABLE:
            self._discover_printers()
            if not self.printer_name:
                self.printer_name = self._find_zebra_printer()
    
    def _discover_printers(self) -> List[str]:
        """Discover all available printers on the system."""
        if not WIN32_AVAILABLE:
            logger.error("win32print not available")
            return []
        
        printers = []
        printer_enum = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        
        for printer in printer_enum:
            printers.append(printer[2])  # printer name
        
        self.available_printers = printers
        logger.info(f"Found {len(printers)} printers: {', '.join(printers)}")
        return printers
    
    def _find_zebra_printer(self) -> Optional[str]:
        """Automatically find Zebra printer in the system."""
        for printer in self.available_printers:
            if 'zebra' in printer.lower() or 'gc420' in printer.lower() or 'zdesigner' in printer.lower():
                logger.info(f"Found Zebra printer: {printer}")
                return printer
        
        logger.warning("No Zebra printer found automatically")
        return None
    
    def list_printers(self) -> List[str]:
        """Return list of available printers."""
        return self.available_printers
    
    def set_printer(self, printer_name: str) -> bool:
        """
        Set the target printer for printing operations.
        
        Args:
            printer_name (str): Name of the printer
            
        Returns:
            bool: True if printer is available, False otherwise
        """
        if printer_name in self.available_printers:
            self.printer_name = printer_name
            logger.info(f"Printer set to: {printer_name}")
            return True
        else:
            logger.error(f"Printer '{printer_name}' not found")
            return False
    
    def send_zpl(self, zpl_commands: str) -> bool:
        """
        Send ZPL commands to the printer.
        
        Args:
            zpl_commands (str): ZPL command string
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.printer_name:
            logger.error("No printer specified")
            return False
        
        # Debug mode - simulate printing
        if self.debug_mode:
            self.last_print_data = zpl_commands
            logger.info("🖨️ DEBUG MODE: Simulating ZPL print job")
            logger.info(f"📄 ZPL Commands ({len(zpl_commands)} chars):")
            
            # Show a preview of the ZPL commands
            lines = zpl_commands.strip().split('\n')
            for i, line in enumerate(lines[:10]):  # Show first 10 lines
                logger.info(f"   {i+1:2d}: {line}")
            if len(lines) > 10:
                logger.info(f"   ... ({len(lines)-10} more lines)")
            
            logger.info("✅ DEBUG MODE: Print job simulated successfully")
            return True
        
        if not WIN32_AVAILABLE:
            logger.error("win32print not available")
            return False
        
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                job_info = ("ZPL Print Job", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, zpl_commands.encode('utf-8'))
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
            
            logger.info("Successfully sent ZPL commands to printer")
            return True
            
        except Exception as e:
            logger.error(f"Error sending ZPL commands: {e}")
            return False
    
    def send_tspl(self, tspl_commands: str) -> bool:
        """
        Send TSPL commands to the printer (for XPrinter and TSC printers).
        
        Args:
            tspl_commands (str): TSPL command string
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.printer_name:
            logger.error("No printer specified")
            return False
        
        # Debug mode - simulate printing
        if self.debug_mode:
            self.last_print_data = tspl_commands
            logger.info("🖨️ DEBUG MODE: Simulating TSPL print job")
            logger.info(f"📄 TSPL Commands ({len(tspl_commands)} chars):")
            
            # Show a preview of the TSPL commands
            lines = tspl_commands.strip().split('\n')
            for i, line in enumerate(lines[:15]):  # Show first 15 lines
                logger.info(f"   {i+1:2d}: {line}")
            if len(lines) > 15:
                logger.info(f"   ... ({len(lines)-15} more lines)")
            
            logger.info("✅ DEBUG MODE: TSPL print job simulated successfully")
            return True
        
        if not WIN32_AVAILABLE:
            logger.error("win32print not available")
            return False
        
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                job_info = ("TSPL Print Job", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, tspl_commands.encode('utf-8'))
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
            
            logger.info("Successfully sent TSPL commands to printer")
            return True
            
        except Exception as e:
            logger.error(f"Error sending TSPL commands: {e}")
            return False
    
    def create_text_label(self, title: str, text_lines: List[str], 
                         title_size: int = 36, text_size: int = 18) -> str:
        """
        Create a simple text label with title and multiple lines.
        
        Args:
            title (str): Main title text
            text_lines (List[str]): List of text lines to print
            title_size (int): Font size for title
            text_size (int): Font size for text lines
            
        Returns:
            str: ZPL command string
        """
        zpl = "^XA\n"  # Start format
        zpl += "^LH30,30\n"  # Label home position
        
        # Title
        y_pos = 10
        zpl += f"^FO20,{y_pos}^ADN,{title_size},20^FD{title}^FS\n"
        
        # Text lines
        y_pos += title_size + 10
        for line in text_lines:
            zpl += f"^FO20,{y_pos}^ADN,{text_size},10^FD{line}^FS\n"
            y_pos += text_size + 5
        
        zpl += "^XZ\n"  # End format
        return zpl
    
    def create_barcode_label(self, title: str, barcode_data: str, 
                           barcode_type: str = "BCN", text_lines: List[str] = None) -> str:
        """
        Create a label with barcode and optional text.
        
        Args:
            title (str): Label title
            barcode_data (str): Data to encode in barcode
            barcode_type (str): ZPL barcode type (BCN=Code128, B3N=Code39, etc.)
            text_lines (List[str]): Optional additional text lines
            
        Returns:
            str: ZPL command string
        """
        zpl = "^XA\n"
        zpl += "^LH30,30\n"
        
        # Title
        y_pos = 10
        zpl += f"^FO20,{y_pos}^ADN,24,12^FD{title}^FS\n"
        y_pos += 40
        
        # Additional text lines
        if text_lines:
            for line in text_lines:
                zpl += f"^FO20,{y_pos}^ADN,18,10^FD{line}^FS\n"
                y_pos += 25
        
        # Barcode
        y_pos += 10
        zpl += f"^FO20,{y_pos}^BY2^{barcode_type},70,Y,N,N^FD{barcode_data}^FS\n"
        
        zpl += "^XZ\n"
        return zpl
    
    def create_shipping_label(self, from_info: Dict, to_info: Dict, 
                            tracking: str = None, date: str = None) -> str:
        """
        Create a shipping label with from/to addresses.
        
        Args:
            from_info (Dict): Sender information {'name', 'address1', 'address2', 'city_state_zip'}
            to_info (Dict): Recipient information {'name', 'address1', 'address2', 'city_state_zip'}
            tracking (str): Optional tracking number
            date (str): Optional date string
            
        Returns:
            str: ZPL command string
        """
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        zpl = "^XA\n"
        zpl += "^LH30,30\n"
        
        # From section
        y_pos = 10
        zpl += f"^FO20,{y_pos}^ADN,20,10^FDFROM:^FS\n"
        y_pos += 25
        zpl += f"^FO20,{y_pos}^ADN,16,8^FD{from_info.get('name', '')}^FS\n"
        y_pos += 20
        if from_info.get('address1'):
            zpl += f"^FO20,{y_pos}^ADN,14,7^FD{from_info['address1']}^FS\n"
            y_pos += 18
        if from_info.get('address2'):
            zpl += f"^FO20,{y_pos}^ADN,14,7^FD{from_info['address2']}^FS\n"
            y_pos += 18
        if from_info.get('city_state_zip'):
            zpl += f"^FO20,{y_pos}^ADN,14,7^FD{from_info['city_state_zip']}^FS\n"
        
        # To section
        y_pos = 160
        zpl += f"^FO20,{y_pos}^ADN,20,10^FDTO:^FS\n"
        y_pos += 25
        zpl += f"^FO20,{y_pos}^ADN,18,9^FD{to_info.get('name', '')}^FS\n"
        y_pos += 23
        if to_info.get('address1'):
            zpl += f"^FO20,{y_pos}^ADN,16,8^FD{to_info['address1']}^FS\n"
            y_pos += 20
        if to_info.get('address2'):
            zpl += f"^FO20,{y_pos}^ADN,16,8^FD{to_info['address2']}^FS\n"
            y_pos += 20
        if to_info.get('city_state_zip'):
            zpl += f"^FO20,{y_pos}^ADN,16,8^FD{to_info['city_state_zip']}^FS\n"
        
        # Date and tracking
        y_pos = 320
        zpl += f"^FO20,{y_pos}^ADN,14,7^FDDate: {date}^FS\n"
        
        if tracking:
            y_pos += 25
            zpl += f"^FO20,{y_pos}^BY2^BCN,50,Y,N,N^FD{tracking}^FS\n"
        
        zpl += "^XZ\n"
        return zpl
    
    def create_product_label(self, product_name: str, sku: str, price: str = None, 
                           barcode: str = None, description: str = None) -> str:
        """
        Create a product label with name, SKU, price, and optional barcode.
        
        Args:
            product_name (str): Product name
            sku (str): SKU or product code
            price (str): Price string (e.g., "$19.99")
            barcode (str): Barcode data (if different from SKU)
            description (str): Optional product description
            
        Returns:
            str: ZPL command string
        """
        zpl = "^XA\n"
        zpl += "^LH30,30\n"
        
        # Product name
        y_pos = 10
        zpl += f"^FO20,{y_pos}^ADN,24,12^FD{product_name}^FS\n"
        y_pos += 35
        
        # SKU
        zpl += f"^FO20,{y_pos}^ADN,18,9^FDSKU: {sku}^FS\n"
        y_pos += 25
        
        # Price
        if price:
            zpl += f"^FO20,{y_pos}^ADN,20,10^FDPrice: {price}^FS\n"
            y_pos += 30
        
        # Description
        if description:
            zpl += f"^FO20,{y_pos}^ADN,14,7^FD{description}^FS\n"
            y_pos += 25
        
        # Barcode (use SKU if no specific barcode provided)
        barcode_data = barcode or sku
        y_pos += 10
        zpl += f"^FO20,{y_pos}^BY2^BCN,60,Y,N,N^FD{barcode_data}^FS\n"
        
        zpl += "^XZ\n"
        return zpl
    
    def print_text_label(self, title: str, text_lines: List[str], copies: int = 1) -> bool:
        """Print a simple text label."""
        zpl = self.create_text_label(title, text_lines)
        return self.print_multiple(zpl, copies)
    
    def print_barcode_label(self, title: str, barcode_data: str, 
                          text_lines: List[str] = None, copies: int = 1) -> bool:
        """Print a barcode label."""
        zpl = self.create_barcode_label(title, barcode_data, text_lines=text_lines)
        return self.print_multiple(zpl, copies)
    
    def print_shipping_label(self, from_info: Dict, to_info: Dict, 
                           tracking: str = None, copies: int = 1) -> bool:
        """Print a shipping label."""
        zpl = self.create_shipping_label(from_info, to_info, tracking)
        return self.print_multiple(zpl, copies)
    
    def print_product_label(self, product_name: str, sku: str, price: str = None, 
                          barcode: str = None, copies: int = 1) -> bool:
        """Print a product label."""
        zpl = self.create_product_label(product_name, sku, price, barcode)
        return self.print_multiple(zpl, copies)
    
    def print_multiple(self, zpl_commands: str, copies: int = 1) -> bool:
        """
        Print multiple copies of a ZPL label.
        
        Args:
            zpl_commands (str): ZPL command string
            copies (int): Number of copies to print
            
        Returns:
            bool: True if successful, False otherwise
        """
        success_count = 0
        for i in range(copies):
            if copies > 1:
                logger.info(f"Printing copy {i+1}/{copies}")
            if self.send_zpl(zpl_commands):
                success_count += 1
            else:
                logger.error(f"Failed to print copy {i+1}")
        
        success = success_count == copies
        if success:
            logger.info(f"Successfully printed {copies} copies")
        else:
            logger.warning(f"Printed {success_count}/{copies} copies successfully")
        
        return success
    
    def get_printer_status(self) -> dict:
        """Get printer status information."""
        if not self.printer_name or not WIN32_AVAILABLE:
            return {}
        
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                printer_info = win32print.GetPrinter(hprinter, 2)
                return {
                    'name': printer_info['pPrinterName'],
                    'status': printer_info['Status'],
                    'driver': printer_info['pDriverName'],
                    'port': printer_info['pPortName'],
                    'location': printer_info.get('pLocation', 'Unknown'),
                    'comment': printer_info.get('pComment', '')
                }
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Failed to get printer status: {str(e)}")
            return {}


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Print ZPL labels to Zebra GC420T printer')
    parser.add_argument('--printer', '-p', help='Printer name (will auto-detect if not specified)')
    parser.add_argument('--copies', '-c', type=int, default=1, help='Number of copies (default: 1)')
    parser.add_argument('--list-printers', '-l', action='store_true', help='List available printers')
    
    # Label types
    parser.add_argument('--text', nargs='+', help='Create text label: --text "Title" "Line 1" "Line 2"')
    parser.add_argument('--barcode', nargs=2, help='Create barcode label: --barcode "Title" "1234567890"')
    parser.add_argument('--product', nargs='+', help='Create product label: --product "Name" "SKU" ["Price"] ["Barcode"]')
    parser.add_argument('--raw-zpl', help='Send raw ZPL commands from string')
    parser.add_argument('--zpl-file', help='Send ZPL commands from file')
    
    args = parser.parse_args()
    
    # Create printer instance
    printer = ZebraZPL(args.printer)
    
    if args.list_printers:
        print("Available printers:")
        for p in printer.list_printers():
            marker = " <- Zebra" if any(x in p.lower() for x in ['zebra', 'gc420', 'zdesigner']) else ""
            print(f"  - {p}{marker}")
        return
    
    if not printer.printer_name:
        print("Error: No Zebra printer found. Available printers:")
        for p in printer.list_printers():
            print(f"  - {p}")
        print("\nSpecify printer name with --printer option")
        return
    
    print(f"Using printer: {printer.printer_name}")
    
    # Handle different label types
    success = False
    
    if args.text:
        if len(args.text) < 1:
            print("Error: --text requires at least a title")
            return
        title = args.text[0]
        lines = args.text[1:] if len(args.text) > 1 else []
        success = printer.print_text_label(title, lines, args.copies)
    
    elif args.barcode:
        title, barcode_data = args.barcode
        success = printer.print_barcode_label(title, barcode_data, copies=args.copies)
    
    elif args.product:
        if len(args.product) < 2:
            print("Error: --product requires at least name and SKU")
            return
        name = args.product[0]
        sku = args.product[1]
        price = args.product[2] if len(args.product) > 2 else None
        barcode = args.product[3] if len(args.product) > 3 else None
        success = printer.print_product_label(name, sku, price, barcode, args.copies)
    
    elif args.raw_zpl:
        success = printer.print_multiple(args.raw_zpl, args.copies)
    
    elif args.zpl_file:
        try:
            with open(args.zpl_file, 'r') as f:
                zpl_content = f.read()
            success = printer.print_multiple(zpl_content, args.copies)
        except FileNotFoundError:
            print(f"Error: ZPL file not found: {args.zpl_file}")
            return
    
    else:
        print("Error: No label type specified. Use --text, --barcode, --product, --raw-zpl, or --zpl-file")
        print("Use --help for usage examples")
        return
    
    if success:
        print("✅ Print job completed successfully!")
    else:
        print("❌ Print job failed!")


if __name__ == "__main__":
    main()