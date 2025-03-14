#!/usr/bin/env python3
"""
Comprehensive test suite for DNASecure package.
Tests all encryption and decryption functionality across various scenarios.
"""

import os
import sys
import tempfile
import random
import unittest
import pickle
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure.core import (
    dna_to_number,
    number_to_dna,
    encrypt_sequence,
    decrypt_sequence,
    encrypt_large_sequence,
    decrypt_large_sequence,
    encrypt_large_sequence_optimized,
    decrypt_large_sequence_optimized,
    encrypt_sequence_optimized,
    decrypt_sequence_optimized,
    encrypt_fasta,
    decrypt_fasta,
    combine_encrypted_chunks,
    split_encrypted_chunks,
    DEFAULT_SECURITY_LEVEL,
    DEFAULT_CHUNK_SIZE
)

class TestDNASecureBasic(unittest.TestCase):
    """Test basic functionality of DNASecure package."""

    def test_dna_to_number_conversion(self):
        """Test DNA to number conversion."""
        # Test basic conversion
        self.assertEqual(dna_to_number("A"), 1)
        self.assertEqual(dna_to_number("C"), 2)
        self.assertEqual(dna_to_number("G"), 3)
        self.assertEqual(dna_to_number("T"), 4)
        self.assertEqual(dna_to_number("N"), 5)
        
        # Test longer sequences
        self.assertEqual(dna_to_number("ACGT"), 1*6**3 + 2*6**2 + 3*6 + 4)
        self.assertEqual(dna_to_number("AAAAAA"), 1*6**5 + 1*6**4 + 1*6**3 + 1*6**2 + 1*6 + 1)
        
        # Test case insensitivity
        self.assertEqual(dna_to_number("acgt"), dna_to_number("ACGT"))
        
        # Test empty sequence
        self.assertEqual(dna_to_number(""), 0)

    def test_number_to_dna_conversion(self):
        """Test number to DNA conversion."""
        # Test basic conversion
        self.assertEqual(number_to_dna(1), "A")
        self.assertEqual(number_to_dna(2), "C")
        self.assertEqual(number_to_dna(3), "G")
        self.assertEqual(number_to_dna(4), "T")
        self.assertEqual(number_to_dna(5), "N")
        
        # Test longer sequences
        self.assertEqual(number_to_dna(1*6**3 + 2*6**2 + 3*6 + 4), "ACGT")
        
        # Test zero
        self.assertEqual(number_to_dna(0), "")
        self.assertEqual(number_to_dna(0, 5), "AAAAA")
        
        # Test with expected length
        self.assertEqual(number_to_dna(1, 3), "AAA")
        self.assertEqual(number_to_dna(1*6 + 2, 3), "AAC")
        self.assertEqual(number_to_dna(1*6**2 + 2*6 + 3, 3), "ACG")
        self.assertEqual(number_to_dna(1*6**2 + 2*6 + 3, 5), "AAACG")

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion from DNA to number and back."""
        test_sequences = [
            "A", "C", "G", "T", "N",
            "ACGT", "AAAAAA", "CCCCCC", "GGGGGG", "TTTTTT",
            "ACGTACGT", "ACGTN", "NACGT",
            "A" * 100, "C" * 100, "G" * 100, "T" * 100,
            "ACGT" * 25
        ]
        
        for seq in test_sequences:
            number = dna_to_number(seq)
            converted_seq = number_to_dna(number, len(seq))
            self.assertEqual(seq, converted_seq, f"Failed roundtrip for {seq}")


class TestDNASecureEncryption(unittest.TestCase):
    """Test encryption and decryption functionality."""
    
    def setUp(self):
        """Set up test sequences."""
        # Small sequence (less than chunk size)
        self.small_sequence = "ACGT" * 100  # 400 bases
        
        # Medium sequence (around chunk size)
        self.medium_sequence = "ACGT" * 2500  # 10,000 bases
        
        # Large sequence (multiple chunks)
        self.large_sequence = "ACGT" * 5000  # 20,000 bases
        
        # Random sequence
        bases = ["A", "C", "G", "T"]
        self.random_sequence = ''.join(random.choice(bases) for _ in range(15000))
        
        # Security levels to test
        self.security_levels = [3, 5, 10]
        
        # Chunk sizes to test
        self.chunk_sizes = [5000, 10000, 20000]

    def test_encrypt_decrypt_small_sequence(self):
        """Test encryption and decryption of small sequences."""
        for security_level in self.security_levels:
            # Standard implementation
            encrypted_data, removed_values = encrypt_sequence(
                self.small_sequence, security_level
            )
            decrypted_sequence = decrypt_sequence(
                encrypted_data, removed_values, len(self.small_sequence)
            )
            self.assertEqual(self.small_sequence, decrypted_sequence)
            
            # Optimized implementation
            encrypted_data, removed_values = encrypt_sequence_optimized(
                self.small_sequence, security_level
            )
            decrypted_sequence = decrypt_sequence_optimized(
                encrypted_data, removed_values, len(self.small_sequence)
            )
            self.assertEqual(self.small_sequence, decrypted_sequence)

    def test_encrypt_decrypt_medium_sequence(self):
        """Test encryption and decryption of medium sequences."""
        for security_level in self.security_levels:
            for chunk_size in self.chunk_sizes:
                # Standard implementation
                encrypted_data, removed_values = encrypt_sequence(
                    self.medium_sequence, security_level, chunk_size
                )
                decrypted_sequence = decrypt_sequence(
                    encrypted_data, removed_values, len(self.medium_sequence)
                )
                self.assertEqual(self.medium_sequence, decrypted_sequence)
                
                # Optimized implementation
                encrypted_data, removed_values = encrypt_sequence_optimized(
                    self.medium_sequence, security_level, chunk_size
                )
                decrypted_sequence = decrypt_sequence_optimized(
                    encrypted_data, removed_values, len(self.medium_sequence)
                )
                self.assertEqual(self.medium_sequence, decrypted_sequence)

    def test_encrypt_decrypt_large_sequence(self):
        """Test encryption and decryption of large sequences."""
        for security_level in self.security_levels:
            for chunk_size in self.chunk_sizes:
                # Standard implementation
                encrypted_data, removed_values = encrypt_large_sequence(
                    self.large_sequence, security_level, chunk_size
                )
                decrypted_sequence = decrypt_large_sequence(
                    encrypted_data, removed_values, len(self.large_sequence)
                )
                self.assertEqual(self.large_sequence, decrypted_sequence)
                
                # Optimized implementation
                encrypted_data, removed_values = encrypt_large_sequence_optimized(
                    self.large_sequence, security_level, chunk_size
                )
                decrypted_sequence = decrypt_large_sequence_optimized(
                    encrypted_data, removed_values, len(self.large_sequence)
                )
                self.assertEqual(self.large_sequence, decrypted_sequence)

    def test_encrypt_decrypt_random_sequence(self):
        """Test encryption and decryption of random sequences."""
        # Standard implementation with default parameters
        encrypted_data, removed_values = encrypt_sequence(self.random_sequence)
        decrypted_sequence = decrypt_sequence(
            encrypted_data, removed_values, len(self.random_sequence)
        )
        self.assertEqual(self.random_sequence, decrypted_sequence)
        
        # Optimized implementation with default parameters
        encrypted_data, removed_values = encrypt_sequence_optimized(self.random_sequence)
        decrypted_sequence = decrypt_sequence_optimized(
            encrypted_data, removed_values, len(self.random_sequence)
        )
        self.assertEqual(self.random_sequence, decrypted_sequence)

    def test_combine_split_encrypted_chunks(self):
        """Test combining and splitting encrypted chunks."""
        # Create some test chunks
        chunks = [b"chunk1", b"chunk2", b"chunk3", b"chunk4"]
        
        # Combine chunks
        combined_data = combine_encrypted_chunks(chunks)
        
        # Split combined data
        split_chunks = split_encrypted_chunks(combined_data)
        
        # Verify that the split chunks match the original chunks
        self.assertEqual(len(chunks), len(split_chunks))
        for i in range(len(chunks)):
            self.assertEqual(chunks[i], split_chunks[i])


class TestDNASecureFASTA(unittest.TestCase):
    """Test FASTA file encryption and decryption."""
    
    def setUp(self):
        """Set up test FASTA files."""
        # Create temporary files
        self.temp_files = []
        
        # Create a temporary FASTA file with multiple sequences
        fd, self.fasta_path = tempfile.mkstemp(suffix='.fasta')
        os.close(fd)
        self.temp_files.append(self.fasta_path)
        
        # Create output files
        fd, self.spd_path = tempfile.mkstemp(suffix='.spd')
        os.close(fd)
        self.temp_files.append(self.spd_path)
        
        fd, self.key_path = tempfile.mkstemp(suffix='.key')
        os.close(fd)
        self.temp_files.append(self.key_path)
        
        fd, self.decrypted_path = tempfile.mkstemp(suffix='.decrypted.fasta')
        os.close(fd)
        self.temp_files.append(self.decrypted_path)
        
        # Generate random DNA sequences
        self.seq1_length = 5000
        self.seq2_length = 8000
        self.seq3_length = 15000
        
        # Write sequences to FASTA file
        with open(self.fasta_path, 'w') as f:
            f.write(f">Sequence1 Test sequence 1\n")
            f.write(f"{''.join(random.choice('ACGT') for _ in range(self.seq1_length))}\n")
            f.write(f">Sequence2 Test sequence 2\n")
            f.write(f"{''.join(random.choice('ACGT') for _ in range(self.seq2_length))}\n")
            f.write(f">Sequence3 Test sequence 3\n")
            f.write(f"{''.join(random.choice('ACGT') for _ in range(self.seq3_length))}\n")

    def tearDown(self):
        """Clean up temporary files."""
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_encrypt_decrypt_fasta(self):
        """Test encryption and decryption of FASTA files."""
        # Test with different security levels and chunk sizes
        security_levels = [3, 5, 10]
        chunk_sizes = [5000, 10000]
        
        for security_level in security_levels:
            for chunk_size in chunk_sizes:
                # Encrypt the FASTA file
                encrypt_fasta(
                    self.fasta_path, self.spd_path, self.key_path,
                    num_removed=security_level, chunk_size=chunk_size
                )
                
                # Decrypt the FASTA file
                decrypt_fasta(self.spd_path, self.key_path, self.decrypted_path)
                
                # Parse the original FASTA file
                original_sequences = self._parse_fasta(self.fasta_path)
                
                # Parse the decrypted FASTA file
                decrypted_sequences = self._parse_fasta(self.decrypted_path)
                
                # Compare the sequences
                self.assertEqual(len(original_sequences), len(decrypted_sequences))
                for header, original_seq in original_sequences.items():
                    self.assertIn(header, decrypted_sequences)
                    decrypted_seq = decrypted_sequences[header]
                    self.assertEqual(len(original_seq), len(decrypted_seq))
                    self.assertEqual(original_seq, decrypted_seq)

    def test_encrypt_decrypt_fasta_parallel(self):
        """Test parallel encryption and decryption of FASTA files."""
        # Encrypt the FASTA file with parallel processing
        encrypt_fasta(
            self.fasta_path, self.spd_path, self.key_path,
            parallel=True, num_processes=2
        )
        
        # Decrypt the FASTA file with parallel processing
        decrypt_fasta(
            self.spd_path, self.key_path, self.decrypted_path,
            parallel=True, num_processes=2
        )
        
        # Parse the original FASTA file
        original_sequences = self._parse_fasta(self.fasta_path)
        
        # Parse the decrypted FASTA file
        decrypted_sequences = self._parse_fasta(self.decrypted_path)
        
        # Compare the sequences
        self.assertEqual(len(original_sequences), len(decrypted_sequences))
        for header, original_seq in original_sequences.items():
            self.assertIn(header, decrypted_sequences)
            decrypted_seq = decrypted_sequences[header]
            self.assertEqual(len(original_seq), len(decrypted_seq))
            self.assertEqual(original_seq, decrypted_seq)

    def _parse_fasta(self, fasta_path):
        """Parse a FASTA file and return a dictionary of sequences."""
        sequences = {}
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
                        sequences[current_header] = ''.join(current_sequence)
                    
                    # Start a new sequence
                    current_header = line[1:]  # Remove the '>' character
                    current_sequence = []
                else:
                    # Add to the current sequence
                    current_sequence.append(line)
            
            # Save the last sequence if it exists
            if current_header is not None:
                sequences[current_header] = ''.join(current_sequence)
        
        return sequences


class TestDNASecureEdgeCases(unittest.TestCase):
    """Test edge cases for DNASecure package."""
    
    def test_empty_sequence(self):
        """Test encryption and decryption of empty sequences."""
        # Empty sequence should be handled gracefully
        empty_seq = ""
        
        # For empty sequences, we should get a minimal result back
        encrypted_data, removed_values = encrypt_sequence(empty_seq)
        self.assertIsNotNone(encrypted_data)
        
        # Decryption should also handle empty data gracefully
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        self.assertEqual(decrypted_sequence, "")
        
        # Optimized implementation
        encrypted_data, removed_values = encrypt_sequence_optimized(empty_seq)
        self.assertIsNotNone(encrypted_data)
        
        decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values)
        self.assertEqual(decrypted_sequence, "")

    def test_very_small_sequence(self):
        """Test encryption and decryption of very small sequences."""
        # Very small sequences should be handled correctly
        small_seqs = ["A", "C", "G", "T", "N", "AC", "GT", "ACG", "ACGT"]
        
        for seq in small_seqs:
            # Standard implementation
            encrypted_data, removed_values = encrypt_sequence(seq)
            decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(seq))
            self.assertEqual(seq, decrypted_sequence)
            
            # Optimized implementation
            encrypted_data, removed_values = encrypt_sequence_optimized(seq)
            decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values, len(seq))
            self.assertEqual(seq, decrypted_sequence)

    def test_non_standard_bases(self):
        """Test handling of non-standard bases."""
        # Sequences with non-standard bases should be handled correctly
        seq_with_n = "ACGTN" * 10
        
        # Standard implementation
        encrypted_data, removed_values = encrypt_sequence(seq_with_n)
        decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(seq_with_n))
        self.assertEqual(seq_with_n, decrypted_sequence)
        
        # Optimized implementation
        encrypted_data, removed_values = encrypt_sequence_optimized(seq_with_n)
        decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values, len(seq_with_n))
        self.assertEqual(seq_with_n, decrypted_sequence)

    def test_different_security_levels(self):
        """Test different security levels."""
        # Test with different security levels
        test_seq = "ACGT" * 100
        security_levels = [1, 3, 5, 10, 20, 50]
        
        for level in security_levels:
            # Standard implementation
            encrypted_data, removed_values = encrypt_sequence(test_seq, level)
            self.assertEqual(len(removed_values), level)
            decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(test_seq))
            self.assertEqual(test_seq, decrypted_sequence)
            
            # Optimized implementation
            encrypted_data, removed_values = encrypt_sequence_optimized(test_seq, level)
            self.assertEqual(len(removed_values), level)
            decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values, len(test_seq))
            self.assertEqual(test_seq, decrypted_sequence)

    def test_different_chunk_sizes(self):
        """Test different chunk sizes."""
        # Test with different chunk sizes
        test_seq = "ACGT" * 1000  # 4000 bases
        chunk_sizes = [100, 500, 1000, 2000, 5000]
        
        for size in chunk_sizes:
            # Standard implementation
            encrypted_data, removed_values = encrypt_sequence(test_seq, DEFAULT_SECURITY_LEVEL, size)
            decrypted_sequence = decrypt_sequence(encrypted_data, removed_values, len(test_seq))
            self.assertEqual(test_seq, decrypted_sequence)
            
            # Optimized implementation
            encrypted_data, removed_values = encrypt_sequence_optimized(test_seq, DEFAULT_SECURITY_LEVEL, size)
            decrypted_sequence = decrypt_sequence_optimized(encrypted_data, removed_values, len(test_seq))
            self.assertEqual(test_seq, decrypted_sequence)


if __name__ == "__main__":
    unittest.main()
