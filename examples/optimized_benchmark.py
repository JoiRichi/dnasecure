#!/usr/bin/env python3
"""
Benchmark comparing original vs. optimized implementation for DNAsecure.

This script tests the performance of the original and optimized implementations
for encrypting and decrypting large DNA sequences.
"""

import os
import sys
import time
import random
import argparse
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)
from dnasecure.core import (
    USE_OPTIMIZED_IMPLEMENTATION,
    encrypt_large_sequence,
    encrypt_large_sequence_optimized,
    decrypt_large_sequence,
    decrypt_large_sequence_optimized
)

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def benchmark_implementation(sequence_length, chunk_size, security_level=DEFAULT_SECURITY_LEVEL, num_runs=3):
    """
    Benchmark original vs. optimized implementation.
    
    Args:
        sequence_length: Length of the test sequence
        chunk_size: Chunk size to use
        security_level: Security level (number of values to remove)
        num_runs: Number of runs to average over
        
    Returns:
        Dictionary of benchmark results
    """
    print(f"\n=== Benchmarking sequence of length {sequence_length} with chunk size {chunk_size} ===")
    
    # Generate a random DNA sequence
    print("Generating random DNA sequence...")
    sequence = generate_random_dna(sequence_length)
    
    results = {
        'sequence_length': sequence_length,
        'chunk_size': chunk_size,
        'security_level': security_level,
        'original_encrypt_time': 0,
        'optimized_encrypt_time': 0,
        'original_decrypt_time': 0,
        'optimized_decrypt_time': 0,
        'original_data_size': 0,
        'optimized_data_size': 0
    }
    
    # Test original implementation
    print("\nTesting original implementation...")
    
    # Temporarily disable optimized implementation
    from dnasecure.core import USE_OPTIMIZED_IMPLEMENTATION as orig_flag
    import dnasecure.core
    dnasecure.core.USE_OPTIMIZED_IMPLEMENTATION = False
    
    original_encrypt_times = []
    original_decrypt_times = []
    
    for run in range(num_runs):
        print(f"  Run {run+1}/{num_runs}...")
        
        # Encrypt
        start_time = time.time()
        encrypted_data, removed_values = encrypt_sequence(sequence, security_level, chunk_size)
        encrypt_time = time.time() - start_time
        original_encrypt_times.append(encrypt_time)
        
        if run == 0:
            results['original_data_size'] = len(encrypted_data)
            
            # Save the first run's results for verification
            original_encrypted_data = encrypted_data
            original_removed_values = removed_values
        
        # Decrypt
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        decrypt_time = time.time() - start_time
        original_decrypt_times.append(decrypt_time)
        
        # Verify
        if decrypted_sequence != sequence:
            print("  ERROR: Original implementation failed to correctly decrypt the sequence!")
    
    # Calculate average times
    results['original_encrypt_time'] = sum(original_encrypt_times) / len(original_encrypt_times)
    results['original_decrypt_time'] = sum(original_decrypt_times) / len(original_decrypt_times)
    
    print(f"  Average encryption time: {results['original_encrypt_time']:.4f} seconds")
    print(f"  Average decryption time: {results['original_decrypt_time']:.4f} seconds")
    print(f"  Encrypted data size: {results['original_data_size']} bytes")
    
    # Test optimized implementation
    print("\nTesting optimized implementation...")
    
    # Enable optimized implementation
    dnasecure.core.USE_OPTIMIZED_IMPLEMENTATION = True
    
    optimized_encrypt_times = []
    optimized_decrypt_times = []
    
    for run in range(num_runs):
        print(f"  Run {run+1}/{num_runs}...")
        
        # Encrypt
        start_time = time.time()
        encrypted_data, removed_values = encrypt_sequence(sequence, security_level, chunk_size)
        encrypt_time = time.time() - start_time
        optimized_encrypt_times.append(encrypt_time)
        
        if run == 0:
            results['optimized_data_size'] = len(encrypted_data)
            
            # Verify that the optimized implementation produces compatible output
            if len(encrypted_data) != len(original_encrypted_data):
                print(f"  NOTE: Optimized implementation produced different sized output: {len(encrypted_data)} vs {len(original_encrypted_data)} bytes")
        
        # Decrypt
        start_time = time.time()
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        decrypt_time = time.time() - start_time
        optimized_decrypt_times.append(decrypt_time)
        
        # Verify
        if decrypted_sequence != sequence:
            print("  ERROR: Optimized implementation failed to correctly decrypt the sequence!")
            
        # Also verify cross-compatibility
        if run == 0:
            try:
                # Try decrypting original data with optimized implementation
                cross_decrypted = decrypt_sequence(original_encrypted_data, original_removed_values)
                if cross_decrypted != sequence:
                    print("  WARNING: Optimized implementation cannot correctly decrypt data from original implementation!")
            except Exception as e:
                print(f"  ERROR in cross-compatibility test: {e}")
    
    # Calculate average times
    results['optimized_encrypt_time'] = sum(optimized_encrypt_times) / len(optimized_encrypt_times)
    results['optimized_decrypt_time'] = sum(optimized_decrypt_times) / len(optimized_decrypt_times)
    
    print(f"  Average encryption time: {results['optimized_encrypt_time']:.4f} seconds")
    print(f"  Average decryption time: {results['optimized_decrypt_time']:.4f} seconds")
    print(f"  Encrypted data size: {results['optimized_data_size']} bytes")
    
    # Calculate speedup
    encrypt_speedup = results['original_encrypt_time'] / results['optimized_encrypt_time']
    decrypt_speedup = results['original_decrypt_time'] / results['optimized_decrypt_time']
    
    print("\nResults:")
    print(f"  Encryption speedup: {encrypt_speedup:.2f}x")
    print(f"  Decryption speedup: {decrypt_speedup:.2f}x")
    
    # Restore original flag
    dnasecure.core.USE_OPTIMIZED_IMPLEMENTATION = orig_flag
    
    return results

def benchmark_sequence_lengths(lengths, chunk_size=DEFAULT_CHUNK_SIZE, security_level=DEFAULT_SECURITY_LEVEL, num_runs=3):
    """
    Benchmark different sequence lengths.
    
    Args:
        lengths: List of sequence lengths to test
        chunk_size: Chunk size to use
        security_level: Security level (number of values to remove)
        num_runs: Number of runs to average over
        
    Returns:
        List of benchmark results
    """
    results = []
    
    for length in lengths:
        result = benchmark_implementation(length, chunk_size, security_level, num_runs)
        results.append(result)
    
    return results

def benchmark_chunk_sizes(sequence_length, chunk_sizes, security_level=DEFAULT_SECURITY_LEVEL, num_runs=3):
    """
    Benchmark different chunk sizes.
    
    Args:
        sequence_length: Length of the test sequence
        chunk_sizes: List of chunk sizes to test
        security_level: Security level (number of values to remove)
        num_runs: Number of runs to average over
        
    Returns:
        List of benchmark results
    """
    results = []
    
    for chunk_size in chunk_sizes:
        result = benchmark_implementation(sequence_length, chunk_size, security_level, num_runs)
        results.append(result)
    
    return results

def plot_sequence_length_results(results, output_file=None):
    """
    Plot benchmark results for different sequence lengths.
    
    Args:
        results: List of benchmark results
        output_file: Path to save the plot (optional)
    """
    lengths = [result['sequence_length'] for result in results]
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot encryption times
    ax1.plot(lengths, [result['original_encrypt_time'] for result in results], 'o-', label='Original')
    ax1.plot(lengths, [result['optimized_encrypt_time'] for result in results], 's-', label='Optimized')
    ax1.set_xlabel('Sequence Length (bases)')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Encryption Time vs. Sequence Length')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True)
    ax1.legend()
    
    # Plot decryption times
    ax2.plot(lengths, [result['original_decrypt_time'] for result in results], 'o-', label='Original')
    ax2.plot(lengths, [result['optimized_decrypt_time'] for result in results], 's-', label='Optimized')
    ax2.set_xlabel('Sequence Length (bases)')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Decryption Time vs. Sequence Length')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def plot_chunk_size_results(results, output_file=None):
    """
    Plot benchmark results for different chunk sizes.
    
    Args:
        results: List of benchmark results
        output_file: Path to save the plot (optional)
    """
    chunk_sizes = [result['chunk_size'] for result in results]
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot encryption times
    ax1.plot(chunk_sizes, [result['original_encrypt_time'] for result in results], 'o-', label='Original')
    ax1.plot(chunk_sizes, [result['optimized_encrypt_time'] for result in results], 's-', label='Optimized')
    ax1.set_xlabel('Chunk Size (bases)')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Encryption Time vs. Chunk Size')
    ax1.set_xscale('log')
    ax1.grid(True)
    ax1.legend()
    
    # Plot decryption times
    ax2.plot(chunk_sizes, [result['original_decrypt_time'] for result in results], 'o-', label='Original')
    ax2.plot(chunk_sizes, [result['optimized_decrypt_time'] for result in results], 's-', label='Optimized')
    ax2.set_xlabel('Chunk Size (bases)')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Decryption Time vs. Chunk Size')
    ax2.set_xscale('log')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark original vs. optimized implementation for DNAsecure",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--test",
        choices=["length", "chunk"],
        default="length",
        help="Test to run: 'length' for different sequence lengths, 'chunk' for different chunk sizes"
    )
    
    parser.add_argument(
        "--lengths",
        type=int,
        nargs="+",
        default=[10000, 50000, 100000, 500000],
        help="Sequence lengths to test"
    )
    
    parser.add_argument(
        "--chunk-sizes",
        type=int,
        nargs="+",
        default=[1000, 5000, 10000, 50000],
        help="Chunk sizes to test"
    )
    
    parser.add_argument(
        "--sequence-length",
        type=int,
        default=100000,
        help="Sequence length to use for chunk size test"
    )
    
    parser.add_argument(
        "--security-level",
        type=int,
        default=DEFAULT_SECURITY_LEVEL,
        help="Security level (number of values to remove)"
    )
    
    parser.add_argument(
        "--num-runs",
        type=int,
        default=3,
        help="Number of runs to average over"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save the plot"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    if args.test == "length":
        print(f"Benchmarking different sequence lengths: {args.lengths}")
        results = benchmark_sequence_lengths(
            args.lengths,
            chunk_size=DEFAULT_CHUNK_SIZE,
            security_level=args.security_level,
            num_runs=args.num_runs
        )
        plot_sequence_length_results(results, args.output)
    else:
        print(f"Benchmarking different chunk sizes: {args.chunk_sizes}")
        results = benchmark_chunk_sizes(
            args.sequence_length,
            args.chunk_sizes,
            security_level=args.security_level,
            num_runs=args.num_runs
        )
        plot_chunk_size_results(results, args.output)

if __name__ == "__main__":
    main() 