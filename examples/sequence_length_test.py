#!/usr/bin/env python3
"""
Test script for DNAsecure to verify that sequences of any length
can be encrypted and decrypted correctly.
"""

import os
import random
import time
from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    encrypt_fasta,
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

def generate_random_dna(length):
    """Generate a random DNA sequence of specified length"""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def test_sequence_length(length, security_level=DEFAULT_SECURITY_LEVEL, chunk_size=DEFAULT_CHUNK_SIZE):
    """Test encryption and decryption of a sequence with specific length"""
    print(f"\nTesting sequence of length {length} (security level: {security_level}, chunk size: {chunk_size})")
    
    # Generate a random sequence
    sequence = generate_random_dna(length)
    
    # Measure encryption time
    start_time = time.time()
    encrypted_data, removed_values = encrypt_sequence(
        sequence, 
        num_removed=security_level, 
        chunk_size=chunk_size
    )
    encryption_time = time.time() - start_time
    
    # Check if chunking was used
    is_chunked = False
    num_chunks = 1
    if len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][1], list):
        is_chunked = True
        num_chunks = len(removed_values)
        print(f"Sequence was chunked into {num_chunks} chunks")
    
    # Measure decryption time
    start_time = time.time()
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    decryption_time = time.time() - start_time
    
    # Verify the result
    if sequence == decrypted_sequence:
        print(f"✓ Success! Sequence of length {length} was correctly encrypted and decrypted")
        print(f"  Encryption time: {encryption_time:.4f}s, Decryption time: {decryption_time:.4f}s")
        print(f"  Encrypted data size: {len(encrypted_data)} bytes")
        print(f"  Key size: {len(str(removed_values))} characters")
        return True
    else:
        print(f"× Failure! Decrypted sequence does not match original for length {length}")
        
        # Try to find where they differ
        if len(sequence) == len(decrypted_sequence):
            mismatch_count = sum(1 for a, b in zip(sequence, decrypted_sequence) if a != b)
            print(f"  Sequences have same length but differ in {mismatch_count} positions")
            
            # Show a sample of differences if there are many
            if mismatch_count > 0:
                for i in range(min(5, mismatch_count)):
                    pos = next(j for j in range(len(sequence)) if sequence[j] != decrypted_sequence[j])
                    print(f"  Difference at position {pos}: {sequence[pos]} vs {decrypted_sequence[pos]}")
        else:
            print(f"  Length mismatch: original={len(sequence)}, decrypted={len(decrypted_sequence)}")
            
            # Check if one is a substring of the other
            if sequence in decrypted_sequence:
                print("  Original sequence is contained within decrypted sequence")
            elif decrypted_sequence in sequence:
                print("  Decrypted sequence is contained within original sequence")
        
        return False

def test_various_lengths():
    """Test a wide range of sequence lengths"""
    print("=== Testing Various Sequence Lengths ===")
    
    # Test very short sequences
    short_lengths = [1, 2, 3, 4, 5, 10, 20]
    
    # Test medium-sized sequences
    medium_lengths = [50, 100, 500, 1000]
    
    # Test sequences around chunk boundaries
    chunk_boundary_lengths = [
        DEFAULT_CHUNK_SIZE - 1,
        DEFAULT_CHUNK_SIZE,
        DEFAULT_CHUNK_SIZE + 1,
        DEFAULT_CHUNK_SIZE * 2 - 1,
        DEFAULT_CHUNK_SIZE * 2,
        DEFAULT_CHUNK_SIZE * 2 + 1
    ]
    
    # Test long sequences
    long_lengths = [20000, 50000, 100000]
    
    # Combine all test lengths
    all_lengths = short_lengths + medium_lengths + chunk_boundary_lengths + long_lengths
    
    # Track results
    results = {}
    
    for length in all_lengths:
        success = test_sequence_length(length)
        results[length] = success
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total tests: {len(all_lengths)}")
    successful_tests = sum(1 for success in results.values() if success)
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {len(all_lengths) - successful_tests}")
    
    if len(all_lengths) - successful_tests > 0:
        print("\nFailed lengths:")
        for length, success in results.items():
            if not success:
                print(f"  - {length}")
    
    return successful_tests == len(all_lengths)

def test_custom_chunk_sizes():
    """Test different chunk sizes with the same sequence"""
    print("\n=== Testing Custom Chunk Sizes ===")
    
    # Use a fixed sequence length
    sequence_length = 50000
    
    # Test different chunk sizes
    chunk_sizes = [100, 500, 1000, 5000, 10000, 20000]
    
    # Track results
    results = {}
    
    for chunk_size in chunk_sizes:
        success = test_sequence_length(sequence_length, chunk_size=chunk_size)
        results[chunk_size] = success
    
    # Print summary
    print("\n=== Chunk Size Summary ===")
    print(f"Sequence length: {sequence_length}")
    print(f"Total tests: {len(chunk_sizes)}")
    successful_tests = sum(1 for success in results.values() if success)
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {len(chunk_sizes) - successful_tests}")
    
    if len(chunk_sizes) - successful_tests > 0:
        print("\nFailed chunk sizes:")
        for chunk_size, success in results.items():
            if not success:
                print(f"  - {chunk_size}")
    
    return successful_tests == len(chunk_sizes)

def test_security_levels():
    """Test different security levels"""
    print("\n=== Testing Security Levels ===")
    
    # Use a fixed sequence length
    sequence_length = 1000
    
    # Test different security levels
    security_levels = [1, 3, 5, 10, 20]
    
    # Track results
    results = {}
    
    for security_level in security_levels:
        success = test_sequence_length(sequence_length, security_level=security_level)
        results[security_level] = success
    
    # Print summary
    print("\n=== Security Level Summary ===")
    print(f"Sequence length: {sequence_length}")
    print(f"Total tests: {len(security_levels)}")
    successful_tests = sum(1 for success in results.values() if success)
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {len(security_levels) - successful_tests}")
    
    if len(security_levels) - successful_tests > 0:
        print("\nFailed security levels:")
        for security_level, success in results.items():
            if not success:
                print(f"  - {security_level}")
    
    return successful_tests == len(security_levels)

def main():
    """Run all tests"""
    print("=== DNAsecure Sequence Length Test ===")
    print(f"Default security level: {DEFAULT_SECURITY_LEVEL}")
    print(f"Default chunk size: {DEFAULT_CHUNK_SIZE}")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run tests
    length_test_success = test_various_lengths()
    chunk_size_test_success = test_custom_chunk_sizes()
    security_level_test_success = test_security_levels()
    
    # Overall result
    if length_test_success and chunk_size_test_success and security_level_test_success:
        print("\n✓ All tests passed! DNAsecure can handle sequences of any length.")
    else:
        print("\n× Some tests failed. See details above.")

if __name__ == "__main__":
    main() 