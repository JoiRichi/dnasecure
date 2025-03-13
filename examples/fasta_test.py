#!/usr/bin/env python3
"""
Comprehensive test script for DNAsecure to verify FASTA file handling
"""

import os
import random
import tempfile
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from dnasecure import (
    encrypt_fasta,
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

def generate_random_dna(length):
    """Generate a random DNA sequence of specified length"""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def create_test_fasta(filename, num_sequences=3, lengths=None, chunk_size=DEFAULT_CHUNK_SIZE):
    """Create a test FASTA file with random sequences"""
    if lengths is None:
        # Create sequences of different lengths, including some that will be chunked
        lengths = [500, chunk_size - 100, chunk_size + 100, chunk_size * 2 + 50]
        lengths = lengths[:num_sequences]  # Limit to requested number of sequences
    
    records = []
    for i in range(num_sequences):
        seq_id = f"seq{i+1}"
        description = f"Test sequence {i+1} (length: {lengths[i]})"
        sequence = generate_random_dna(lengths[i])
        record = SeqRecord(Seq(sequence), id=seq_id, description=description)
        records.append(record)
    
    # Write to FASTA file
    SeqIO.write(records, filename, "fasta")
    
    # Return the original sequences for verification
    return [str(record.seq) for record in records]

def test_fasta_encryption_decryption(security_level=DEFAULT_SECURITY_LEVEL, chunk_size=DEFAULT_CHUNK_SIZE, parallel=True):
    """Test encryption and decryption of FASTA files"""
    print(f"\n=== Testing FASTA encryption/decryption ===")
    print(f"Security level: {security_level}")
    print(f"Chunk size: {chunk_size}")
    print(f"Parallel processing: {parallel}")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as input_fasta, \
         tempfile.NamedTemporaryFile(suffix='.spd', delete=False) as output_spd, \
         tempfile.NamedTemporaryFile(suffix='.key', delete=False) as output_key, \
         tempfile.NamedTemporaryFile(suffix='.decrypted.fasta', delete=False) as output_fasta:
        
        input_fasta_path = input_fasta.name
        output_spd_path = output_spd.name
        output_key_path = output_key.name
        output_fasta_path = output_fasta.name
    
    try:
        # Create test FASTA file with multiple sequences
        print("Creating test FASTA file with multiple sequences...")
        original_sequences = create_test_fasta(
            input_fasta_path, 
            num_sequences=3, 
            lengths=[500, chunk_size - 100, chunk_size + 100]
        )
        print(f"Created FASTA file with {len(original_sequences)} sequences")
        
        # Encrypt the FASTA file
        print("Encrypting FASTA file...")
        encrypt_fasta(
            input_fasta_path,
            output_spd_path,
            output_key_path,
            num_removed=security_level,
            parallel=parallel,
            chunk_size=chunk_size
        )
        print("Encryption completed")
        
        # Verify encrypted files exist and have content
        spd_size = os.path.getsize(output_spd_path)
        key_size = os.path.getsize(output_key_path)
        print(f"Encrypted SPD file size: {spd_size} bytes")
        print(f"Key file size: {key_size} bytes")
        
        if spd_size == 0 or key_size == 0:
            print("× Error: Encrypted files are empty")
            return False
        
        # Decrypt the FASTA file
        print("Decrypting FASTA file...")
        decrypt_fasta(
            output_spd_path,
            output_key_path,
            output_fasta_path,
            parallel=parallel
        )
        print("Decryption completed")
        
        # Read the decrypted sequences
        decrypted_sequences = []
        with open(output_fasta_path, 'r') as f:
            for record in SeqIO.parse(f, "fasta"):
                decrypted_sequences.append(str(record.seq))
        
        # Verify the results
        if len(decrypted_sequences) != len(original_sequences):
            print(f"× Error: Number of sequences doesn't match. Original: {len(original_sequences)}, Decrypted: {len(decrypted_sequences)}")
            return False
        
        all_match = True
        for i, (original, decrypted) in enumerate(zip(original_sequences, decrypted_sequences)):
            if original == decrypted:
                print(f"✓ Sequence {i+1} (length {len(original)}) correctly encrypted and decrypted")
            else:
                print(f"× Sequence {i+1} (length {len(original)}) failed verification")
                if len(original) == len(decrypted):
                    mismatch_count = sum(1 for a, b in zip(original, decrypted) if a != b)
                    print(f"  Sequences have same length but differ in {mismatch_count} positions")
                else:
                    print(f"  Length mismatch: original={len(original)}, decrypted={len(decrypted)}")
                all_match = False
        
        return all_match
    
    finally:
        # Clean up temporary files
        for file_path in [input_fasta_path, output_spd_path, output_key_path, output_fasta_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_large_fasta():
    """Test with a larger FASTA file containing multiple sequences of various sizes"""
    print("\n=== Testing with larger FASTA file ===")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as input_fasta, \
         tempfile.NamedTemporaryFile(suffix='.spd', delete=False) as output_spd, \
         tempfile.NamedTemporaryFile(suffix='.key', delete=False) as output_key, \
         tempfile.NamedTemporaryFile(suffix='.decrypted.fasta', delete=False) as output_fasta:
        
        input_fasta_path = input_fasta.name
        output_spd_path = output_spd.name
        output_key_path = output_key.name
        output_fasta_path = output_fasta.name
    
    try:
        # Create test FASTA file with multiple sequences of various sizes
        print("Creating large test FASTA file...")
        lengths = [500, 1000, 5000, 9999, 10000, 10001, 15000, 20000]
        original_sequences = create_test_fasta(
            input_fasta_path, 
            num_sequences=len(lengths), 
            lengths=lengths
        )
        print(f"Created FASTA file with {len(original_sequences)} sequences of various lengths")
        
        # Encrypt the FASTA file
        print("Encrypting large FASTA file...")
        encrypt_fasta(
            input_fasta_path,
            output_spd_path,
            output_key_path,
            parallel=True
        )
        print("Encryption completed")
        
        # Decrypt the FASTA file
        print("Decrypting large FASTA file...")
        decrypt_fasta(
            output_spd_path,
            output_key_path,
            output_fasta_path,
            parallel=True
        )
        print("Decryption completed")
        
        # Read the decrypted sequences
        decrypted_sequences = []
        with open(output_fasta_path, 'r') as f:
            for record in SeqIO.parse(f, "fasta"):
                decrypted_sequences.append(str(record.seq))
        
        # Verify the results
        if len(decrypted_sequences) != len(original_sequences):
            print(f"× Error: Number of sequences doesn't match. Original: {len(original_sequences)}, Decrypted: {len(decrypted_sequences)}")
            return False
        
        all_match = True
        for i, (original, decrypted) in enumerate(zip(original_sequences, decrypted_sequences)):
            if original == decrypted:
                print(f"✓ Sequence {i+1} (length {len(original)}) correctly encrypted and decrypted")
            else:
                print(f"× Sequence {i+1} (length {len(original)}) failed verification")
                all_match = False
        
        return all_match
    
    finally:
        # Clean up temporary files
        for file_path in [input_fasta_path, output_spd_path, output_key_path, output_fasta_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_custom_chunk_size():
    """Test FASTA encryption/decryption with a custom chunk size"""
    print("\n=== Testing with custom chunk size ===")
    return test_fasta_encryption_decryption(chunk_size=5000)

def test_custom_security_level():
    """Test FASTA encryption/decryption with a custom security level"""
    print("\n=== Testing with custom security level ===")
    return test_fasta_encryption_decryption(security_level=10)

def test_sequential_processing():
    """Test FASTA encryption/decryption with sequential processing"""
    print("\n=== Testing with sequential processing ===")
    return test_fasta_encryption_decryption(parallel=False)

def main():
    """Run all tests"""
    print("=== DNAsecure FASTA File Test ===")
    print(f"Default security level: {DEFAULT_SECURITY_LEVEL}")
    print(f"Default chunk size: {DEFAULT_CHUNK_SIZE}")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run tests
    basic_test = test_fasta_encryption_decryption()
    large_test = test_large_fasta()
    chunk_size_test = test_custom_chunk_size()
    security_level_test = test_custom_security_level()
    sequential_test = test_sequential_processing()
    
    # Print overall results
    print("\n=== Test Results Summary ===")
    print(f"Basic FASTA test: {'✓ Passed' if basic_test else '× Failed'}")
    print(f"Large FASTA test: {'✓ Passed' if large_test else '× Failed'}")
    print(f"Custom chunk size test: {'✓ Passed' if chunk_size_test else '× Failed'}")
    print(f"Custom security level test: {'✓ Passed' if security_level_test else '× Failed'}")
    print(f"Sequential processing test: {'✓ Passed' if sequential_test else '× Failed'}")
    
    all_passed = basic_test and large_test and chunk_size_test and security_level_test and sequential_test
    
    if all_passed:
        print("\n✓ All tests passed! DNAsecure correctly handles FASTA files with multiple sequences.")
        print("The package is ready for redeployment.")
    else:
        print("\n× Some tests failed. See details above.")

if __name__ == "__main__":
    main() 