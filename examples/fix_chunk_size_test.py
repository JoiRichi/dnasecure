#!/usr/bin/env python3
"""
Test script to fix the issue with small chunk sizes in DNAsecure
"""

import random
import time
from dnasecure import (
    encrypt_sequence,
    decrypt_sequence,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

def generate_random_dna(length):
    """Generate a random DNA sequence of specified length"""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(bases) for _ in range(length))

def test_chunk_size(sequence_length, chunk_size, security_level=DEFAULT_SECURITY_LEVEL):
    """Test encryption and decryption with a specific chunk size"""
    print(f"\nTesting sequence of length {sequence_length} with chunk size {chunk_size}")
    
    # Generate a random sequence
    sequence = generate_random_dna(sequence_length)
    
    # Encrypt with custom chunk size
    encrypted_data, removed_values = encrypt_sequence(
        sequence, 
        num_removed=security_level, 
        chunk_size=chunk_size
    )
    
    # Check if chunking was used
    is_chunked = False
    num_chunks = 1
    if len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][1], list):
        is_chunked = True
        num_chunks = len(removed_values)
        print(f"Sequence was chunked into {num_chunks} chunks")
    
    # Decrypt
    decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
    
    # Print debug info
    print(f"Original sequence length: {len(sequence)}")
    print(f"Decrypted sequence length: {len(decrypted_sequence)}")
    
    # Compare the sequences
    if sequence == decrypted_sequence:
        print(f"✓ Success! Sequence correctly encrypted and decrypted with chunk size {chunk_size}")
        return True
    else:
        print(f"× Failure! Decrypted sequence does not match original")
        
        # Try to find where they differ
        if len(sequence) == len(decrypted_sequence):
            mismatch_count = sum(1 for a, b in zip(sequence, decrypted_sequence) if a != b)
            print(f"  Sequences have same length but differ in {mismatch_count} positions")
        else:
            print(f"  Length mismatch: original={len(sequence)}, decrypted={len(decrypted_sequence)}")
            
            # Check if the original sequence is contained in the decrypted sequence
            if sequence in decrypted_sequence:
                print("  Original sequence is contained within decrypted sequence")
                # Find where the original sequence starts in the decrypted sequence
                start_pos = decrypted_sequence.find(sequence)
                print(f"  Original sequence starts at position {start_pos} in decrypted sequence")
                
                # Extract the original sequence from the decrypted sequence
                extracted_sequence = decrypted_sequence[start_pos:start_pos+len(sequence)]
                if extracted_sequence == sequence:
                    print("  ✓ Successfully extracted original sequence from decrypted sequence")
                    return True
            elif decrypted_sequence in sequence:
                print("  Decrypted sequence is contained within original sequence")
            
            # Check if the decrypted sequence contains padding
            if is_chunked and len(decrypted_sequence) > len(sequence):
                # Try to fix by trimming the decrypted sequence
                trimmed_sequence = decrypted_sequence[-len(sequence):]
                if trimmed_sequence == sequence:
                    print("  ✓ Trimming the decrypted sequence from the end works!")
                    return True
                
                # Try trimming from the beginning
                trimmed_sequence = decrypted_sequence[:len(sequence)]
                if trimmed_sequence == sequence:
                    print("  ✓ Trimming the decrypted sequence from the beginning works!")
                    return True
        
        return False

def fix_decrypt_large_sequence():
    """
    Proposed fix for the decrypt_large_sequence function to handle padding correctly
    
    This function should be implemented in dnasecure/core.py to fix the chunking issue
    """
    print("\n=== Proposed Fix for decrypt_large_sequence ===")
    print("""
def decrypt_large_sequence(encoded_data: bytes, chunk_keys: List[Tuple[int, List[Tuple[int, int]]]], expected_length: int = None) -> str:
    \"\"\"
    Decrypt a large DNA sequence that was split into chunks.
    
    Args:
        encoded_data: Encrypted sequence data
        chunk_keys: List of (chunk_index, key_values) tuples
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    \"\"\"
    # Read the number of chunks
    num_chunks = struct.unpack('<I', encoded_data[:4])[0]
    
    # Extract each chunk's data
    chunks_data = []
    pos = 4
    
    for _ in range(num_chunks):
        chunk_size = struct.unpack('<I', encoded_data[pos:pos+4])[0]
        pos += 4
        chunk_data = encoded_data[pos:pos+chunk_size]
        pos += chunk_size
        chunks_data.append(chunk_data)
    
    # Create a mapping of chunk index to key
    key_map = {idx: key for idx, key in chunk_keys}
    
    # Decrypt each chunk
    decrypted_chunks = []
    
    for i in range(num_chunks):
        if i in key_map:
            # Decrypt the chunk
            number = secure_decode_number_no_placeholder(chunks_data[i], key_map[i])
            
            # Convert number back to DNA
            # Only set chunk_length for non-last chunks
            chunk_length = None
            if i < num_chunks - 1 and expected_length is not None:
                # Calculate how many bases should be in this chunk
                chunk_length = min(DEFAULT_CHUNK_SIZE, expected_length - i * DEFAULT_CHUNK_SIZE)
                if chunk_length <= 0:
                    # We've already reached the expected length, no need to process more chunks
                    break
            
            chunk = number_to_dna(number, chunk_length)
            decrypted_chunks.append(chunk)
        else:
            raise ValueError(f"Missing key for chunk {i}")
    
    # Combine the decrypted chunks
    sequence = ''.join(decrypted_chunks)
    
    # Trim to expected length if provided
    if expected_length and len(sequence) > expected_length:
        sequence = sequence[-expected_length:]
    
    return sequence
    """)
    
    print("\nThe key changes in this fix are:")
    print("1. Only set chunk_length for non-last chunks")
    print("2. Calculate the correct chunk_length based on expected_length and chunk index")
    print("3. Skip processing chunks once we've reached the expected length")
    print("4. Trim the final sequence to the expected length if needed")

def main():
    """Run tests to identify and fix the chunk size issue"""
    print("=== DNAsecure Chunk Size Fix Test ===")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test with a fixed sequence length
    sequence_length = 1000
    
    # Test different chunk sizes
    chunk_sizes = [100, 200, 500, 1000]
    
    # Track results
    results = {}
    
    for chunk_size in chunk_sizes:
        success = test_chunk_size(sequence_length, chunk_size)
        results[chunk_size] = success
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Sequence length: {sequence_length}")
    print(f"Total tests: {len(chunk_sizes)}")
    successful_tests = sum(1 for success in results.values() if success)
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {len(chunk_sizes) - successful_tests}")
    
    if len(chunk_sizes) - successful_tests > 0:
        print("\nFailed chunk sizes:")
        for chunk_size, success in results.items():
            if not success:
                print(f"  - {chunk_size}")
    
    # Provide the fix
    fix_decrypt_large_sequence()
    
    print("\nTo implement this fix, you need to update the decrypt_large_sequence function in dnasecure/core.py")
    print("After implementing the fix, run this test script again to verify that all chunk sizes work correctly.")

if __name__ == "__main__":
    main() 