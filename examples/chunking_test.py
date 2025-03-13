#!/usr/bin/env python3
"""
Test script for the chunking approach to handle large DNA sequences.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    DEFAULT_SECURITY_LEVEL
)

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def test_sequence(length):
    """Test encryption and decryption of a DNA sequence of the given length."""
    print(f"\n=== Testing Sequence of Length {length} ===")
    
    # Generate a random DNA sequence
    print(f"Generating random DNA sequence...")
    sequence = generate_random_dna(length)
    
    # Encrypt the sequence
    print(f"Encrypting sequence...")
    start_time = time.time()
    try:
        encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=DEFAULT_SECURITY_LEVEL)
        encryption_time = time.time() - start_time
        
        print(f"Encryption time: {encryption_time:.4f} seconds")
        print(f"Encrypted data size: {len(encrypted_data)} bytes")
        print(f"Type of removed values: {type(removed_values)}")
        
        if isinstance(removed_values, list) and len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][0], int) and isinstance(removed_values[0][1], list):
            print(f"Chunked sequence detected with {len(removed_values)} chunks")
        else:
            print(f"Regular sequence with {len(removed_values)} removed values")
        
        # Decrypt the sequence
        print(f"Decrypting sequence...")
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        decryption_time = time.time() - start_time
        
        print(f"Decryption time: {decryption_time:.4f} seconds")
        
        # Verify the decryption
        is_correct = sequence == decrypted_sequence
        print(f"Decryption successful: {is_correct}")
        
        if not is_correct:
            print(f"Original sequence length: {len(sequence)}")
            print(f"Decrypted sequence length: {len(decrypted_sequence)}")
            
            # Find the first difference
            for i in range(min(len(sequence), len(decrypted_sequence))):
                if sequence[i] != decrypted_sequence[i]:
                    print(f"First difference at position {i}: {sequence[i]} vs {decrypted_sequence[i]}")
                    break
        
        return is_correct
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== DNAsecure Chunking Test ===")
    
    # Test with increasing sequence lengths
    lengths = [50, 150, 500, 1000, 5000]
    
    for length in lengths:
        success = test_sequence(length)
        if not success:
            print(f"Test failed at length {length}")
            break
    
    print("\nAll tests completed.") 