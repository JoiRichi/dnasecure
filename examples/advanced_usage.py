#!/usr/bin/env python3
"""
Advanced usage example for the DNAsecure package.

This script demonstrates more advanced features of the DNAsecure package:
1. Working with multiple sequences
2. Different security levels
3. Performance benchmarking
4. Handling large sequences
"""

import os
import sys
import time
import tempfile
import random
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    encrypt_fasta,
    decrypt_fasta,
    dna_to_number,
    number_to_dna,
    DEFAULT_SECURITY_LEVEL
)

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def benchmark_security_levels():
    """Benchmark encryption and decryption with different security levels."""
    print("\n=== Benchmarking Different Security Levels ===")
    
    # Generate a random DNA sequence
    sequence_length = 10000  # Back to original size
    sequence = generate_random_dna(sequence_length)
    print(f"Generated random DNA sequence of length {sequence_length}")
    
    security_levels = [1, 2, 5, 10, 20, 50]  # Restored 50
    encryption_times = []
    decryption_times = []
    file_sizes = []
    
    for level in security_levels:
        print(f"\nTesting security level {level}...")
        
        # Measure encryption time
        start_time = time.time()
        encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=level)
        encryption_time = time.time() - start_time
        encryption_times.append(encryption_time)
        
        file_size = len(encrypted_data)
        file_sizes.append(file_size)
        
        print(f"Encryption time: {encryption_time:.4f} seconds")
        print(f"Encrypted data size: {file_size} bytes")
        print(f"Number of removed values: {len(removed_values)}")
        
        # Measure decryption time
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        decryption_time = time.time() - start_time
        decryption_times.append(decryption_time)
        
        print(f"Decryption time: {decryption_time:.4f} seconds")
        print(f"Decryption successful: {sequence == decrypted_sequence}")
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(security_levels, encryption_times, 'o-', label='Encryption Time')
    plt.xlabel('Security Level (number of removed values)')
    plt.ylabel('Time (seconds)')
    plt.title('Encryption Time vs. Security Level')
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot(security_levels, decryption_times, 'o-', label='Decryption Time')
    plt.xlabel('Security Level (number of removed values)')
    plt.ylabel('Time (seconds)')
    plt.title('Decryption Time vs. Security Level')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(security_levels, file_sizes, 'o-', label='File Size')
    plt.xlabel('Security Level (number of removed values)')
    plt.ylabel('Size (bytes)')
    plt.title('Encrypted File Size vs. Security Level')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    compression_ratio = [sequence_length / (file_size + level * 8) for file_size, level in zip(file_sizes, security_levels)]
    plt.plot(security_levels, compression_ratio, 'o-', label='Compression Ratio')
    plt.xlabel('Security Level (number of removed values)')
    plt.ylabel('Compression Ratio')
    plt.title('Compression Ratio vs. Security Level')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('security_level_benchmark.png')
    print(f"\nBenchmark results saved to security_level_benchmark.png")

def benchmark_sequence_length():
    """Benchmark encryption and decryption with different sequence lengths."""
    print("\n=== Benchmarking Different Sequence Lengths ===")
    
    sequence_lengths = [100, 1000, 10000, 100000]  # Restored original lengths
    encryption_times = []
    decryption_times = []
    file_sizes = []
    
    for length in sequence_lengths:
        print(f"\nTesting sequence length {length}...")
        
        # Generate a random DNA sequence
        sequence = generate_random_dna(length)
        
        # Measure encryption time
        start_time = time.time()
        encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=DEFAULT_SECURITY_LEVEL)
        encryption_time = time.time() - start_time
        encryption_times.append(encryption_time)
        
        file_size = len(encrypted_data)
        file_sizes.append(file_size)
        
        print(f"Encryption time: {encryption_time:.4f} seconds")
        print(f"Encrypted data size: {file_size} bytes")
        
        # Measure decryption time
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        decryption_time = time.time() - start_time
        decryption_times.append(decryption_time)
        
        print(f"Decryption time: {decryption_time:.4f} seconds")
        print(f"Decryption successful: {sequence == decrypted_sequence}")
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(sequence_lengths, encryption_times, 'o-', label='Encryption Time')
    plt.xlabel('Sequence Length (bases)')
    plt.ylabel('Time (seconds)')
    plt.title('Encryption Time vs. Sequence Length')
    plt.xscale('log')
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot(sequence_lengths, decryption_times, 'o-', label='Decryption Time')
    plt.xlabel('Sequence Length (bases)')
    plt.ylabel('Time (seconds)')
    plt.title('Decryption Time vs. Sequence Length')
    plt.xscale('log')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(sequence_lengths, file_sizes, 'o-', label='File Size')
    plt.xlabel('Sequence Length (bases)')
    plt.ylabel('Size (bytes)')
    plt.title('Encrypted File Size vs. Sequence Length')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    compression_ratio = [length / file_size for length, file_size in zip(sequence_lengths, file_sizes)]
    plt.plot(sequence_lengths, compression_ratio, 'o-', label='Compression Ratio')
    plt.xlabel('Sequence Length (bases)')
    plt.ylabel('Compression Ratio')
    plt.title('Compression Ratio vs. Sequence Length')
    plt.xscale('log')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('sequence_length_benchmark.png')
    print(f"\nBenchmark results saved to sequence_length_benchmark.png")

def create_multi_sequence_fasta():
    """Create a temporary FASTA file with multiple sequences of different lengths."""
    fd, path = tempfile.mkstemp(suffix='.fasta')
    with os.fdopen(fd, 'w') as f:
        # Short sequence
        f.write(">Sequence1 Short test sequence\n")
        f.write(f"{generate_random_dna(100)}\n")
        
        # Medium sequence
        f.write(">Sequence2 Medium test sequence\n")
        f.write(f"{generate_random_dna(1000)}\n")  # Restored to 1000
        
        # Long sequence
        f.write(">Sequence3 Long test sequence\n")
        f.write(f"{generate_random_dna(10000)}\n")  # Restored to 10000
    
    return path

def test_multi_sequence_fasta():
    """Test encryption and decryption of a FASTA file with multiple sequences."""
    print("\n=== Testing Multi-Sequence FASTA File ===")
    
    # Create a temporary FASTA file with multiple sequences
    input_fasta = create_multi_sequence_fasta()
    print(f"Created test FASTA file with multiple sequences: {input_fasta}")
    
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
        start_time = time.time()
        encrypt_fasta(input_fasta, output_spd, output_key, num_removed=DEFAULT_SECURITY_LEVEL)
        encryption_time = time.time() - start_time
        
        print(f"Encryption time: {encryption_time:.4f} seconds")
        print(f"Encrypted file size: {os.path.getsize(output_spd)} bytes")
        print(f"Key file size: {os.path.getsize(output_key)} bytes")
        
        # Decrypt the FASTA file
        print("\nDecrypting FASTA file...")
        start_time = time.time()
        decrypt_fasta(output_spd, output_key, output_fasta)
        decryption_time = time.time() - start_time
        
        print(f"Decryption time: {decryption_time:.4f} seconds")
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

def test_very_large_sequence():
    """Test encryption and decryption of a very large DNA sequence."""
    print("\n=== Testing Very Large Sequence ===")
    
    # Generate a very large random DNA sequence (1 million bases)
    sequence_length = 1000000
    print(f"Generating random DNA sequence of length {sequence_length}...")
    sequence = generate_random_dna(sequence_length)
    
    # Encrypt the sequence
    print("\nEncrypting sequence...")
    start_time = time.time()
    encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=DEFAULT_SECURITY_LEVEL)
    encryption_time = time.time() - start_time
    
    print(f"Encryption time: {encryption_time:.4f} seconds")
    print(f"Encrypted data size: {len(encrypted_data)} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    
    # Decrypt the sequence
    print("\nDecrypting sequence...")
    start_time = time.time()
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    decryption_time = time.time() - start_time
    
    print(f"Decryption time: {decryption_time:.4f} seconds")
    
    # Verify the decryption
    print("\nVerifying decryption...")
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

if __name__ == "__main__":
    print("=== DNAsecure Advanced Usage Example ===")
    
    # Test multi-sequence FASTA file
    test_multi_sequence_fasta()
    
    # Benchmark different security levels
    benchmark_security_levels()
    
    # Benchmark different sequence lengths
    benchmark_sequence_length()
    
    # Test very large sequence
    test_very_large_sequence()
    
    print("\nAll tests completed.") 