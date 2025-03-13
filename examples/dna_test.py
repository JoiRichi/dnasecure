#!/usr/bin/env python3
"""
Simple test script for DNA sequence encryption using the original functions.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from selfpowerdecomposer import (
    secure_encode_number_no_placeholder,
    secure_decode_number_no_placeholder
)

# DNA base to number mapping
BASE_TO_NUM = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
NUM_TO_BASE = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: 'N'}

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def dna_to_number(sequence):
    """Convert a DNA sequence to a single large integer."""
    number = 0
    for base in sequence:
        number = number * 5 + BASE_TO_NUM.get(base.upper(), 4)
    return number

def number_to_dna(number, length=None):
    """Convert a number back to a DNA sequence."""
    sequence = []
    while number > 0:
        base_num = number % 5
        sequence.append(NUM_TO_BASE[base_num])
        number //= 5
    
    sequence.reverse()
    
    if length and len(sequence) < length:
        sequence = ['A'] * (length - len(sequence)) + sequence
    
    return ''.join(sequence)

def test_dna_sequence(length):
    """Test encryption and decryption of a DNA sequence."""
    print(f"\n=== Testing DNA Sequence of Length {length} ===")
    
    # Generate a random DNA sequence
    print(f"Generating random DNA sequence...")
    sequence = generate_random_dna(length)
    
    # Convert to number
    print(f"Converting to number...")
    number = dna_to_number(sequence)
    print(f"Number: {number}")
    
    # Encode the number
    print(f"Encoding number...")
    start_time = time.time()
    try:
        encoded_data, removed_values = secure_encode_number_no_placeholder(number, 5)
        encoding_time = time.time() - start_time
        
        print(f"Encoding time: {encoding_time:.4f} seconds")
        print(f"Encoded data size: {len(encoded_data)} bytes")
        print(f"Number of removed values: {len(removed_values)}")
        
        # Decode the number
        print(f"Decoding number...")
        start_time = time.time()
        decoded_number = secure_decode_number_no_placeholder(encoded_data, removed_values)
        decoding_time = time.time() - start_time
        
        print(f"Decoding time: {decoding_time:.4f} seconds")
        
        # Convert back to DNA
        print(f"Converting back to DNA...")
        decoded_sequence = number_to_dna(decoded_number, length)
        
        # Verify the decoding
        is_correct = sequence == decoded_sequence
        print(f"Decoding successful: {is_correct}")
        
        if not is_correct:
            print(f"Original sequence: {sequence[:50]}...")
            print(f"Decoded sequence: {decoded_sequence[:50]}...")
            
            # Find the first difference
            for i in range(min(len(sequence), len(decoded_sequence))):
                if sequence[i] != decoded_sequence[i]:
                    print(f"First difference at position {i}: {sequence[i]} vs {decoded_sequence[i]}")
                    break
        
        return is_correct
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== DNA Sequence Encryption Test ===")
    
    # Test with increasing sequence lengths
    lengths = [10, 100, 1000]
    
    for length in lengths:
        success = test_dna_sequence(length)
        if not success:
            print(f"Test failed at length {length}")
            break
    
    print("\nAll tests completed.") 