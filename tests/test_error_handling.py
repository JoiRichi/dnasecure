#!/usr/bin/env python3
"""
Test error handling capabilities of DNASecure package.
Verifies that the library properly handles various error conditions.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure.core import (
    encrypt_sequence,
    decrypt_sequence,
    encrypt_large_sequence,
    decrypt_large_sequence,
    encrypt_fasta,
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

class TestErrorHandling(unittest.TestCase):
    """Test error handling capabilities of DNASecure package."""
    
    def test_invalid_sequence_type(self):
        """Test handling of invalid sequence types."""
        # Test with non-string input
        with self.assertRaises(Exception):
            encrypt_sequence(123)
        
        with self.assertRaises(Exception):
            encrypt_sequence([1, 2, 3, 4])
    
    def test_invalid_decryption_input(self):
        """Test handling of invalid decryption input."""
        # Encrypt a sequence
        sequence = "ACGT" * 100
        encrypted_data, removed_values = encrypt_sequence(sequence)
        
        # Test with invalid removed values
        with self.assertRaises(Exception):
            decrypt_sequence(encrypted_data, "invalid key")
        
        # Test with mismatched removed values
        other_sequence = "AAAA" * 100
        _, other_removed_values = encrypt_sequence(other_sequence)
        
        # This should fail during decryption, but might not raise an exception
        # Instead, we'll check that the decrypted sequence doesn't match the original
        decrypted_sequence = decrypt_sequence(encrypted_data, other_removed_values, len(sequence))
        self.assertNotEqual(sequence, decrypted_sequence)
    
    def test_invalid_fasta_input(self):
        """Test handling of invalid FASTA input."""
        # Create temporary files
        fd, fasta_path = tempfile.mkstemp(suffix='.fasta')
        os.close(fd)
        
        fd, spd_path = tempfile.mkstemp(suffix='.spd')
        os.close(fd)
        
        fd, key_path = tempfile.mkstemp(suffix='.key')
        os.close(fd)
        
        fd, decrypted_path = tempfile.mkstemp(suffix='.decrypted.fasta')
        os.close(fd)
        
        try:
            # Test with non-existent input file
            with self.assertRaises(Exception):
                encrypt_fasta("non_existent_file.fasta", spd_path, key_path)
            
            # Test with non-existent SPD file for decryption
            with self.assertRaises(Exception):
                decrypt_fasta("non_existent_file.spd", key_path, decrypted_path)
            
            # Test with non-existent key file for decryption
            with self.assertRaises(Exception):
                decrypt_fasta(spd_path, "non_existent_file.key", decrypted_path)
            
            # Test with invalid SPD file format
            with open(spd_path, 'wb') as f:
                f.write(b"This is not a valid SPD file")
            
            with self.assertRaises(Exception):
                decrypt_fasta(spd_path, key_path, decrypted_path)
            
            # Test with invalid key file format
            with open(key_path, 'wb') as f:
                f.write(b"This is not a valid key file")
            
            with self.assertRaises(Exception):
                decrypt_fasta(spd_path, key_path, decrypted_path)
        
        finally:
            # Clean up temporary files
            for file_path in [fasta_path, spd_path, key_path, decrypted_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_chunked_sequence_mismatch(self):
        """Test handling of mismatched chunked sequences."""
        # Encrypt a large sequence
        sequence = "ACGT" * 5000  # 20,000 bases
        encrypted_data, removed_values = encrypt_large_sequence(sequence)
        
        # Modify the number of chunks in the encrypted data
        # This should cause an error during decryption
        modified_data = bytearray(encrypted_data)
        modified_data[0] = modified_data[0] + 1  # Increase the number of chunks
        
        with self.assertRaises(Exception):
            decrypt_large_sequence(bytes(modified_data), removed_values)
        
        # Modify the removed values
        # This should cause an error during decryption
        modified_values = removed_values[:-1]  # Remove the last chunk's key
        
        with self.assertRaises(Exception):
            decrypt_large_sequence(encrypted_data, modified_values)
    
    def test_empty_sequence(self):
        """Test handling of empty sequences."""
        # Empty sequence should be handled gracefully
        empty_seq = ""
        
        # For empty sequences, we should get a minimal result back
        encrypted_data, removed_values = encrypt_sequence(empty_seq)
        self.assertIsNotNone(encrypted_data)
        
        # Decryption should also handle empty data gracefully
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        self.assertEqual(decrypted_sequence, "")


if __name__ == "__main__":
    unittest.main() 