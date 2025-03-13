#!/usr/bin/env python3
"""
Custom test script for DNAsecure to test a specific sequence length with custom chunk size
"""

import random
import time
from dnasecure import (
    encrypt_sequence,
    decrypt_sequence
)

def generate_random_dna(length):
    """Generate a random DNA sequence of specified length"""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def test_custom_parameters(sequence_length=50000, chunk_size=30000, security_level=5):
    """Test encryption and decryption with custom parameters"""
    print(f"\nTesting sequence of length {sequence_length} with chunk size {chunk_size} and security level {security_level}")
    
    # Generate a random sequence
    print("Generating random DNA sequence...")
    sequence = generate_random_dna(sequence_length)
    print(f"Generated sequence of length {len(sequence)}")
    
    # Encrypt with custom parameters
    print("Encrypting sequence...")
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
    
    # Decrypt
    print("Decrypting sequence...")
    start_time = time.time()
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    decryption_time = time.time() - start_time
    
    # Print results
    print(f"Encryption time: {encryption_time:.4f}s")
    print(f"Decryption time: {decryption_time:.4f}s")
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Key size: {len(str(removed_values))} characters")
    
    # Verify the result
    if sequence == decrypted_sequence:
        print(f"✓ Success! Sequence was correctly encrypted and decrypted")
        return True
    else:
        print(f"× Failure! Decrypted sequence does not match original")
        
        # Try to find where they differ
        if len(sequence) == len(decrypted_sequence):
            mismatch_count = sum(1 for a, b in zip(sequence, decrypted_sequence) if a != b)
            print(f"  Sequences have same length but differ in {mismatch_count} positions")
        else:
            print(f"  Length mismatch: original={len(sequence)}, decrypted={len(decrypted_sequence)}")
        
        return False

def main():
    """Run the custom test"""
    print("=== DNAsecure Custom Test ===")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run test with custom parameters
    success = test_custom_parameters(
        sequence_length=50000,
        chunk_size=30000,
        security_level=5
    )
    
    # Print overall result
    if success:
        print("\n✓ Test passed! DNAsecure successfully handled the custom parameters.")
    else:
        print("\n× Test failed. See details above.")

if __name__ == "__main__":
    main() 