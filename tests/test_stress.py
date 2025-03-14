#!/usr/bin/env python3
"""
Stress test for DNASecure package.
Tests the library with very large sequences and various edge cases.
"""

import os
import sys
import time
import random
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure.core import (
    encrypt_sequence,
    decrypt_sequence,
    encrypt_large_sequence,
    decrypt_large_sequence,
    encrypt_sequence_optimized,
    decrypt_sequence_optimized,
    encrypt_fasta,
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    return ''.join(random.choice('ACGT') for _ in range(length))

def test_large_sequence(length, security_level=DEFAULT_SECURITY_LEVEL, chunk_size=DEFAULT_CHUNK_SIZE):
    """Test encryption and decryption of a large sequence."""
    print(f"\n=== Testing sequence of length {length:,} bases ===")
    print(f"Security level: {security_level}, Chunk size: {chunk_size:,}")
    
    # Generate a random sequence
    print("Generating random sequence...")
    sequence = generate_random_dna(length)
    
    # Encrypt the sequence
    print("Encrypting sequence...")
    start_time = time.time()
    encrypted_data, removed_values = encrypt_sequence(sequence, security_level, chunk_size)
    encrypt_time = time.time() - start_time
    print(f"Encryption completed in {encrypt_time:.2f} seconds")
    print(f"Encrypted data size: {len(encrypted_data):,} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    
    # Decrypt the sequence
    print("Decrypting sequence...")
    start_time = time.time()
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(sequence))
    decrypt_time = time.time() - start_time
    print(f"Decryption completed in {decrypt_time:.2f} seconds")
    
    # Verify the result
    print("Verifying result...")
    if sequence == decrypted_sequence:
        print("SUCCESS: Original and decrypted sequences match")
    else:
        print("ERROR: Original and decrypted sequences do not match")
        if len(sequence) == len(decrypted_sequence):
            # Find the first mismatch
            for i in range(len(sequence)):
                if sequence[i] != decrypted_sequence[i]:
                    print(f"First mismatch at position {i}: '{sequence[i]}' vs '{decrypted_sequence[i]}'")
                    break
        else:
            print(f"Length mismatch: Original={len(sequence)}, Decrypted={len(decrypted_sequence)}")
    
    return sequence == decrypted_sequence

def test_optimized_large_sequence(length, security_level=DEFAULT_SECURITY_LEVEL, chunk_size=DEFAULT_CHUNK_SIZE):
    """Test encryption and decryption of a large sequence using optimized functions."""
    print(f"\n=== Testing optimized sequence of length {length:,} bases ===")
    print(f"Security level: {security_level}, Chunk size: {chunk_size:,}")
    
    # Generate a random sequence
    print("Generating random sequence...")
    sequence = generate_random_dna(length)
    
    # Encrypt the sequence
    print("Encrypting sequence (optimized)...")
    start_time = time.time()
    encrypted_data, removed_values = encrypt_sequence_optimized(sequence, security_level, chunk_size)
    encrypt_time = time.time() - start_time
    print(f"Encryption completed in {encrypt_time:.2f} seconds")
    print(f"Encrypted data size: {len(encrypted_data):,} bytes")
    print(f"Number of removed values: {len(removed_values)}")
    
    # Decrypt the sequence
    print("Decrypting sequence (optimized)...")
    start_time = time.time()
    decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values, len(sequence))
    decrypt_time = time.time() - start_time
    print(f"Decryption completed in {decrypt_time:.2f} seconds")
    
    # Verify the result
    print("Verifying result...")
    if sequence == decrypted_sequence:
        print("SUCCESS: Original and decrypted sequences match")
    else:
        print("ERROR: Original and decrypted sequences do not match")
        if len(sequence) == len(decrypted_sequence):
            # Find the first mismatch
            for i in range(len(sequence)):
                if sequence[i] != decrypted_sequence[i]:
                    print(f"First mismatch at position {i}: '{sequence[i]}' vs '{decrypted_sequence[i]}'")
                    break
        else:
            print(f"Length mismatch: Original={len(sequence)}, Decrypted={len(decrypted_sequence)}")
    
    return sequence == decrypted_sequence

def test_large_fasta(num_sequences=5, max_length=100000, security_level=DEFAULT_SECURITY_LEVEL, chunk_size=DEFAULT_CHUNK_SIZE):
    """Test encryption and decryption of a large FASTA file."""
    print(f"\n=== Testing FASTA with {num_sequences} sequences (max length: {max_length:,}) ===")
    print(f"Security level: {security_level}, Chunk size: {chunk_size:,}")
    
    # Create temporary files
    temp_files = []
    
    # Create a temporary FASTA file with multiple sequences
    fd, fasta_path = tempfile.mkstemp(suffix='.fasta')
    os.close(fd)
    temp_files.append(fasta_path)
    
    # Create output files
    fd, spd_path = tempfile.mkstemp(suffix='.spd')
    os.close(fd)
    temp_files.append(spd_path)
    
    fd, key_path = tempfile.mkstemp(suffix='.key')
    os.close(fd)
    temp_files.append(key_path)
    
    fd, decrypted_path = tempfile.mkstemp(suffix='.decrypted.fasta')
    os.close(fd)
    temp_files.append(decrypted_path)
    
    # Generate random DNA sequences
    print("Generating random sequences...")
    sequences = []
    lengths = []
    
    with open(fasta_path, 'w') as f:
        for i in range(num_sequences):
            length = random.randint(1000, max_length)
            lengths.append(length)
            sequence = generate_random_dna(length)
            sequences.append(sequence)
            
            f.write(f">Sequence{i+1} Test sequence {i+1} (length: {length})\n")
            
            # Write the sequence in lines of 70 characters
            for j in range(0, len(sequence), 70):
                f.write(f"{sequence[j:j+70]}\n")
    
    print(f"Created FASTA file with {num_sequences} sequences")
    print(f"Sequence lengths: {', '.join(f'{length:,}' for length in lengths)}")
    
    # Encrypt the FASTA file
    print("\nEncrypting FASTA file...")
    start_time = time.time()
    encrypt_fasta(
        fasta_path, spd_path, key_path,
        num_removed=security_level, chunk_size=chunk_size
    )
    encrypt_time = time.time() - start_time
    print(f"Encryption completed in {encrypt_time:.2f} seconds")
    
    # Get the size of the encrypted files
    spd_size = os.path.getsize(spd_path)
    key_size = os.path.getsize(key_path)
    print(f"Encrypted data size: {spd_size:,} bytes")
    print(f"Key size: {key_size:,} bytes")
    
    # Decrypt the FASTA file
    print("\nDecrypting FASTA file...")
    start_time = time.time()
    decrypt_fasta(spd_path, key_path, decrypted_path)
    decrypt_time = time.time() - start_time
    print(f"Decryption completed in {decrypt_time:.2f} seconds")
    
    # Parse the original FASTA file
    original_sequences = {}
    with open(fasta_path, 'r') as f:
        current_header = None
        current_sequence = []
        
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('>'):
                # Save the previous sequence if it exists
                if current_header is not None:
                    original_sequences[current_header] = ''.join(current_sequence)
                
                # Start a new sequence
                current_header = line[1:]  # Remove the '>' character
                current_sequence = []
            else:
                # Add to the current sequence
                current_sequence.append(line)
        
        # Save the last sequence if it exists
        if current_header is not None:
            original_sequences[current_header] = ''.join(current_sequence)
    
    # Parse the decrypted FASTA file
    decrypted_sequences = {}
    with open(decrypted_path, 'r') as f:
        current_header = None
        current_sequence = []
        
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('>'):
                # Save the previous sequence if it exists
                if current_header is not None:
                    decrypted_sequences[current_header] = ''.join(current_sequence)
                
                # Start a new sequence
                current_header = line[1:]  # Remove the '>' character
                current_sequence = []
            else:
                # Add to the current sequence
                current_sequence.append(line)
        
        # Save the last sequence if it exists
        if current_header is not None:
            decrypted_sequences[current_header] = ''.join(current_sequence)
    
    # Compare the sequences
    print("\nVerifying results...")
    all_match = True
    for header, original_seq in original_sequences.items():
        if header not in decrypted_sequences:
            print(f"ERROR: Header '{header}' not found in decrypted file")
            all_match = False
            continue
        
        decrypted_seq = decrypted_sequences[header]
        if original_seq != decrypted_seq:
            print(f"ERROR: Sequence '{header}' doesn't match")
            print(f"  Original length: {len(original_seq)}")
            print(f"  Decrypted length: {len(decrypted_seq)}")
            if len(original_seq) == len(decrypted_seq):
                # Find the first mismatch
                for i in range(len(original_seq)):
                    if original_seq[i] != decrypted_seq[i]:
                        print(f"  First mismatch at position {i}: '{original_seq[i]}' vs '{decrypted_seq[i]}'")
                        break
            all_match = False
        else:
            print(f"SUCCESS: Sequence '{header}' matches (length: {len(original_seq):,})")
    
    print(f"All sequences match: {all_match}")
    
    # Clean up temporary files
    for file_path in temp_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return all_match

def test_edge_cases():
    """Test various edge cases."""
    print("\n=== Testing Edge Cases ===")
    
    # Test empty sequence
    print("\nTesting empty sequence...")
    empty_seq = ""
    encrypted_data, removed_values = encrypt_sequence(empty_seq)
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    empty_seq_passed = empty_seq == decrypted_sequence
    if empty_seq_passed:
        print("SUCCESS: Empty sequence test passed")
    else:
        print("ERROR: Empty sequence test failed")
    
    # Test very small sequences
    print("\nTesting very small sequences...")
    small_seqs = ["A", "C", "G", "T", "N", "AC", "GT", "ACG", "ACGT"]
    all_small_passed = True
    
    for seq in small_seqs:
        encrypted_data, removed_values = encrypt_sequence(seq)
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(seq))
        if seq != decrypted_sequence:
            print(f"ERROR: Small sequence '{seq}' test failed")
            all_small_passed = False
    
    if all_small_passed:
        print("SUCCESS: All small sequence tests passed")
    
    # Test sequences with non-standard bases
    print("\nTesting sequences with non-standard bases...")
    seq_with_n = "ACGTN" * 10
    encrypted_data, removed_values = encrypt_sequence(seq_with_n)
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(seq_with_n))
    non_standard_passed = seq_with_n == decrypted_sequence
    if non_standard_passed:
        print("SUCCESS: Sequence with non-standard bases test passed")
    else:
        print("ERROR: Sequence with non-standard bases test failed")
    
    # Test with different security levels
    print("\nTesting different security levels...")
    test_seq = "ACGT" * 100
    security_levels = [1, 3, 5, 10, 20, 50]
    all_security_passed = True
    
    for level in security_levels:
        encrypted_data, removed_values = encrypt_sequence(test_seq, level)
        # Skip the check for empty sequences which use a special marker
        if test_seq and len(removed_values) != level:
            print(f"ERROR: Security level {level} test failed (wrong number of removed values)")
            all_security_passed = False
            continue
            
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(test_seq))
        if test_seq != decrypted_sequence:
            print(f"ERROR: Security level {level} test failed (decryption mismatch)")
            all_security_passed = False
    
    if all_security_passed:
        print("SUCCESS: All security level tests passed")
    
    # Test with different chunk sizes
    print("\nTesting different chunk sizes...")
    test_seq = "ACGT" * 1000  # 4000 bases
    chunk_sizes = [100, 500, 1000, 2000, 5000]
    all_chunk_passed = True
    
    for size in chunk_sizes:
        encrypted_data, removed_values = encrypt_sequence(test_seq, DEFAULT_SECURITY_LEVEL, size)
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(test_seq))
        if test_seq != decrypted_sequence:
            print(f"ERROR: Chunk size {size} test failed")
            all_chunk_passed = False
    
    if all_chunk_passed:
        print("SUCCESS: All chunk size tests passed")
    
    return empty_seq_passed and all_small_passed and non_standard_passed and all_security_passed and all_chunk_passed

def main():
    """Main entry point for the script."""
    print("=== DNASecure Stress Test ===")
    
    # Test edge cases
    edge_cases_passed = test_edge_cases()
    
    # Test with different sequence lengths
    lengths = [1000, 10000, 50000, 100000]
    standard_tests_passed = all(test_large_sequence(length) for length in lengths)
    
    # Test with optimized functions
    optimized_tests_passed = all(test_optimized_large_sequence(length) for length in lengths)
    
    # Test with different security levels
    security_tests_passed = all(test_large_sequence(10000, security_level) for security_level in [3, 10, 20])
    
    # Test with different chunk sizes
    chunk_tests_passed = all(test_large_sequence(20000, DEFAULT_SECURITY_LEVEL, chunk_size) for chunk_size in [5000, 10000, 20000])
    
    # Test FASTA functionality
    fasta_test_passed = test_large_fasta()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Edge Cases: {'PASSED' if edge_cases_passed else 'FAILED'}")
    print(f"Standard Tests: {'PASSED' if standard_tests_passed else 'FAILED'}")
    print(f"Optimized Tests: {'PASSED' if optimized_tests_passed else 'FAILED'}")
    print(f"Security Level Tests: {'PASSED' if security_tests_passed else 'FAILED'}")
    print(f"Chunk Size Tests: {'PASSED' if chunk_tests_passed else 'FAILED'}")
    print(f"FASTA Tests: {'PASSED' if fasta_test_passed else 'FAILED'}")
    
    all_passed = (edge_cases_passed and standard_tests_passed and optimized_tests_passed and 
                 security_tests_passed and chunk_tests_passed and fasta_test_passed)
    
    print(f"\nOverall Result: {'PASSED' if all_passed else 'FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 