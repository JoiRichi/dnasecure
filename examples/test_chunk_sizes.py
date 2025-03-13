#!/usr/bin/env python3
"""
Test script to verify that different chunk sizes work correctly with DNAsecure.
"""

from dnasecure.core import encrypt_sequence, decrypt_sequence

def test_chunk_sizes():
    """Test encryption and decryption with different chunk sizes."""
    seq = 'A' * 50000
    chunk_sizes = [100, 500, 1000, 5000, 10000, 30000]
    
    results = []
    for chunk_size in chunk_sizes:
        print(f"\nTesting chunk size: {chunk_size}")
        enc, key = encrypt_sequence(seq, num_removed=5, chunk_size=chunk_size)
        dec = decrypt_sequence(enc, key)
        
        match = seq == dec
        results.append((chunk_size, match))
        
        print(f"Original length: {len(seq)}")
        print(f"Decrypted length: {len(dec)}")
        print(f"Match: {match}")
        
        if not match:
            # Find where they differ
            for i in range(min(len(seq), len(dec))):
                if seq[i] != dec[i]:
                    print(f"First mismatch at position {i}: '{seq[i]}' vs '{dec[i]}'")
                    break
    
    # Print summary
    print("\nSummary:")
    for chunk_size, match in results:
        status = "✓" if match else "×"
        print(f"{status} Chunk size {chunk_size}: {'Success' if match else 'Failed'}")

if __name__ == "__main__":
    test_chunk_sizes() 