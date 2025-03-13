#!/usr/bin/env python3
"""
Test script to verify FASTA encryption and decryption with different chunk sizes.
This script tests the DNAsecure package's ability to handle FASTA files with
multiple sequences using various chunk sizes.
"""

import os
import random
import tempfile
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from dnasecure.core import DEFAULT_SECURITY_LEVEL, encrypt_fasta, decrypt_fasta

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    return ''.join(random.choice('ACGT') for _ in range(length))

def create_test_fasta(filename, num_sequences=3, lengths=None):
    """Create a test FASTA file with random sequences."""
    if lengths is None:
        lengths = [1000, 5000, 10000]
    
    records = []
    for i in range(num_sequences):
        seq_length = lengths[i % len(lengths)]
        seq = generate_random_dna(seq_length)
        record = SeqRecord(
            Seq(seq),
            id=f"seq{i+1}",
            description=f"Random DNA sequence {i+1} (length {seq_length})"
        )
        records.append(record)
    
    SeqIO.write(records, filename, "fasta")
    print(f"Created FASTA file with {num_sequences} sequences")
    return records

def test_fasta_chunk_size(chunk_size, debug=True):
    """Test FASTA encryption and decryption with a specific chunk size."""
    print(f"\n=== Testing with chunk size {chunk_size} ===")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta, \
         tempfile.NamedTemporaryFile(suffix='.spd', delete=False) as temp_spd, \
         tempfile.NamedTemporaryFile(suffix='.key', delete=False) as temp_key, \
         tempfile.NamedTemporaryFile(suffix='.decrypted.fasta', delete=False) as temp_decrypted:
        
        # Create test FASTA file
        original_records = create_test_fasta(temp_fasta.name)
        
        # Encrypt the FASTA file
        encrypt_fasta(
            temp_fasta.name, 
            temp_spd.name, 
            temp_key.name, 
            num_removed=DEFAULT_SECURITY_LEVEL, 
            chunk_size=chunk_size,
            parallel=True
        )
        
        # Get encrypted file sizes
        spd_size = os.path.getsize(temp_spd.name)
        key_size = os.path.getsize(temp_key.name)
        if debug:
            print(f"Encrypted SPD file size: {spd_size} bytes")
            print(f"Key file size: {key_size} bytes")
        
        # Decrypt the FASTA file
        decrypt_fasta(
            temp_spd.name, 
            temp_key.name, 
            temp_decrypted.name, 
            parallel=True
        )
        
        # Verify the decrypted sequences
        decrypted_records = list(SeqIO.parse(temp_decrypted.name, "fasta"))
        
        success = True
        for i, (orig, dec) in enumerate(zip(original_records, decrypted_records)):
            orig_seq = str(orig.seq)
            dec_seq = str(dec.seq)
            
            if orig_seq == dec_seq:
                print(f"✓ Sequence {i+1} (length {len(orig_seq)}) correctly encrypted and decrypted")
            else:
                success = False
                print(f"× Sequence {i+1} (length {len(orig_seq)}) failed verification")
                if debug:
                    # Calculate the number of differences
                    diff_count = sum(1 for a, b in zip(orig_seq, dec_seq) if a != b)
                    print(f"  Differences: {diff_count} positions out of {len(orig_seq)}")
                    
                    # Show a sample of differences
                    if len(orig_seq) == len(dec_seq):
                        diff_positions = [i for i, (a, b) in enumerate(zip(orig_seq, dec_seq)) if a != b]
                        if diff_positions:
                            sample_size = min(5, len(diff_positions))
                            sample_pos = diff_positions[:sample_size]
                            print("  Sample differences (position: original -> decrypted):")
                            for pos in sample_pos:
                                print(f"    {pos}: {orig_seq[pos]} -> {dec_seq[pos]}")
                    else:
                        print(f"  Length mismatch: original={len(orig_seq)}, decrypted={len(dec_seq)}")
        
        # Clean up temporary files
        for file in [temp_fasta.name, temp_spd.name, temp_key.name, temp_decrypted.name]:
            if os.path.exists(file):
                os.remove(file)
        
        return success

def main():
    """Run tests with different chunk sizes."""
    # Test with different chunk sizes
    chunk_sizes = [100, 500, 1000, 5000, 10000]
    results = {}
    
    for chunk_size in chunk_sizes:
        results[chunk_size] = test_fasta_chunk_size(chunk_size)
    
    # Print summary
    print("\nSummary:")
    for chunk_size, success in results.items():
        status = "✓ Success" if success else "× Failed"
        print(f"{status if success else '×'} Chunk size {chunk_size}: {status}")

if __name__ == "__main__":
    main() 