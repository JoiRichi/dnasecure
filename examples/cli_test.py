#!/usr/bin/env python3
"""
Test script for DNAsecure CLI
"""

import os
import tempfile
import subprocess
import sys

def run_command(command):
    """Run a shell command and return the output"""
    print(f"Running command: {command}")
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"Exit code: {process.returncode}")
    if process.stdout:
        print("STDOUT:")
        print(process.stdout)
    
    if process.stderr:
        print("STDERR:")
        print(process.stderr)
    
    return process

def test_cli_help():
    """Test the help command"""
    print("\n=== Testing CLI Help ===")
    result = run_command("dnasecure --help")
    assert result.returncode == 0
    assert "usage:" in result.stdout
    print("✓ Help command test passed")

def test_cli_version():
    """Test the version command"""
    print("\n=== Testing CLI Version ===")
    result = run_command("dnasecure --version")
    assert result.returncode == 0
    assert "DNAsecure v" in result.stdout
    print("✓ Version command test passed")

def test_cli_encryption():
    """Test basic encryption and decryption"""
    print("\n=== Testing CLI Encryption/Decryption ===")
    
    # Create a temporary FASTA file
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta:
        temp_fasta.write(b">TestSequence\nATGCATGCATGCATGCATGC\n")
        temp_fasta_path = temp_fasta.name
    
    # Define output files
    temp_spd_path = temp_fasta_path + '.spd'
    temp_key_path = temp_fasta_path + '.key'
    temp_decrypted_path = temp_fasta_path + '.decrypted.fasta'
    
    try:
        # Encrypt
        encrypt_cmd = f"dnasecure encrypt {temp_fasta_path} {temp_spd_path} {temp_key_path} --security-level 3"
        result = run_command(encrypt_cmd)
        assert result.returncode == 0
        assert os.path.exists(temp_spd_path)
        assert os.path.exists(temp_key_path)
        
        # Decrypt
        decrypt_cmd = f"dnasecure decrypt {temp_spd_path} {temp_key_path} {temp_decrypted_path}"
        result = run_command(decrypt_cmd)
        assert result.returncode == 0
        assert os.path.exists(temp_decrypted_path)
        
        # Verify content
        with open(temp_fasta_path, 'r') as f:
            original_content = f.read()
        with open(temp_decrypted_path, 'r') as f:
            decrypted_content = f.read()
        
        assert original_content == decrypted_content
        print("✓ Basic encryption/decryption test passed")
        
    finally:
        # Clean up
        for file_path in [temp_fasta_path, temp_spd_path, temp_key_path, temp_decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_cli_chunk_size():
    """Test encryption with custom chunk size"""
    print("\n=== Testing CLI Chunk Size ===")
    
    # Create a temporary FASTA file with a longer sequence
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta:
        # Create a sequence of 200 bases
        sequence = "ATGC" * 50
        temp_fasta.write(f">LongSequence\n{sequence}\n".encode())
        temp_fasta_path = temp_fasta.name
    
    # Define output files
    temp_spd_path = temp_fasta_path + '.spd'
    temp_key_path = temp_fasta_path + '.key'
    temp_decrypted_path = temp_fasta_path + '.decrypted.fasta'
    
    try:
        # Encrypt with custom chunk size
        encrypt_cmd = f"dnasecure encrypt {temp_fasta_path} {temp_spd_path} {temp_key_path} --chunk-size 50"
        result = run_command(encrypt_cmd)
        assert result.returncode == 0, "Encryption failed"
        assert os.path.exists(temp_spd_path), "SPD file not created"
        assert os.path.exists(temp_key_path), "Key file not created"
        
        # Decrypt
        decrypt_cmd = f"dnasecure decrypt {temp_spd_path} {temp_key_path} {temp_decrypted_path}"
        result = run_command(decrypt_cmd)
        assert result.returncode == 0, "Decryption failed"
        assert os.path.exists(temp_decrypted_path), "Decrypted file not created"
        
        # Verify that the decrypted file contains valid FASTA format
        with open(temp_decrypted_path, 'r') as f:
            decrypted_content = f.read()
            
        # Check that the file contains a FASTA header and sequence
        decrypted_lines = decrypted_content.strip().split('\n')
        assert len(decrypted_lines) >= 2, "Decrypted file doesn't contain enough lines"
        assert decrypted_lines[0].startswith('>'), "Decrypted file doesn't start with a FASTA header"
        assert len(decrypted_lines[1]) > 0, "Decrypted sequence is empty"
        
        # Print sequence lengths for debugging
        with open(temp_fasta_path, 'r') as f:
            original_content = f.read()
        original_lines = original_content.strip().split('\n')
        
        print(f"Original sequence length: {len(original_lines[1])}")
        print(f"Decrypted sequence length: {len(decrypted_lines[1])}")
        
        print("✓ Chunk size test passed")
        
    finally:
        # Clean up
        for file_path in [temp_fasta_path, temp_spd_path, temp_key_path, temp_decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_cli_parallel():
    """Test parallel processing"""
    print("\n=== Testing CLI Parallel Processing ===")
    
    # Create a temporary FASTA file with multiple sequences
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as temp_fasta:
        temp_fasta.write(b">Seq1\nATGCATGCATGC\n>Seq2\nGGGAAACCCTTT\n>Seq3\nTAGGCATGCATG\n>Seq4\nCATGCATGCATG\n")
        temp_fasta_path = temp_fasta.name
    
    # Define output files
    temp_spd_path = temp_fasta_path + '.spd'
    temp_key_path = temp_fasta_path + '.key'
    temp_decrypted_path = temp_fasta_path + '.decrypted.fasta'
    
    try:
        # Encrypt with parallel processing
        encrypt_cmd = f"dnasecure encrypt {temp_fasta_path} {temp_spd_path} {temp_key_path} --parallel"
        result = run_command(encrypt_cmd)
        assert result.returncode == 0
        assert os.path.exists(temp_spd_path)
        assert os.path.exists(temp_key_path)
        
        # Decrypt with parallel processing
        decrypt_cmd = f"dnasecure decrypt {temp_spd_path} {temp_key_path} {temp_decrypted_path} --parallel"
        result = run_command(decrypt_cmd)
        assert result.returncode == 0
        assert os.path.exists(temp_decrypted_path)
        
        # Verify content
        with open(temp_fasta_path, 'r') as f:
            original_content = f.read()
        with open(temp_decrypted_path, 'r') as f:
            decrypted_content = f.read()
        
        assert original_content == decrypted_content
        print("✓ Parallel processing test passed")
        
    finally:
        # Clean up
        for file_path in [temp_fasta_path, temp_spd_path, temp_key_path, temp_decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

def main():
    """Run all tests"""
    print("=== DNAsecure CLI Test ===")
    
    try:
        # Run tests
        test_cli_help()
        test_cli_version()
        test_cli_encryption()
        test_cli_chunk_size()
        test_cli_parallel()
        
        print("\nAll CLI tests passed! ✓")
        return 0
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 