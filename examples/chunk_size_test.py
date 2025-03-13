#!/usr/bin/env python3
"""
Chunk Size Test for DNAsecure

This script tests the effect of different chunk sizes on encryption and decryption
performance and security.
"""

import os
import time
import random
from dnasecure import encrypt_sequence, decrypt_sequence

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    return ''.join(random.choice('ACGT') for _ in range(length))

def test_chunk_size(sequence_length, chunk_sizes, security_level=5):
    """
    Test different chunk sizes for encryption and decryption.
    
    Args:
        sequence_length: Length of the test sequence
        chunk_sizes: List of chunk sizes to test
        security_level: Security level (number of values to remove)
    """
    # Generate a random DNA sequence
    print(f"Generating random DNA sequence of length {sequence_length}...")
    sequence = generate_random_dna(sequence_length)
    
    results = []
    
    for chunk_size in chunk_sizes:
        print(f"\nTesting chunk size: {chunk_size}")
        
        # Encrypt the sequence
        print("Encrypting...")
        start_time = time.time()
        encrypted_data, removed_values = encrypt_sequence(sequence, security_level, chunk_size)
        encrypt_time = time.time() - start_time
        print(f"Encryption time: {encrypt_time:.2f} seconds")
        
        # Calculate the number of chunks
        num_chunks = (len(sequence) + chunk_size - 1) // chunk_size
        print(f"Number of chunks: {num_chunks}")
        
        # Calculate the total key size
        if num_chunks > 1:
            # For chunked sequences, count the total number of removed values across all chunks
            total_removed = sum(len(chunk_key) for _, chunk_key in removed_values)
        else:
            # For single chunk, count the number of removed values
            total_removed = len(removed_values)
        print(f"Total removed values: {total_removed}")
        print(f"Removed values per chunk: {total_removed / num_chunks:.2f}")
        
        # Calculate the encrypted data size
        encrypted_size = len(encrypted_data)
        print(f"Encrypted data size: {encrypted_size} bytes")
        
        # Decrypt the sequence
        print("Decrypting...")
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(sequence))
        decrypt_time = time.time() - start_time
        print(f"Decryption time: {decrypt_time:.2f} seconds")
        
        # Verify the decryption
        is_correct = decrypted_sequence == sequence
        print(f"Decryption correct: {is_correct}")
        
        # Store the results
        results.append({
            'chunk_size': chunk_size,
            'num_chunks': num_chunks,
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'total_removed': total_removed,
            'removed_per_chunk': total_removed / num_chunks,
            'encrypted_size': encrypted_size,
            'is_correct': is_correct
        })
    
    # Print summary
    print("\nSummary:")
    print(f"{'Chunk Size':<12} {'Chunks':<8} {'Encrypt(s)':<12} {'Decrypt(s)':<12} {'Key Size':<10} {'Data Size':<10}")
    print("-" * 70)
    for result in results:
        print(f"{result['chunk_size']:<12} {result['num_chunks']:<8} {result['encrypt_time']:<12.2f} {result['decrypt_time']:<12.2f} {result['total_removed']:<10} {result['encrypted_size']:<10}")
    
    return results

def main():
    """Main entry point for the script."""
    # Test parameters
    sequence_length = 100000  # 100k bases
    chunk_sizes = [5000, 10000, 20000, 30000, 50000, 100000]  # Different chunk sizes to test
    security_level = 5  # Number of values to remove
    
    # Run the test
    test_chunk_size(sequence_length, chunk_sizes, security_level)

if __name__ == "__main__":
    main() 