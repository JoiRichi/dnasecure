#!/usr/bin/env python3
"""
Simple benchmark for parallel vs. sequential processing in DNAsecure.
"""

import os
import time
from dnasecure import encrypt_fasta, decrypt_fasta

def main():
    """Main entry point for the script."""
    input_fasta = "test_large.fasta"
    
    # Test sequential processing
    print("Testing sequential processing...")
    
    # Sequential encryption
    output_spd_seq = "test_large_seq.spd"
    output_key_seq = "test_large_seq.key"
    
    start_time = time.time()
    encrypt_fasta(
        input_fasta,
        output_spd_seq,
        output_key_seq,
        num_removed=5,
        parallel=False
    )
    seq_encrypt_time = time.time() - start_time
    print(f"Sequential encryption time: {seq_encrypt_time:.2f} seconds")
    
    # Sequential decryption
    output_fasta_seq = "test_large_seq_decrypted.fasta"
    
    start_time = time.time()
    decrypt_fasta(
        output_spd_seq,
        output_key_seq,
        output_fasta_seq,
        parallel=False
    )
    seq_decrypt_time = time.time() - start_time
    print(f"Sequential decryption time: {seq_decrypt_time:.2f} seconds")
    
    # Test parallel processing
    print("\nTesting parallel processing...")
    
    # Parallel encryption
    output_spd_par = "test_large_par.spd"
    output_key_par = "test_large_par.key"
    
    start_time = time.time()
    encrypt_fasta(
        input_fasta,
        output_spd_par,
        output_key_par,
        num_removed=5,
        parallel=True
    )
    par_encrypt_time = time.time() - start_time
    print(f"Parallel encryption time: {par_encrypt_time:.2f} seconds")
    
    # Parallel decryption
    output_fasta_par = "test_large_par_decrypted.fasta"
    
    start_time = time.time()
    decrypt_fasta(
        output_spd_par,
        output_key_par,
        output_fasta_par,
        parallel=True
    )
    par_decrypt_time = time.time() - start_time
    print(f"Parallel decryption time: {par_decrypt_time:.2f} seconds")
    
    # Print summary
    print("\nSummary:")
    print(f"Sequential encryption time: {seq_encrypt_time:.2f} seconds")
    print(f"Parallel encryption time: {par_encrypt_time:.2f} seconds")
    print(f"Speedup: {seq_encrypt_time / par_encrypt_time:.2f}x")
    
    print(f"Sequential decryption time: {seq_decrypt_time:.2f} seconds")
    print(f"Parallel decryption time: {par_decrypt_time:.2f} seconds")
    print(f"Speedup: {seq_decrypt_time / par_decrypt_time:.2f}x")
    
    # Clean up
    for file in [output_spd_seq, output_key_seq, output_fasta_seq, 
                 output_spd_par, output_key_par, output_fasta_par]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    main() 