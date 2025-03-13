#!/usr/bin/env python3
"""
Basic usage example for the DNAsecure package.

This script demonstrates how to:
1. Encrypt a simple DNA sequence
2. Decrypt it back to the original sequence
3. Encrypt and decrypt a FASTA file
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    encrypt_fasta,
    decrypt_fasta,
    dna_to_number,
    number_to_dna
)

def test_single_sequence():
    """Test encryption and decryption of a single DNA sequence."""
    print("\n=== Testing Single Sequence Encryption/Decryption ===")
    
    # Create a simple DNA sequence
    original_sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
    print(f"Original sequence: {original_sequence}")
    print(f"Sequence length: {len(original_sequence)}")
    
    # Convert to number and back as a basic test
    number = dna_to_number(original_sequence)
    print(f"As number: {number}")
    sequence_from_number = number_to_dna(number)
    print(f"Back to sequence: {sequence_from_number}")
    print(f"Matches original: {original_sequence == sequence_from_number}")
    
    # Encrypt the sequence
    print("\nEncrypting sequence...")
    encrypted_data, removed_values = encrypt_sequence(original_sequence, num_removed=5)
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    print(f"Removed values: {removed_values}")
    
    # Decrypt the sequence
    print("\nDecrypting sequence...")
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    print(f"Decrypted sequence: {decrypted_sequence}")
    print(f"Matches original: {original_sequence == decrypted_sequence}")
    
    # Try decryption with wrong key
    print("\nTesting decryption with wrong key...")
    wrong_values = [(pos, val + 1) for pos, val in removed_values]  # Modify the values
    try:
        wrong_sequence = decrypt_sequence(encrypted_data, wrong_values)
        print(f"Decrypted with wrong key: {wrong_sequence}")
        print(f"Matches original: {original_sequence == wrong_sequence}")
    except Exception as e:
        print(f"Error with wrong key: {e}")

def create_test_fasta():
    """Create a temporary FASTA file for testing."""
    fd, path = tempfile.mkstemp(suffix='.fasta')
    with os.fdopen(fd, 'w') as f:
        f.write(">Sequence1 Test sequence 1\n")
        f.write("ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC\n")
        f.write(">Sequence2 Test sequence 2\n")
        f.write("GGGAAACCCTTTAGGCATGCATGCATGCATGCATGCATGCATGC\n")
    return path

def test_fasta_file():
    """Test encryption and decryption of a FASTA file."""
    print("\n=== Testing FASTA File Encryption/Decryption ===")
    
    # Create a temporary FASTA file
    input_fasta = create_test_fasta()
    print(f"Created test FASTA file: {input_fasta}")
    
    # Create temporary output files
    fd_spd, output_spd = tempfile.mkstemp(suffix='.spd')
    os.close(fd_spd)
    
    fd_key, output_key = tempfile.mkstemp(suffix='.key')
    os.close(fd_key)
    
    fd_out, output_fasta = tempfile.mkstemp(suffix='.fasta')
    os.close(fd_out)
    
    try:
        # Encrypt the FASTA file
        print("\nEncrypting FASTA file...")
        encrypt_fasta(input_fasta, output_spd, output_key)
        print(f"Encrypted file size: {os.path.getsize(output_spd)} bytes")
        print(f"Key file size: {os.path.getsize(output_key)} bytes")
        
        # Decrypt the FASTA file
        print("\nDecrypting FASTA file...")
        decrypt_fasta(output_spd, output_key, output_fasta)
        print(f"Decrypted file size: {os.path.getsize(output_fasta)} bytes")
        
        # Compare original and decrypted files
        print("\nComparing original and decrypted files...")
        with open(input_fasta, 'r') as f1, open(output_fasta, 'r') as f2:
            original_content = f1.read()
            decrypted_content = f2.read()
            
            # Remove newlines for comparison (since formatting might differ)
            original_content = original_content.replace('\n', '')
            decrypted_content = decrypted_content.replace('\n', '')
            
            print(f"Files match: {original_content == decrypted_content}")
    
    finally:
        # Clean up temporary files
        for file in [input_fasta, output_spd, output_key, output_fasta]:
            if os.path.exists(file):
                os.remove(file)
        print("\nTemporary files cleaned up.")

if __name__ == "__main__":
    print("=== DNAsecure Basic Usage Example ===")
    
    # Test single sequence encryption/decryption
    test_single_sequence()
    
    # Test FASTA file encryption/decryption
    test_fasta_file()
    
    print("\nAll tests completed.")
