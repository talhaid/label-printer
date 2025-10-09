#!/usr/bin/env python3
"""
Zebra GC420T PDF Printing Module
===============================

A Python module for printing PDF files to a Zebra GC420T thermal printer.
This module provides functionality to:
- Convert PDF pages to images
- Send raw data to the Zebra printer
- Handle printer communication via USB or Network
- Configure print settings for optimal output

Requirements:
- PyPDF2 or pypdf for PDF handling
- Pillow (PIL) for image processing
- win32print for Windows printer communication
- zebra-zpl for ZPL command generation (optional)

Author: Python PDF Printer for Zebra GC420T
Date: August 2025
"""

import os
import sys
import logging
from typing import Optional, List, Tuple
import tempfile
import subprocess

try:
    import win32print
    import win32api
    import win32con
except ImportError:
    print("Warning: win32print not available. Install pywin32 for Windows printer support.")
    win32print = None

try:
    from PIL import Image, ImageWin
    PIL_AVAILABLE = True
except ImportError:
    print("Warning: Pillow not available. Install Pillow for image processing.")
    PIL_AVAILABLE = False
    Image = None

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2
        PYPDF2_AVAILABLE = True
        PYMUPDF_AVAILABLE = False
    except ImportError:
        print("Warning: No PDF library found. Install PyMuPDF or PyPDF2.")
        PYMUPDF_AVAILABLE = False
        PYPDF2_AVAILABLE = False
        fitz = None
        PyPDF2 = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ZebraPrinter:
    """
    A class to handle PDF printing to Zebra GC420T printer.
    
    The Zebra GC420T is a thermal transfer/direct thermal printer that supports
    multiple connection types including USB, Serial, and Ethernet.
    """
    
    def __init__(self, printer_name: str = None):
        """
        Initialize the Zebra printer interface.
        
        Args:
            printer_name (str): Name of the printer as it appears in Windows.
                              If None, will attempt to find Zebra printer automatically.
        """
        self.printer_name = printer_name
        self.available_printers = []
        self.printer_handle = None
        
        if win32print:
            self._discover_printers()
            if not self.printer_name:
                self.printer_name = self._find_zebra_printer()
    
    def _discover_printers(self) -> List[str]:
        """Discover all available printers on the system."""
        if not win32print:
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
            if 'zebra' in printer.lower() or 'gc420' in printer.lower():
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
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 203) -> List:
        """
        Convert PDF pages to images suitable for thermal printing.
        
        Args:
            pdf_path (str): Path to the PDF file
            dpi (int): Resolution for conversion (203 DPI matches GC420T)
            
        Returns:
            List: List of PIL Images, one per page
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        images = []
        
        if PYMUPDF_AVAILABLE and fitz:  # Use PyMuPDF (recommended)
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Convert to image with specified DPI
                mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default PDF DPI
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                
                # Convert to PIL Image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ppm') as tmp:
                    tmp.write(img_data)
                    tmp.flush()
                    if PIL_AVAILABLE:
                        img = Image.open(tmp.name)
                        # Convert to monochrome for thermal printing
                        img = img.convert('L')  # Grayscale first
                        img = img.convert('1')  # Then to monochrome
                        images.append(img)
                    
        elif PYPDF2_AVAILABLE and PyPDF2:  # Fallback to PyPDF2 (requires additional image extraction)
            logger.warning("PyPDF2 doesn't directly support image extraction. Consider installing PyMuPDF.")
            # This would require additional libraries for image extraction
            raise NotImplementedError("PyPDF2 image extraction not implemented. Please install PyMuPDF.")
        
        else:
            raise ImportError("No PDF processing library available. Install PyMuPDF or PyPDF2.")
        
        logger.info(f"Converted {len(images)} pages from PDF to images")
        return images
    
    def print_image(self, image, copies: int = 1) -> bool:
        """
        Print a PIL Image to the Zebra printer.
        
        Args:
            image: PIL Image to print
            copies (int): Number of copies to print
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.printer_name:
            logger.error("No printer specified")
            return False
        
        if not win32print:
            logger.error("win32print not available")
            return False
        
        try:
            # Open printer
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                # Start a print job
                job_info = ("Python PDF Print Job", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Convert image to bitmap for printing
                    if PIL_AVAILABLE and Image:
                        # Save image to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.bmp') as tmp:
                            # Resize image if needed (GC420T max width ~832 pixels at 203 DPI)
                            max_width = 832
                            if image.width > max_width:
                                ratio = max_width / image.width
                                new_height = int(image.height * ratio)
                                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                            
                            image.save(tmp.name, 'BMP')
                            tmp.flush()
                            
                            # Read bitmap data
                            with open(tmp.name, 'rb') as f:
                                bitmap_data = f.read()
                            
                            # Send to printer
                            for _ in range(copies):
                                win32print.WritePrinter(hprinter, bitmap_data)
                    else:
                        logger.error("PIL not available for image processing")
                        return False
                    
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
            
            logger.info(f"Successfully printed image to {self.printer_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to print image: {str(e)}")
            return False
    
    def print_pdf(self, pdf_path: str, copies: int = 1, dpi: int = 203) -> bool:
        """
        Print a PDF file to the Zebra printer.
        
        Args:
            pdf_path (str): Path to the PDF file
            copies (int): Number of copies to print
            dpi (int): Resolution for printing (203 DPI for GC420T)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting PDF print job: {pdf_path}")
            
            # Convert PDF to images
            images = self.pdf_to_images(pdf_path, dpi)
            
            if not images:
                logger.error("No images extracted from PDF")
                return False
            
            # Print each page
            success_count = 0
            for i, image in enumerate(images):
                logger.info(f"Printing page {i+1}/{len(images)}")
                if self.print_image(image, copies):
                    success_count += 1
                else:
                    logger.error(f"Failed to print page {i+1}")
            
            success = success_count == len(images)
            if success:
                logger.info(f"Successfully printed all {len(images)} pages")
            else:
                logger.warning(f"Printed {success_count}/{len(images)} pages successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to print PDF: {str(e)}")
            return False
    
    def send_raw_zpl(self, zpl_commands: str) -> bool:
        """
        Send raw ZPL commands to the printer.
        
        Args:
            zpl_commands (str): ZPL command string
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.printer_name:
            logger.error("No printer specified")
            return False
        
        if not win32print:
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
            logger.error(f"Failed to send ZPL commands: {str(e)}")
            return False
    
    def get_printer_status(self) -> dict:
        """
        Get printer status information.
        
        Returns:
            dict: Printer status information
        """
        if not self.printer_name or not win32print:
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
    
    parser = argparse.ArgumentParser(description='Print PDF files to Zebra GC420T printer')
    parser.add_argument('pdf_file', help='Path to PDF file to print')
    parser.add_argument('--printer', '-p', help='Printer name (will auto-detect if not specified)')
    parser.add_argument('--copies', '-c', type=int, default=1, help='Number of copies (default: 1)')
    parser.add_argument('--dpi', '-d', type=int, default=203, help='Print resolution DPI (default: 203)')
    parser.add_argument('--list-printers', '-l', action='store_true', help='List available printers')
    
    args = parser.parse_args()
    
    # Create printer instance
    printer = ZebraPrinter(args.printer)
    
    if args.list_printers:
        print("Available printers:")
        for p in printer.list_printers():
            print(f"  - {p}")
        return
    
    if not printer.printer_name:
        print("Error: No Zebra printer found. Available printers:")
        for p in printer.list_printers():
            print(f"  - {p}")
        print("\nSpecify printer name with --printer option")
        return
    
    print(f"Using printer: {printer.printer_name}")
    
    # Print the PDF
    if printer.print_pdf(args.pdf_file, args.copies, args.dpi):
        print("Print job completed successfully!")
    else:
        print("Print job failed!")


if __name__ == "__main__":
    main()