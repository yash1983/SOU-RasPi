#!/usr/bin/env python3
"""
Ticket Parser Utility for SOU Raspberry Pi
Handles QR code parsing and HMAC verification for offline ticket validation
"""

import hmac
import hashlib
import base64


class TicketParser:
    """Parse and validate QR code tickets using HMAC verification"""
    
    def __init__(self, secret_key="mayur@123", gate_mapping=None):
        """
        Initialize ticket parser with secret key and gate mapping
        
        Args:
            secret_key: Secret key for HMAC verification (default: "mayur@123")
            gate_mapping: Dictionary mapping attraction codes to gate codes (e.g., {'A': '01', 'B': '02', 'C': '03'})
                         If None, will try to load from config, otherwise uses default {'A': '01', 'B': '02', 'C': '03'}
        """
        self.secret_key = secret_key
        
        # Load gate mapping from config if not provided
        if gate_mapping is None:
            try:
                from config import config
                gate_mapping = config.get('gate_mapping', {})
            except ImportError:
                gate_mapping = {}
        
        # Use default mapping if config is empty or missing
        if not gate_mapping:
            gate_mapping = {'A': '01', 'B': '02', 'C': '03'}
        
        self.gate_mapping = gate_mapping
    
    def generate_verification_code(self, ticket_data):
        """
        Generate a 12-character verification code using HMAC-SHA256
        
        Args:
            ticket_data: The ticket data string (e.g., "20251015-000003-010202020302")
        
        Returns:
            12-character verification code (HEX-encoded, uppercase, first 12 chars)
        """
        # Create HMAC using SHA-256
        hmac_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            ticket_data.encode('utf-8'),
            hashlib.sha256
        )
        
        # Get the digest and return first 12 HEX chars (uppercase)
        digest = hmac_obj.digest()
        hex_digest = digest.hex().upper()
        return hex_digest[:12]
    
    def verify_verification_code(self, ticket_data, provided_code):
        """
        Verify that the provided code matches the ticket data
        
        Args:
            ticket_data: The ticket data string (e.g., "20251015-000003-010702080309")
            provided_code: The 12-character code from QR code
        
        Returns:
            True if verification code is valid, False otherwise
        """
        expected_code = self.generate_verification_code(ticket_data)
        
        # Normalize provided code to uppercase (server sends HEX)
        provided_norm = (provided_code or "").upper()
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_code, provided_norm)
    
    def parse_qr_code(self, qr_code):
        """
        Parse QR code and extract ticket information
        
        Format: YYYYMMDD-SERIAL-GATES-VERIFICATIONCODE
        Example: 20251014-000019-010207021602-467C41E17F6B
        
        Gate codes:
        - Gate codes are configurable via config.json gate_mapping
        - Default: 01 = Gate A (Attraction A), 02 = Gate B (Attraction B), 03 = Gate C (Attraction C)
        
        Args:
            qr_code: The full QR code string
        
        Returns:
            dict with parsed data:
            {
                'valid': bool,
                'date': str (YYYYMMDD),
                'serial': str,
                'reference_no': str (full reference: YYYYMMDD-SERIAL),
                'gates': str (gate passenger string),
                'gate_info': dict ({'01': 7, '02': 8, '03': 9}),
                'verification_code': str,
                'ticket_data': str (data part without verification),
                'error': str (if invalid)
            }
        """
        parts = qr_code.split('-')
        
        if len(parts) < 4:
            return {
                'valid': False,
                'error': 'Invalid QR format - not enough parts',
                'parts_count': len(parts)
            }
        
        # Extract parts
        date = parts[0]  # YYYYMMDD
        serial = parts[1]  # Serial number (e.g., 000003)
        gates = parts[2]  # Gate-wise passengers (e.g., 010702080309)
        verification_code = '-'.join(parts[3:])  # Last part(s) as verification code
        
        # Validate date format (8 digits)
        if len(date) != 8 or not date.isdigit():
            return {
                'valid': False,
                'error': f'Invalid date format: {date}'
            }
        
        # Validate serial format
        if not serial.isdigit():
            return {
                'valid': False,
                'error': f'Invalid serial format: {serial}'
            }
        
        # Validate gates format (must be multiple of 4 characters: GGNN where GG=gate, NN=passengers)
        if len(gates) % 4 != 0:
            return {
                'valid': False,
                'error': f'Invalid gates format: {gates} (length must be multiple of 4)'
            }
        
        # Parse gate information
        gate_info = {}
        for i in range(0, len(gates), 4):
            if i + 4 <= len(gates):
                gate_code = gates[i:i+2]
                try:
                    passenger_count = int(gates[i+2:i+4])
                    gate_info[gate_code] = passenger_count
                except ValueError:
                    return {
                        'valid': False,
                        'error': f'Invalid passenger count in gates: {gates[i+2:i+4]}'
                    }
        
        # Reconstruct ticket data (without verification code) for HMAC validation
        ticket_data = f"{date}-{serial}-{gates}"
        
        # Create reference number (for database lookup)
        reference_no = f"{date}-{serial}"
        
        # Verify the code
        hmac_valid = self.verify_verification_code(ticket_data, verification_code)
        
        return {
            'valid': hmac_valid,
            'date': date,
            'serial': serial,
            'reference_no': reference_no,
            'gates': gates,
            'gate_info': gate_info,  # {'01': 7, '02': 8, '03': 9}
            'verification_code': verification_code,
            'ticket_data': ticket_data,
            'error': None if hmac_valid else 'Invalid verification code'
        }
    
    def get_attraction_passengers(self, parsed_ticket, attraction_code):
        """
        Get passenger count for a specific attraction from parsed ticket
        
        Args:
            parsed_ticket: Parsed ticket dict from parse_qr_code()
            attraction_code: 'A', 'B', or 'C'
        
        Returns:
            Passenger count for the attraction (0 if not valid for that attraction)
        """
        if not parsed_ticket.get('valid'):
            return 0
        
        # Map attraction codes to gate codes using configured mapping
        gate_code = self.gate_mapping.get(attraction_code.upper())
        if not gate_code:
            return 0
        
        return parsed_ticket.get('gate_info', {}).get(gate_code, 0)
    
    def get_gate_mapping(self):
        """
        Get the current gate mapping configuration
        
        Returns:
            Dictionary mapping attraction codes to gate codes
        """
        return self.gate_mapping.copy()


def test_ticket_parser():
    """Test ticket parser functionality"""
    parser = TicketParser(secret_key="mayur@123")
    
    # Test QR code from user's example
    qr_code = "20251015-000003-010702080309-8ML/Lf6faRhs"
    
    print("Testing Ticket Parser")
    print("=" * 60)
    print(f"QR Code: {qr_code}")
    print()
    
    # Parse the QR code
    parsed = parser.parse_qr_code(qr_code)
    
    if parsed['valid']:
        print("[OK] QR Code is valid!")
        print(f"  Date: {parsed['date']}")
        print(f"  Serial: {parsed['serial']}")
        print(f"  Reference No: {parsed['reference_no']}")
        print(f"  Gate Info: {parsed['gate_info']}")
        print(f"  Attraction A passengers: {parser.get_attraction_passengers(parsed, 'A')}")
        print(f"  Attraction B passengers: {parser.get_attraction_passengers(parsed, 'B')}")
        print(f"  Attraction C passengers: {parser.get_attraction_passengers(parsed, 'C')}")
    else:
        print(f"[ERROR] QR Code is invalid: {parsed.get('error', 'Unknown error')}")
    
    print()
    
    # Test verification code generation
    ticket_data = "20251015-000003-010702080309"
    code = parser.generate_verification_code(ticket_data)
    print(f"Ticket Data: {ticket_data}")
    print(f"Generated Code: {code}")
    print(f"Verification: {parser.verify_verification_code(ticket_data, code)}")
    print()
    
    # Test that different data produces different code
    ticket_data2 = "20251015-000003-010702080310"  # Changed last digit
    code2 = parser.generate_verification_code(ticket_data2)
    print(f"Ticket Data: {ticket_data2}")
    print(f"Generated Code: {code2}")
    print(f"Codes are different: {code != code2}")


if __name__ == "__main__":
    test_ticket_parser()

