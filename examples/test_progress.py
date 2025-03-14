#!/usr/bin/env python3
"""
Test script to verify progress information in encrypt_fasta and decrypt_fasta functions.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure import encrypt_sequence, decrypt_sequence

def main():
    """Main entry point for the script."""
    print("\n=== Testing Progress Information ===")
    
    # Create a test sequence
    sequence = "ATGCATGCATGCATGC" * 1000
    print(f"Created test sequence of length {len(sequence)}")
    
    # Encrypt the sequence
    print("\nEncrypting sequence...")
    encrypted_data, removed_values = encrypt_sequence(sequence)
    print(f"Encryption complete. Data size: {len(encrypted_data)} bytes")
    
    # Decrypt the sequence
    print("\nDecrypting sequence...")
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    print(f"Decryption complete. Sequence length: {len(decrypted_sequence)}")
    
    # Verify the result
    print("\n=== Verification ===")
    print(f"Original length: {len(sequence)}")
    print(f"Decrypted length: {len(decrypted_sequence)}")
    print(f"Match: {sequence == decrypted_sequence}")

if __name__ == "__main__":
    main() 