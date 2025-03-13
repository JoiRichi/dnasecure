#!/usr/bin/env python3
"""
Tests for the DNAsecure CLI.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnasecure.cli import main

class TestCLI(unittest.TestCase):
    """Test cases for the DNAsecure CLI."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary FASTA file
        self.input_fasta = self._create_test_fasta()
        
        # Create temporary output files
        fd_spd, self.output_spd = tempfile.mkstemp(suffix='.spd')
        os.close(fd_spd)
        
        fd_key, self.output_key = tempfile.mkstemp(suffix='.key')
        os.close(fd_key)
        
        fd_out, self.output_fasta = tempfile.mkstemp(suffix='.fasta')
        os.close(fd_out)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary files
        for file in [self.input_fasta, self.output_spd, self.output_key, self.output_fasta]:
            if os.path.exists(file):
                os.remove(file)
    
    def _create_test_fasta(self):
        """Create a temporary FASTA file for testing."""
        fd, path = tempfile.mkstemp(suffix='.fasta')
        with os.fdopen(fd, 'w') as f:
            f.write(">Sequence1 Test sequence 1\n")
            f.write("ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC\n")
            f.write(">Sequence2 Test sequence 2\n")
            f.write("GGGAAACCCTTTAGGCATGCATGCATGCATGCATGCATGCATGC\n")
        return path
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption through the CLI."""
        # Test encryption
        args = [
            "encrypt",
            self.input_fasta,
            self.output_spd,
            self.output_key,
            "--security-level",
            "5"
        ]
        
        exit_code = main(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(self.output_spd))
        self.assertTrue(os.path.exists(self.output_key))
        
        # Test decryption
        args = [
            "decrypt",
            self.output_spd,
            self.output_key,
            self.output_fasta
        ]
        
        exit_code = main(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(self.output_fasta))
        
        # Compare original and decrypted files
        with open(self.input_fasta, 'r') as f1, open(self.output_fasta, 'r') as f2:
            original_content = f1.read()
            decrypted_content = f2.read()
            
            # Remove newlines for comparison (since formatting might differ)
            original_content = original_content.replace('\n', '')
            decrypted_content = decrypted_content.replace('\n', '')
            
            self.assertEqual(original_content, decrypted_content)
    
    def test_invalid_command(self):
        """Test CLI with invalid command."""
        args = ["invalid_command"]
        
        with self.assertRaises(SystemExit):
            main(args)
    
    def test_version(self):
        """Test version flag."""
        args = ["--version"]
        
        with self.assertRaises(SystemExit):
            main(args)

if __name__ == "__main__":
    unittest.main() 