#!/usr/bin/env python3
"""
Debug script to identify issues with the selfpowerdecomposer package.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from selfpowerdecomposer import (
    secure_encode_number_no_placeholder,
    secure_decode_number_no_placeholder,
    save_removed_info_no_placeholder,
    load_removed_info_no_placeholder
)

def main():
    """Main function to debug the selfpowerdecomposer package."""
    print("Testing selfpowerdecomposer package...")
    
    # Create a simple number
    number = 12345678901234567890
    print(f"Original number: {number}")
    
    # Encrypt the number
    print("\nEncrypting number...")
    try:
        encoded_data, removed_values = secure_encode_number_no_placeholder(number, 5)
        print(f"Encrypted data size: {len(encoded_data)} bytes")
        print(f"Number of removed values: {len(removed_values)}")
        print(f"Removed values: {removed_values}")
        
        # Create temporary files for testing
        fd_data, data_file = tempfile.mkstemp(suffix='.bin')
        os.close(fd_data)
        
        fd_key, key_file = tempfile.mkstemp(suffix='.key')
        os.close(fd_key)
        
        # Write data to file
        with open(data_file, 'wb') as f:
            f.write(encoded_data)
        
        # Write key to file - using the filename directly
        save_removed_info_no_placeholder(removed_values, key_file)
        
        print(f"\nData saved to {data_file}")
        print(f"Key saved to {key_file}")
        
        # Read data from file
        with open(data_file, 'rb') as f:
            data = f.read()
        
        # Read key from file - using the filename directly
        key = load_removed_info_no_placeholder(key_file)
        
        print("\nDecrypting number...")
        decrypted_number = secure_decode_number_no_placeholder(data, key)
        print(f"Decrypted number: {decrypted_number}")
        print(f"Matches original: {number == decrypted_number}")
        
        # Clean up temporary files
        os.remove(data_file)
        os.remove(key_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 