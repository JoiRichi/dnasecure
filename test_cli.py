#!/usr/bin/env python3
"""
Test script for the dnasecure CLI.
This script tests the command-line interface of the dnasecure package.
"""

import subprocess
import tempfile
import os

def test_cli_functionality():
    """Test the CLI functionality of the dnasecure package."""
    print("=== DNASecure CLI Test ===\n")
    
    # Create a temporary FASTA file
    with tempfile.NamedTemporaryFile(suffix='.fasta', delete=False) as f:
        fasta_path = f.name
        f.write(b">Sequence1\n")
        f.write(b"ACGTACGTACGT\n")
        f.write(b">Sequence2\n")
        f.write(b"TGCATGCATGCA\n")
    
    # Create output file paths
    fd, spd_path = tempfile.mkstemp(suffix='.spd')
    os.close(fd)
    
    fd, key_path = tempfile.mkstemp(suffix='.key')
    os.close(fd)
    
    fd, decrypted_path = tempfile.mkstemp(suffix='.decrypted.fasta')
    os.close(fd)
    
    try:
        # Test the encrypt command
        print("Testing 'dnasecure encrypt' command...")
        encrypt_cmd = [
            "dnasecure", "encrypt",
            "--security-level", "5",
            "--chunk-size", "10000",
            fasta_path, spd_path, key_path
        ]
        
        print(f"Running command: {' '.join(encrypt_cmd)}")
        encrypt_result = subprocess.run(encrypt_cmd, capture_output=True, text=True)
        
        if encrypt_result.returncode == 0:
            print("Encryption command succeeded")
            print(encrypt_result.stdout)
        else:
            print("Encryption command failed")
            print(f"Return code: {encrypt_result.returncode}")
            print(f"Error: {encrypt_result.stderr}")
            return False
        
        # Test the decrypt command
        print("\nTesting 'dnasecure decrypt' command...")
        decrypt_cmd = [
            "dnasecure", "decrypt",
            spd_path, key_path, decrypted_path
        ]
        
        print(f"Running command: {' '.join(decrypt_cmd)}")
        decrypt_result = subprocess.run(decrypt_cmd, capture_output=True, text=True)
        
        if decrypt_result.returncode == 0:
            print("Decryption command succeeded")
            print(decrypt_result.stdout)
        else:
            print("Decryption command failed")
            print(f"Return code: {decrypt_result.returncode}")
            print(f"Error: {decrypt_result.stderr}")
            return False
        
        # Verify the result
        print("\nVerifying result...")
        with open(fasta_path, 'r') as f:
            original_content = f.read()
        
        with open(decrypted_path, 'r') as f:
            decrypted_content = f.read()
        
        # Compare the content (ignoring whitespace differences)
        original_lines = [line.strip() for line in original_content.split('\n') if line.strip()]
        decrypted_lines = [line.strip() for line in decrypted_content.split('\n') if line.strip()]
        
        if len(original_lines) == len(decrypted_lines):
            all_match = True
            for i in range(len(original_lines)):
                if original_lines[i] != decrypted_lines[i]:
                    if original_lines[i].startswith('>') and decrypted_lines[i].startswith('>'):
                        # Headers might have additional information, just check if they start the same
                        if original_lines[i].split()[0] != decrypted_lines[i].split()[0]:
                            all_match = False
                            break
                    elif not original_lines[i].startswith('>') and not decrypted_lines[i].startswith('>'):
                        # For sequences, they should match exactly
                        all_match = False
                        break
            
            if all_match:
                print("SUCCESS: CLI test passed - content matches")
                return True
            else:
                print("ERROR: CLI test failed - content mismatch")
                return False
        else:
            print(f"ERROR: CLI test failed - line count mismatch ({len(original_lines)} vs {len(decrypted_lines)})")
            return False
    
    finally:
        # Clean up temporary files
        for file_path in [fasta_path, spd_path, key_path, decrypted_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    result = test_cli_functionality()
    
    print("\n=== Test Summary ===")
    print(f"CLI Functionality: {'PASSED' if result else 'FAILED'}")
    
    print("\nIf all tests passed, the dnasecure CLI is working correctly!") 