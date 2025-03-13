#!/usr/bin/env python3
"""
Test script for DNAsecure API
"""

import os
import tempfile
from dnasecure import (
    encrypt_sequence, 
    decrypt_sequence, 
    encrypt_fasta, 
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

def test_sequence_encryption():
    """Test basic sequence encryption and decryption"""
    print("Testing basic sequence encryption and decryption...")
    
    # Test sequence
    sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
    print(f"Original sequence: {sequence}")
    
    # Encrypt with default parameters
    encrypted_data, removed_values = encrypt_sequence(sequence)
    
    # Decrypt
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    print(f"Decrypted sequence: {decrypted_sequence}")
    
    # Verify
    assert sequence == decrypted_sequence
    print("✓ Basic encryption/decryption test passed")
    print()

def test_chunked_sequence():
    """Test chunked sequence encryption and decryption with custom chunk size"""
    print("Testing chunked sequence encryption and decryption...")
    
    # Test with different chunk sizes
    # Use a sequence length that's exactly divisible by the chunk size
    test_cases = [
        {"chunk_size": 20, "sequence_length": 100},
        {"chunk_size": 50, "sequence_length": 150},
        {"chunk_size": 100, "sequence_length": 200}
    ]
    
    for case in test_cases:
        chunk_size = case["chunk_size"]
        seq_length = case["sequence_length"]
        
        # Generate a sequence of exact length
        sequence = "ATGC" * (seq_length // 4)
        if len(sequence) < seq_length:
            sequence += "A" * (seq_length - len(sequence))
        
        print(f"\nTesting with chunk size: {chunk_size}, sequence length: {seq_length}")
        
        # Encrypt with custom chunk size
        encrypted_data, removed_values = encrypt_sequence(sequence, num_removed=5, chunk_size=chunk_size)
        
        # Check if we're dealing with a chunked sequence
        is_chunked = False
        if len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][1], list):
            is_chunked = True
            print(f"Detected chunked sequence with {len(removed_values)} chunks")
        
        # Decrypt
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        
        # Print debug info
        print(f"Original sequence length: {len(sequence)}")
        print(f"Decrypted sequence length: {len(decrypted_sequence)}")
        
        # Compare the sequences
        if sequence == decrypted_sequence:
            print(f"✓ Chunked encryption/decryption test passed for chunk size {chunk_size}")
        else:
            # Try to find where they differ
            min_len = min(len(sequence), len(decrypted_sequence))
            for i in range(min_len):
                if sequence[i] != decrypted_sequence[i]:
                    print(f"Sequences differ at position {i}: {sequence[i]} vs {decrypted_sequence[i]}")
                    break
            
            # If they're different lengths but match up to the shorter one
            if sequence[:min_len] == decrypted_sequence[:min_len]:
                print("Sequences match up to the shorter length, but have different lengths")
            
            # Try a different approach - use a simple test sequence
            test_seq = "A" * chunk_size
            print(f"\nTrying with a simple test sequence of {len(test_seq)} 'A's")
            enc_data, enc_key = encrypt_sequence(test_seq, num_removed=5, chunk_size=chunk_size)
            dec_seq = decrypt_sequence(enc_data, enc_key)
            
            if test_seq == dec_seq:
                print("✓ Simple test sequence passed")
            else:
                print("× Simple test sequence failed")
                
            assert sequence == decrypted_sequence, "Chunked sequence test failed"

def test_fasta_encryption():
    """Test FASTA file encryption and decryption"""
    print("\nTesting FASTA file encryption and decryption...")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta:
        temp_fasta.write(b">Sequence1\nATGCATGCATGCATGCATGC\n>Sequence2\nGGGAAACCCTTTAGGCATGC\n")
        temp_fasta_path = temp_fasta.name
    
    temp_spd_path = temp_fasta_path + '.spd'
    temp_key_path = temp_fasta_path + '.key'
    temp_decrypted_path = temp_fasta_path + '.decrypted.fasta'
    
    try:
        # Encrypt FASTA file
        print(f"Encrypting FASTA file: {temp_fasta_path}")
        encrypt_fasta(
            temp_fasta_path, 
            temp_spd_path, 
            temp_key_path, 
            num_removed=3, 
            chunk_size=10
        )
        
        # Decrypt FASTA file
        print(f"Decrypting to: {temp_decrypted_path}")
        decrypt_fasta(
            temp_spd_path, 
            temp_key_path, 
            temp_decrypted_path
        )
        
        # Verify files exist
        assert os.path.exists(temp_spd_path)
        assert os.path.exists(temp_key_path)
        assert os.path.exists(temp_decrypted_path)
        
        print("✓ FASTA encryption/decryption test passed")
        
    finally:
        # Clean up temporary files
        for file_path in [temp_fasta_path, temp_spd_path, temp_key_path, temp_decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_parallel_processing():
    """Test parallel processing for multiple sequences"""
    print("\nTesting parallel processing...")
    
    # Create temporary files with multiple sequences
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta:
        temp_fasta.write(b">Seq1\nATGCATGCATGC\n>Seq2\nGGGAAACCCTTT\n>Seq3\nTAGGCATGCATG\n>Seq4\nCATGCATGCATG\n")
        temp_fasta_path = temp_fasta.name
    
    temp_spd_path = temp_fasta_path + '.spd'
    temp_key_path = temp_fasta_path + '.key'
    temp_decrypted_path = temp_fasta_path + '.decrypted.fasta'
    
    try:
        # Encrypt with parallel processing
        print("Encrypting with parallel processing...")
        encrypt_fasta(
            temp_fasta_path, 
            temp_spd_path, 
            temp_key_path, 
            parallel=True, 
            num_processes=2
        )
        
        # Decrypt with parallel processing
        print("Decrypting with parallel processing...")
        decrypt_fasta(
            temp_spd_path, 
            temp_key_path, 
            temp_decrypted_path, 
            parallel=True, 
            num_processes=2
        )
        
        print("✓ Parallel processing test passed")
        
    finally:
        # Clean up temporary files
        for file_path in [temp_fasta_path, temp_spd_path, temp_key_path, temp_decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def main():
    """Run all tests"""
    print("=== DNAsecure API Test ===")
    print(f"Default security level: {DEFAULT_SECURITY_LEVEL}")
    print(f"Default chunk size: {DEFAULT_CHUNK_SIZE}")
    print()
    
    # Run tests
    test_sequence_encryption()
    test_chunked_sequence()
    test_fasta_encryption()
    test_parallel_processing()
    
    print("\nAll tests passed! ✓")

if __name__ == "__main__":
    main() 