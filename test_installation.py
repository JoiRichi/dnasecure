#!/usr/bin/env python3
"""
Test script for the dnasecure package.
This script tests the basic functionality of the dnasecure package.
"""

import dnasecure
import tempfile
import os

def test_basic_functionality():
    """Test basic encryption and decryption of a DNA sequence."""
    print("Testing dnasecure version:", dnasecure.__version__)
    
    # Test sequence
    sequence = "ACGTACGTACGT"
    print(f"Original sequence: {sequence}")
    
    # Encrypt the sequence
    print("Encrypting sequence...")
    encrypted_data, removed_values = dnasecure.encrypt_sequence(sequence)
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    
    # Decrypt the sequence
    print("Decrypting sequence...")
    decrypted_sequence = dnasecure.decrypt_sequence(encrypted_data, removed_values)
    print(f"Decrypted sequence: {decrypted_sequence}")
    
    # Verify the result
    if sequence == decrypted_sequence:
        print("SUCCESS: Original and decrypted sequences match")
    else:
        print("ERROR: Original and decrypted sequences do not match")
    
    return sequence == decrypted_sequence

def test_empty_sequence():
    """Test encryption and decryption of an empty sequence."""
    print("\nTesting empty sequence...")
    
    # Empty sequence
    sequence = ""
    print(f"Original sequence: '{sequence}' (empty)")
    
    # Encrypt the sequence
    print("Encrypting sequence...")
    encrypted_data, removed_values = dnasecure.encrypt_sequence(sequence)
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Removed values: {removed_values}")
    
    # Decrypt the sequence
    print("Decrypting sequence...")
    decrypted_sequence = dnasecure.decrypt_sequence(encrypted_data, removed_values)
    print(f"Decrypted sequence: '{decrypted_sequence}' (empty)")
    
    # Verify the result
    if sequence == decrypted_sequence:
        print("SUCCESS: Empty sequence test passed")
    else:
        print("ERROR: Empty sequence test failed")
    
    return sequence == decrypted_sequence

def test_fasta_functionality():
    """Test encryption and decryption of a FASTA file."""
    print("\nTesting FASTA functionality...")
    
    # Create a temporary FASTA file
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as f:
        fasta_path = f.name
        f.write(b">Sequence1\n")
        f.write(b"ACGTACGTACGT\n")
        f.write(b">Sequence2\n")
        f.write(b"TGCATGCATGCA\n")
    
    # Create output files
    fd, spd_path = tempfile.mkstemp(suffix='.spd')
    os.close(fd)
    
    fd, key_path = tempfile.mkstemp(suffix='.key')
    os.close(fd)
    
    fd, decrypted_path = tempfile.mkstemp(suffix='.decrypted.fasta')
    os.close(fd)
    
    try:
        # Encrypt the FASTA file
        print(f"Encrypting FASTA file: {fasta_path}")
        dnasecure.encrypt_fasta(fasta_path, spd_path, key_path)
        
        # Decrypt the FASTA file
        print(f"Decrypting to: {decrypted_path}")
        dnasecure.decrypt_fasta(spd_path, key_path, decrypted_path)
        
        # Verify the result
        print("Verifying result...")
        with open(fasta_path, 'r') as f:
            original_content = f.read()
        
        with open(decrypted_path, 'r') as f:
            decrypted_content = f.read()
        
        # Compare the content (ignoring whitespace differences)
        original_lines = [line.strip() for line in original_content.split('\n') if line.strip()]
        decrypted_lines = [line.strip() for line in decrypted_content.split('\n') if line.strip()]
        
        if len(original_lines) == len(decrypted_lines):
            all_match = True
            for i in range(len(original_lines)):
                if original_lines[i] != decrypted_lines[i]:
                    if original_lines[i].startswith('>') and decrypted_lines[i].startswith('>'):
                        # Headers might have additional information, just check if they start the same
                        if original_lines[i].split()[0] != decrypted_lines[i].split()[0]:
                            all_match = False
                            break
                    elif not original_lines[i].startswith('>') and not decrypted_lines[i].startswith('>'):
                        # For sequences, they should match exactly
                        all_match = False
                        break
            
            if all_match:
                print("SUCCESS: FASTA test passed")
            else:
                print("ERROR: FASTA test failed - content mismatch")
        else:
            print(f"ERROR: FASTA test failed - line count mismatch ({len(original_lines)} vs {len(decrypted_lines)})")
    
    finally:
        # Clean up temporary files
        for file_path in [fasta_path, spd_path, key_path, decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    print("=== DNASecure Installation Test ===\n")
    
    basic_test_passed = test_basic_functionality()
    empty_test_passed = test_empty_sequence()
    test_fasta_functionality()
    
    print("\n=== Test Summary ===")
    print(f"Basic Functionality: {'PASSED' if basic_test_passed else 'FAILED'}")
    print(f"Empty Sequence: {'PASSED' if empty_test_passed else 'FAILED'}")
    
    print("\nIf all tests passed, the dnasecure package is installed correctly!") 