#!/usr/bin/env python3

import os
import sys
import tempfile
import random

# Add the parent directory to the path so we can import the dnasecure package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnasecure.core import encrypt_fasta, decrypt_fasta

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    return ''.join(random.choice('ACGT') for _ in range(length))

def main():
    print("\n=== Testing FASTA Progress Information ===")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta, \
         tempfile.NamedTemporaryFile(suffix='.spd', delete=False) as temp_spd, \
         tempfile.NamedTemporaryFile(suffix='.key', delete=False) as temp_key, \
         tempfile.NamedTemporaryFile(suffix='.decrypted.fasta', delete=False) as temp_decrypted:
        
        # Generate random DNA sequences
        print("Generating random DNA sequences...")
        seq1_length = 15000
        seq2_length = 8000
        
        # Write sequences to FASTA file
        temp_fasta.write(f">Sequence1 Test sequence 1\n".encode())
        temp_fasta.write(f"{generate_random_dna(seq1_length)}\n".encode())
        temp_fasta.write(f">Sequence2 Test sequence 2\n".encode())
        temp_fasta.write(f"{generate_random_dna(seq2_length)}\n".encode())
        temp_fasta.flush()
        
        fasta_path = temp_fasta.name
        spd_path = temp_spd.name
        key_path = temp_key.name
        decrypted_path = temp_decrypted.name
    
    print(f"Created FASTA file with 2 sequences: {seq1_length} and {seq2_length} bases")
    
    # Encrypt the FASTA file
    print("\n=== Encrypting FASTA file ===")
    encrypt_fasta(fasta_path, spd_path, key_path, chunk_size=10000)
    
    # Decrypt the FASTA file
    print("\n=== Decrypting FASTA file ===")
    decrypt_fasta(spd_path, key_path, decrypted_path)
    
    # Verify the decrypted file
    print("\n=== Verification ===")
    
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
    all_match = True
    for header, original_seq in original_sequences.items():
        if header not in decrypted_sequences:
            print(f"Header '{header}' not found in decrypted file")
            all_match = False
            continue
        
        decrypted_seq = decrypted_sequences[header]
        if original_seq != decrypted_seq:
            print(f"Sequence '{header}' doesn't match")
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
            print(f"Sequence '{header}' matches (length: {len(original_seq)})")
    
    print(f"All sequences match: {all_match}")
    
    # Clean up temporary files
    for file_path in [fasta_path, spd_path, key_path, decrypted_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("\nTest completed.")

if __name__ == "__main__":
    main() 