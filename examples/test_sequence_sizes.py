#!/usr/bin/env python3
"""
Test script for DNAsecure with different sequence lengths.

This script tests the DNAsecure package with sequences of different lengths
to verify that it can handle small, medium, and large sequences correctly.
"""

import os
import sys
import random
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

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def test_sequence_size(length):
    """Test encryption and decryption of a DNA sequence of the specified length."""
    print(f"\n=== Testing Sequence of Length {length} ===")
    
    # Generate a random DNA sequence
    original_sequence = generate_random_dna(length)
    print(f"Generated random sequence of length {length}")
    
    try:
        # Encrypt the sequence
        print("Encrypting sequence...")
        encrypted_data, removed_values = encrypt_sequence(original_sequence, num_removed=3)
        print(f"Encryption successful! Data size: {len(encrypted_data)} bytes")
        print(f"Number of removed values: {len(removed_values)}")
        
        # Decrypt the sequence
        print("Decrypting sequence...")
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        print(f"Decryption successful! Sequence length: {len(decrypted_sequence)}")
        
        # Verify the result
        if original_sequence == decrypted_sequence:
            print("SUCCESS: Original and decrypted sequences match!")
        else:
            print("ERROR: Original and decrypted sequences do not match!")
            # Print the first 50 characters of each for comparison
            print(f"Original (first 50): {original_sequence[:50]}")
            print(f"Decrypted (first 50): {decrypted_sequence[:50]}")
            
        return original_sequence == decrypted_sequence
    
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def create_test_fasta(sequences):
    """Create a temporary FASTA file with the given sequences."""
    fd, path = tempfile.mkstemp(suffix='.fasta')
    with os.fdopen(fd, 'w') as f:
        for i, seq in enumerate(sequences):
            f.write(f">Sequence{i+1} Test sequence of length {len(seq)}\n")
            # Write sequence with line wrapping at 60 characters
            for j in range(0, len(seq), 60):
                f.write(seq[j:j+60] + "\n")
    return path

def test_fasta_with_mixed_sizes():
    """Test encryption and decryption of a FASTA file with sequences of different sizes."""
    print("\n=== Testing FASTA File with Mixed Sequence Sizes ===")
    
    # Generate sequences of different sizes
    sequences = [
        generate_random_dna(50),    # Small
        generate_random_dna(200),   # Medium
        generate_random_dna(500),   # Large
        generate_random_dna(1000),  # Very large
    ]
    
    # Create a temporary FASTA file
    input_fasta = create_test_fasta(sequences)
    print(f"Created test FASTA file with {len(sequences)} sequences")
    
    # Create temporary output files
    fd_spd, output_spd = tempfile.mkstemp(suffix='.spd')
    os.close(fd_spd)
    
    fd_key, output_key = tempfile.mkstemp(suffix='.key')
    os.close(fd_key)
    
    fd_out, output_fasta = tempfile.mkstemp(suffix='.fasta')
    os.close(fd_out)
    
    try:
        # Encrypt the FASTA file
        print("Encrypting FASTA file...")
        encrypt_fasta(input_fasta, output_spd, output_key)
        print(f"Encryption successful! SPD file size: {os.path.getsize(output_spd)} bytes")
        print(f"Key file size: {os.path.getsize(output_key)} bytes")
        
        # Decrypt the FASTA file
        print("Decrypting FASTA file...")
        decrypt_fasta(output_spd, output_key, output_fasta)
        print(f"Decryption successful! FASTA file size: {os.path.getsize(output_fasta)} bytes")
        
        # Verify the result by comparing the sequences
        original_sequences = []
        with open(input_fasta, 'r') as f:
            current_seq = ""
            for line in f:
                if line.startswith('>'):
                    if current_seq:
                        original_sequences.append(current_seq)
                        current_seq = ""
                else:
                    current_seq += line.strip()
            if current_seq:
                original_sequences.append(current_seq)
        
        decrypted_sequences = []
        with open(output_fasta, 'r') as f:
            current_seq = ""
            for line in f:
                if line.startswith('>'):
                    if current_seq:
                        decrypted_sequences.append(current_seq)
                        current_seq = ""
                else:
                    current_seq += line.strip()
            if current_seq:
                decrypted_sequences.append(current_seq)
        
        if len(original_sequences) != len(decrypted_sequences):
            print(f"ERROR: Number of sequences doesn't match! Original: {len(original_sequences)}, Decrypted: {len(decrypted_sequences)}")
            return False
        
        all_match = True
        for i, (orig, decr) in enumerate(zip(original_sequences, decrypted_sequences)):
            if orig != decr:
                print(f"ERROR: Sequence {i+1} doesn't match!")
                all_match = False
        
        if all_match:
            print("SUCCESS: All sequences match!")
        
        return all_match
    
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    finally:
        # Clean up temporary files
        for file in [input_fasta, output_spd, output_key, output_fasta]:
            if os.path.exists(file):
                os.remove(file)
        print("Temporary files cleaned up.")

if __name__ == "__main__":
    print("=== DNAsecure Sequence Size Test ===")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test individual sequences of different sizes
    sizes = [10, 50, 100, 200, 500, 1000]
    results = {}
    
    for size in sizes:
        results[size] = test_sequence_size(size)
    
    # Test FASTA file with mixed sizes
    results['fasta'] = test_fasta_with_mixed_sizes()
    
    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        if test == 'fasta':
            print(f"FASTA with mixed sizes: {status}")
        else:
            print(f"Sequence length {test}: {status}")
        all_passed = all_passed and passed
    
    print(f"\nOverall result: {'SUCCESS' if all_passed else 'FAILURE'}")
    sys.exit(0 if all_passed else 1) 