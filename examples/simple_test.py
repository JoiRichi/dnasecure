#!/usr/bin/env python3
"""
Simple test script for the selfpowerdecomposer package.
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

def test_number(number):
    """Test encoding and decoding of a number."""
    print(f"\n=== Testing Number: {number} ===")
    
    # Encode the number
    print(f"Encoding number...")
    start_time = time.time()
    encoded_data, removed_values = secure_encode_number_no_placeholder(number, 5)
    encoding_time = time.time() - start_time
    
    print(f"Encoding time: {encoding_time:.4f} seconds")
    print(f"Encoded data size: {len(encoded_data)} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    print(f"Removed values: {removed_values}")
    
    # Decode the number
    print(f"Decoding number...")
    start_time = time.time()
    decoded_number = secure_decode_number_no_placeholder(encoded_data, removed_values)
    decoding_time = time.time() - start_time
    
    print(f"Decoding time: {decoding_time:.4f} seconds")
    print(f"Decoded number: {decoded_number}")
    
    # Verify the decoding
    is_correct = number == decoded_number
    print(f"Decoding successful: {is_correct}")
    
    return is_correct

if __name__ == "__main__":
    print("=== SelfPowerDecomposer Test ===")
    
    # Test with different numbers
    numbers = [
        123456789,
        9876543210,
        12345678901234567890
    ]
    
    for number in numbers:
        success = test_number(number)
        if not success:
            print(f"Test failed for number {number}")
            break
    
    print("\nAll tests completed.") 