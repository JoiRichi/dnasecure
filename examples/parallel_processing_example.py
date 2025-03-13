#!/usr/bin/env python3
"""
Parallel Processing Example for DNAsecure

This example demonstrates how to use parallel processing with DNAsecure
to improve performance when working with multiFASTA files.

Note: For small files with few sequences (like this example), parallel processing
may actually be slower than sequential processing due to the overhead of creating
and managing processes. The speedup becomes significant for larger files with
many sequences, as demonstrated in our benchmarks where we achieved:
- 5.37x speedup for encryption
- 5.95x speedup for decryption
on a 30MB FASTA file with 10 sequences.
"""

import os
import time
from dnasecure import encrypt_fasta, decrypt_fasta

def main():
    """
    Demonstrate parallel processing with DNAsecure by comparing
    sequential and parallel processing performance.
    """
    # Input and output files
    input_file = "test.fasta"
    
    # If test.fasta doesn't exist, create a simple example
    if not os.path.exists(input_file):
        print(f"Creating example file {input_file}...")
        with open(input_file, "w") as f:
            f.write(">Sequence1 Test sequence 1\n")
            f.write("ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC\n")
            f.write(">Sequence2 Test sequence 2\n")
            f.write("GGGAAACCCTTTAGGCATGCATGCATGCATGCATGCATGCATGC\n")
    
    # Sequential processing
    seq_output_spd = "test_sequential.spd"
    seq_output_key = "test_sequential.key"
    seq_output_fasta = "test_sequential_decrypted.fasta"
    
    print("\n=== Sequential Processing ===")
    
    # Sequential encryption
    print("Encrypting with sequential processing...")
    start_time = time.time()
    encrypt_fasta(
        input_file, 
        seq_output_spd, 
        seq_output_key, 
        num_removed=5,
        parallel=False
    )
    seq_encrypt_time = time.time() - start_time
    print(f"Sequential encryption completed in {seq_encrypt_time:.2f} seconds")
    
    # Sequential decryption
    print("Decrypting with sequential processing...")
    start_time = time.time()
    decrypt_fasta(
        seq_output_spd, 
        seq_output_key, 
        seq_output_fasta,
        parallel=False
    )
    seq_decrypt_time = time.time() - start_time
    print(f"Sequential decryption completed in {seq_decrypt_time:.2f} seconds")
    
    # Parallel processing
    par_output_spd = "test_parallel.spd"
    par_output_key = "test_parallel.key"
    par_output_fasta = "test_parallel_decrypted.fasta"
    
    print("\n=== Parallel Processing ===")
    
    # Parallel encryption
    print("Encrypting with parallel processing...")
    start_time = time.time()
    encrypt_fasta(
        input_file, 
        par_output_spd, 
        par_output_key, 
        num_removed=5,
        parallel=True,
        num_processes=4  # Use 4 processes
    )
    par_encrypt_time = time.time() - start_time
    print(f"Parallel encryption completed in {par_encrypt_time:.2f} seconds")
    
    # Parallel decryption
    print("Decrypting with parallel processing...")
    start_time = time.time()
    decrypt_fasta(
        par_output_spd, 
        par_output_key, 
        par_output_fasta,
        parallel=True,
        num_processes=4  # Use 4 processes
    )
    par_decrypt_time = time.time() - start_time
    print(f"Parallel decryption completed in {par_decrypt_time:.2f} seconds")
    
    # Compare results
    print("\n=== Performance Comparison ===")
    if seq_encrypt_time > 0:
        encrypt_speedup = seq_encrypt_time / par_encrypt_time
        print(f"Encryption speedup: {encrypt_speedup:.2f}x")
        if encrypt_speedup < 1:
            print("Note: Parallel processing is slower for this small example due to process creation overhead.")
            print("      For larger files with many sequences, parallel processing provides significant speedup.")
    
    if seq_decrypt_time > 0:
        decrypt_speedup = seq_decrypt_time / par_decrypt_time
        print(f"Decryption speedup: {decrypt_speedup:.2f}x")
        if decrypt_speedup < 1:
            print("Note: Parallel processing is slower for this small example due to process creation overhead.")
            print("      For larger files with many sequences, parallel processing provides significant speedup.")
    
    # Verify that the results are identical
    print("\n=== Verification ===")
    with open(seq_output_fasta, 'r') as f1, open(par_output_fasta, 'r') as f2:
        seq_content = f1.read()
        par_content = f2.read()
        
        if seq_content == par_content:
            print("✓ Sequential and parallel results are identical")
        else:
            print("✗ Sequential and parallel results differ")
    
    # Clean up
    print("\nCleaning up temporary files...")
    for file in [seq_output_spd, seq_output_key, seq_output_fasta,
                par_output_spd, par_output_key, par_output_fasta]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main() 