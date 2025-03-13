#!/usr/bin/env python3
"""
Simple test script for large DNA sequences.
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
    encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=DEFAULT_SECURITY_LEVEL)
    encryption_time = time.time() - start_time
    
    print(f"Encryption time: {encryption_time:.4f} seconds")
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    
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
        # Check where the difference is
        min_len = min(len(sequence), len(decrypted_sequence))
        for i in range(min_len):
            if sequence[i] != decrypted_sequence[i]:
                print(f"First difference at position {i}: {sequence[i]} vs {decrypted_sequence[i]}")
                break
        
        print(f"Original length: {len(sequence)}")
        print(f"Decrypted length: {len(decrypted_sequence)}")
    
    return is_correct

if __name__ == "__main__":
    print("=== DNAsecure Large Sequence Test ===")
    
    # Test with increasing sequence lengths
    lengths = [100, 1000, 10000]
    
    for length in lengths:
        success = test_sequence(length)
        if not success:
            print(f"Test failed at length {length}")
            break
    
    print("\nAll tests completed.") 