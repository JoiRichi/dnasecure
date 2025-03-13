#!/usr/bin/env python3
"""
Benchmark parallel vs. sequential processing for DNAsecure.
"""

import os
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np
from dnasecure import encrypt_fasta, decrypt_fasta

def run_benchmark(input_fasta, num_processes_list, security_level=5):
    """
    Run benchmark tests for different numbers of processes.
    
    Args:
        input_fasta: Path to input FASTA file
        num_processes_list: List of number of processes to test
        security_level: Security level for encryption
        
    Returns:
        Dictionary of benchmark results
    """
    results = {
        'encrypt_times': [],
        'decrypt_times': [],
        'num_processes': num_processes_list
    }
    
    # Create temporary output files
    output_spd = 'benchmark_output.spd'
    output_key = 'benchmark_output.key'
    output_fasta = 'benchmark_output.fasta'
    
    try:
        # Run benchmarks for each number of processes
        for num_processes in num_processes_list:
            print(f"\nBenchmarking with {num_processes} processes:")
            
            # Benchmark encryption
            print(f"  Encrypting with {num_processes} processes...")
            start_time = time.time()
            encrypt_fasta(
                input_fasta,
                output_spd,
                output_key,
                security_level,
                parallel=(num_processes > 0),
                num_processes=num_processes if num_processes > 0 else None
            )
            encrypt_time = time.time() - start_time
            results['encrypt_times'].append(encrypt_time)
            print(f"  Encryption time: {encrypt_time:.2f} seconds")
            
            # Benchmark decryption
            print(f"  Decrypting with {num_processes} processes...")
            start_time = time.time()
            decrypt_fasta(
                output_spd,
                output_key,
                output_fasta,
                parallel=(num_processes > 0),
                num_processes=num_processes if num_processes > 0 else None
            )
            decrypt_time = time.time() - start_time
            results['decrypt_times'].append(decrypt_time)
            print(f"  Decryption time: {decrypt_time:.2f} seconds")
            
        return results
    
    finally:
        # Clean up temporary files
        for file in [output_spd, output_key, output_fasta]:
            if os.path.exists(file):
                os.remove(file)

def plot_results(results, output_file=None):
    """
    Plot benchmark results.
    
    Args:
        results: Dictionary of benchmark results
        output_file: Path to output plot file
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot encryption times
    ax1.bar(range(len(results['num_processes'])), results['encrypt_times'], color='blue', alpha=0.7)
    ax1.set_xlabel('Number of Processes')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Encryption Time')
    ax1.set_xticks(range(len(results['num_processes'])))
    ax1.set_xticklabels([str(p) if p > 0 else 'Sequential' for p in results['num_processes']])
    
    # Plot decryption times
    ax2.bar(range(len(results['num_processes'])), results['decrypt_times'], color='green', alpha=0.7)
    ax2.set_xlabel('Number of Processes')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Decryption Time')
    ax2.set_xticks(range(len(results['num_processes'])))
    ax2.set_xticklabels([str(p) if p > 0 else 'Sequential' for p in results['num_processes']])
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
        print(f"Plot saved to {output_file}")
    else:
        plt.show()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Benchmark parallel vs. sequential processing for DNAsecure"
    )
    parser.add_argument(
        "input_fasta",
        help="Path to input FASTA file"
    )
    parser.add_argument(
        "--output-plot",
        default="benchmark_results.png",
        help="Path to output plot file (default: benchmark_results.png)"
    )
    parser.add_argument(
        "--security-level",
        type=int,
        default=5,
        help="Security level for encryption (default: 5)"
    )
    parser.add_argument(
        "--max-processes",
        type=int,
        default=None,
        help="Maximum number of processes to test (default: number of CPU cores)"
    )
    
    args = parser.parse_args()
    
    # Determine the number of processes to test
    import multiprocessing
    max_processes = args.max_processes or multiprocessing.cpu_count()
    
    # Create a list of process counts to test
    # Include 0 for sequential processing
    num_processes_list = [0]  # 0 means sequential (no parallel)
    
    # Add powers of 2 up to max_processes
    p = 1
    while p <= max_processes:
        num_processes_list.append(p)
        p *= 2
    
    # Add max_processes if it's not already in the list
    if max_processes not in num_processes_list:
        num_processes_list.append(max_processes)
    
    # Sort the list
    num_processes_list.sort()
    
    print(f"Testing with process counts: {num_processes_list}")
    
    # Run benchmarks
    results = run_benchmark(args.input_fasta, num_processes_list, args.security_level)
    
    # Plot results
    plot_results(results, args.output_plot)
    
    # Print summary
    print("\nSummary:")
    print(f"Sequential encryption time: {results['encrypt_times'][0]:.2f} seconds")
    print(f"Best parallel encryption time: {min(results['encrypt_times'][1:]):.2f} seconds")
    print(f"Speedup: {results['encrypt_times'][0] / min(results['encrypt_times'][1:]):.2f}x")
    
    print(f"Sequential decryption time: {results['decrypt_times'][0]:.2f} seconds")
    print(f"Best parallel decryption time: {min(results['decrypt_times'][1:]):.2f} seconds")
    print(f"Speedup: {results['decrypt_times'][0] / min(results['decrypt_times'][1:]):.2f}x")

if __name__ == "__main__":
    main() 