#!/usr/bin/env python3
"""
Debug Serial Monitor - Help diagnose serial data issues
=====================================

This tool helps identify why serial data isn't being recognized by:
1. Testing different baudrates automatically
2. Showing exact raw bytes received
3. Checking data patterns and line endings
4. Testing regex patterns against received data

Use this on the company side to see exactly what their device is sending.
"""

import sys
import os
import serial
import serial.tools.list_ports
import time
import re
from datetime import datetime

class DebugSerialMonitor:
    """Debug version of serial monitor with extensive logging"""
    
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        
    def test_connection(self):
        """Test serial connection with different baudrate settings"""
        print(f"🔧 Testing connection to {self.port}...")
        
        # Common baudrate options (most common first)
        baudrates = [115200, 9600, 38400, 19200, 57600, 4800, 2400, 1200]
        
        for baud in baudrates:
            try:
                print(f"  Testing baudrate: {baud}...", end="")
                ser = serial.Serial(
                    port=self.port,
                    baudrate=baud,
                    timeout=2.0,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                # Wait for data
                time.sleep(2)
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    print(f" ✅ DATA FOUND!")
                    print(f"    Received {len(data)} bytes: {data[:50]}{'...' if len(data) > 50 else ''}")
                    ser.close()
                    return baud
                else:
                    print(f" ❌ No data")
                
                ser.close()
                
            except Exception as e:
                print(f" ❌ Error: {e}")
        
        print("⚠️ No data detected at any baudrate. Device might not be sending data.")
        return None
    
    def monitor_raw_data(self, duration=30):
        """Monitor and log all raw data received"""
        print(f"\n📡 Monitoring raw serial data for {duration} seconds...")
        print("📝 This will show EXACTLY what the device is sending...")
        print("🎯 Looking for data that matches: ##SERIAL|IMEI|IMSI|CCID|MAC##")
        print("-" * 60)
        
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            start_time = time.time()
            buffer = b""
            data_count = 0
            total_bytes = 0
            
            print(f"⏰ Started monitoring at {datetime.now().strftime('%H:%M:%S')}")
            
            while (time.time() - start_time) < duration:
                if self.serial_connection.in_waiting > 0:
                    new_data = self.serial_connection.read(self.serial_connection.in_waiting)
                    buffer += new_data
                    data_count += 1
                    total_bytes += len(new_data)
                    
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    
                    print(f"\n📦 [{timestamp}] Chunk #{data_count} ({len(new_data)} bytes):")
                    print(f"   Hex: {new_data.hex()}")
                    print(f"   Raw: {new_data}")
                    
                    # Try to decode
                    try:
                        decoded = new_data.decode('utf-8')
                        print(f"   Text: '{decoded}'")
                        
                        # Show special characters
                        special_chars = []
                        for char in decoded:
                            if char == '\n':
                                special_chars.append('\\n')
                            elif char == '\r':
                                special_chars.append('\\r')
                            elif char == '\t':
                                special_chars.append('\\t')
                            elif ord(char) < 32 or ord(char) > 126:
                                special_chars.append(f'\\x{ord(char):02x}')
                        if special_chars:
                            print(f"   Special chars: {' '.join(special_chars)}")
                            
                    except UnicodeDecodeError as e:
                        print(f"   ⚠️ Decode error: {e}")
                        try:
                            decoded = new_data.decode('utf-8', errors='replace')
                            print(f"   Text (with replacements): '{decoded}'")
                        except:
                            print(f"   ❌ Cannot decode as text")
                    
                    # Check for complete messages in buffer
                    self._check_for_patterns(buffer)
                
                # Show progress every 5 seconds
                elif int(time.time() - start_time) % 5 == 0:
                    elapsed = int(time.time() - start_time)
                    remaining = duration - elapsed
                    if remaining > 0 and elapsed > 0:
                        print(f"⏳ {remaining}s remaining... ({data_count} chunks, {total_bytes} bytes so far)")
                
                time.sleep(0.01)
            
            print(f"\n📊 MONITORING COMPLETE")
            print(f"   Duration: {duration} seconds")
            print(f"   Data chunks received: {data_count}")
            print(f"   Total bytes: {total_bytes}")
            
            if buffer:
                print(f"\n📋 FINAL BUFFER ANALYSIS:")
                print(f"   Total buffer size: {len(buffer)} bytes")
                try:
                    final_text = buffer.decode('utf-8', errors='replace')
                    print(f"   Buffer content: '{final_text}'")
                    
                    # Final pattern check
                    self._comprehensive_pattern_check(final_text)
                    
                except Exception as e:
                    print(f"   ❌ Error analyzing final buffer: {e}")
            else:
                print(f"❌ NO DATA RECEIVED!")
                print(f"   Possible issues:")
                print(f"   - Wrong COM port selected")
                print(f"   - Wrong baudrate")
                print(f"   - Device not sending data")
                print(f"   - Cable/connection problem")
            
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
        finally:
            if self.serial_connection:
                self.serial_connection.close()
    
    def _check_for_patterns(self, buffer):
        """Check buffer for known patterns"""
        try:
            text = buffer.decode('utf-8', errors='replace')
            
            # Check for ## patterns
            if '##' in text:
                print(f"      🎯 FOUND ## MARKERS!")
                
                # Show what's between ## markers
                hash_matches = re.findall(r'##(.*?)##', text, re.DOTALL)
                if hash_matches:
                    print(f"      📋 Content between ##: {hash_matches}")
                    
                    for i, content in enumerate(hash_matches):
                        print(f"         Match {i+1}: '{content}'")
                        
                        # Count pipes
                        pipe_count = content.count('|')
                        print(f"         Pipe count: {pipe_count} (expected: 4)")
                        
                        if pipe_count == 4:
                            parts = content.split('|')
                            print(f"         Parts: {parts}")
                            print(f"         Lengths: {[len(p) for p in parts]}")
                
                # Try original regex
                pattern1 = re.compile(r'##([A-Z0-9]+)\|([0-9]+)\|([0-9\s]+)\|([0-9A-F]+)\|([A-F0-9:]+)##')
                matches1 = pattern1.findall(text)
                if matches1:
                    print(f"      ✅ ORIGINAL REGEX MATCHES: {matches1}")
                else:
                    print(f"      ❌ Original regex doesn't match")
                    
                    # Try more flexible patterns
                    pattern2 = re.compile(r'##([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^#]+)##')
                    matches2 = pattern2.findall(text)
                    if matches2:
                        print(f"      ✅ FLEXIBLE REGEX MATCHES: {matches2}")
                    else:
                        print(f"      ❌ Even flexible regex doesn't match")
            
            # Check for line endings
            line_endings = []
            if '\\n' in repr(text):
                line_endings.append('\\n')
            if '\\r' in repr(text):
                line_endings.append('\\r')
            if line_endings:
                print(f"      📄 Line endings found: {', '.join(line_endings)}")
                
        except Exception as e:
            print(f"      ⚠️ Error checking patterns: {e}")
    
    def _comprehensive_pattern_check(self, text):
        """Comprehensive check of all possible patterns"""
        print(f"\n🔍 COMPREHENSIVE PATTERN ANALYSIS:")
        
        # Check for any ## content
        if '##' in text:
            print(f"   ✅ Contains ## markers")
            
            # Extract everything between ##
            import re
            all_hash_content = re.findall(r'##(.*?)##', text, re.DOTALL)
            print(f"   Found {len(all_hash_content)} potential data packets:")
            
            for i, content in enumerate(all_hash_content):
                print(f"\n   📦 Packet {i+1}:")
                print(f"      Content: '{content}'")
                print(f"      Length: {len(content)} chars")
                
                # Check if it has pipe separators
                if '|' in content:
                    parts = content.split('|')
                    print(f"      Parts ({len(parts)}): {parts}")
                    
                    if len(parts) == 5:
                        print(f"      ✅ Correct number of parts (5)")
                        print(f"      Part 1 (Serial): '{parts[0]}' (len: {len(parts[0])})")
                        print(f"      Part 2 (IMEI): '{parts[1]}' (len: {len(parts[1])})")
                        print(f"      Part 3 (IMSI): '{parts[2]}' (len: {len(parts[2])})")
                        print(f"      Part 4 (CCID): '{parts[3]}' (len: {len(parts[3])})")
                        print(f"      Part 5 (MAC): '{parts[4]}' (len: {len(parts[4])})")
                        
                        # Test against original regex patterns
                        self._test_regex_patterns(content)
                    else:
                        print(f"      ❌ Wrong number of parts (expected 5, got {len(parts)})")
                else:
                    print(f"      ❌ No pipe separators found")
        else:
            print(f"   ❌ No ## markers found")
            print(f"   Data content: '{text[:100]}{'...' if len(text) > 100 else ''}'")
    
    def _test_regex_patterns(self, content):
        """Test various regex patterns against the content"""
        print(f"      🧪 Testing regex patterns:")
        
        # Original strict pattern
        pattern1 = r'([A-Z0-9]+)\|([0-9]+)\|([0-9\s]+)\|([0-9A-F]+)\|([A-F0-9:]+)'
        match1 = re.match(pattern1, content)
        print(f"         Strict pattern: {'✅ MATCH' if match1 else '❌ NO MATCH'}")
        if match1:
            print(f"         Groups: {match1.groups()}")
        
        # More flexible pattern
        pattern2 = r'([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)'
        match2 = re.match(pattern2, content)
        print(f"         Flexible pattern: {'✅ MATCH' if match2 else '❌ NO MATCH'}")
        if match2:
            print(f"         Groups: {match2.groups()}")

def main():
    """Main debug function"""
    print("🔍 SERIAL DATA DEBUG TOOL")
    print("=" * 60)
    print("This tool will help diagnose why serial data isn't being recognized.")
    print("Run this on the computer where the device data isn't working.")
    print("=" * 60)
    
    # List available ports
    print("\n📱 Available serial ports:")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("❌ No serial ports found!")
        print("   Make sure your device is connected and drivers are installed.")
        input("Press Enter to exit...")
        return
    
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    # Get port selection
    try:
        choice = input(f"\nSelect port (1-{len(ports)}): ").strip()
        if not choice:
            print("❌ No selection made!")
            return
        port_index = int(choice) - 1
        if port_index < 0 or port_index >= len(ports):
            raise IndexError()
        selected_port = ports[port_index].device
    except (ValueError, IndexError):
        print("❌ Invalid selection!")
        return
    
    print(f"\n🎯 Selected port: {selected_port}")
    
    # Create debug monitor
    debug_monitor = DebugSerialMonitor(selected_port)
    
    # Test connection with different baudrates
    print(f"\n🔧 Step 1: Testing connection...")
    working_baudrate = debug_monitor.test_connection()
    if working_baudrate:
        print(f"✅ Found data at {working_baudrate} baud!")
        debug_monitor.baudrate = working_baudrate
    else:
        print("⚠️ No data detected automatically.")
        try:
            manual_baud = input("Enter baudrate manually (or press Enter for 9600): ").strip()
            if manual_baud:
                debug_monitor.baudrate = int(manual_baud)
        except ValueError:
            print("Using default 9600 baud")
    
    # Monitor raw data
    print(f"\n📡 Step 2: Monitoring raw data...")
    try:
        duration_input = input(f"Monitor duration in seconds (default 30): ").strip()
        duration = int(duration_input) if duration_input else 30
    except ValueError:
        duration = 30
    
    debug_monitor.monitor_raw_data(duration)
    
    print(f"\n🏁 Debug session complete!")
    print(f"📧 Share this output to help diagnose the issue.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()