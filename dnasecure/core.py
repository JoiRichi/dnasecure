"""
DNAsecure - DNA sequence encryption using self-power decomposition

This module provides tools for encrypting and decrypting DNA sequences using
the self-power decomposition algorithm from the selfpowerdecomposer package.
"""

import os
import struct
import tempfile
from typing import Dict, List, Tuple, Union
import multiprocessing
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import sys
import functools
from itertools import islice
import pickle


sys.set_int_max_str_digits(0)
# Import from the updated selfpowerdecomposer
from selfpowerdecomposer import (
    secure_encode_number_no_placeholder,
    secure_decode_number_no_placeholder,
    save_removed_info_no_placeholder,
    load_removed_info_no_placeholder
)

# DNA base to number mapping (starting from 1 to avoid leading zero issues)
BASE_TO_NUM = {'A': 1, 'C': 2, 'G': 3, 'T': 4, 'N': 5}
NUM_TO_BASE = {1: 'A', 2: 'C', 3: 'G', 4: 'T', 5: 'N'}

# Number of values to remove for security (key size)
DEFAULT_SECURITY_LEVEL = 5

# Default chunk size for large sequences (to avoid overflow)
DEFAULT_CHUNK_SIZE = 10000  # Default chunk size is 10,000 bases

# Default number of processes for parallel processing
DEFAULT_PROCS = multiprocessing.cpu_count()

# Flag to use optimized implementation (default: False)
USE_OPTIMIZED_IMPLEMENTATION = False

# Precompute struct formats for optimized implementation
CHUNK_HEADER = struct.Struct('<I')

# Precompute lookup tables for maximum speed
_BASE_TO_NUM_LOOKUP = [5] * 256
for char, val in [('A', 1), ('a', 1), ('C', 2), ('c', 2),
                  ('G', 3), ('g', 3), ('T', 4), ('t', 4),
                  ('N', 5), ('n', 5)]:
    _BASE_TO_NUM_LOOKUP[ord(char)] = val

_NUM_TO_BASE_LIST = ['', 'A', 'C', 'G', 'T', 'N']


def dna_to_number(sequence: str) -> int:
    """Convert DNA sequence to a number using optimized lookup and reduce."""
    lookup = _BASE_TO_NUM_LOOKUP  # Local variable for speed
    return functools.reduce(lambda x, c: x * 6 + lookup[c],
                            map(ord, sequence), 0)


def number_to_dna(number: int, length: int = None) -> str:
    """Convert number back to DNA using list comprehensions and preallocated lookups."""
    num_to_base = _NUM_TO_BASE_LIST  # Local variable for speed
    if number == 0:
        return 'A' * length if length else ''

    digits = []
    while number > 0:
        number, rem = divmod(number, 6)
        digits.append(rem)

    digits.reverse()
    if length is not None:
        pad = length - len(digits)
        if pad > 0:
            digits = [1] * pad + digits  # 1 corresponds to 'A'

    return ''.join(num_to_base[d] for d in digits)




def encrypt_sequence(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Tuple[bytes, List[Tuple[int, int]]]:
    """
    Encrypt a DNA sequence using secure self-power decomposition.
    For large sequences (>chunk_size bases), splits into chunks to avoid slow decomposition.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        chunk_size: Maximum size of each chunk for large sequences
        
    Returns:
        Tuple of (encrypted data, removed values)
    """
    # Special case for empty sequences
    if not sequence:
        # Return a special marker for empty sequences
        return b'\x02', [(0, 0)]  # Flag 2 for empty sequence
    
    # Check if sequence is too large and needs chunking
    if len(sequence) > chunk_size:
        print(f"Sequence length ({len(sequence):,} bases) exceeds chunk size ({chunk_size:,} bases), splitting into chunks...")
        return encrypt_large_sequence(sequence, num_removed, chunk_size)
    
    # Convert DNA to number
    number = dna_to_number(sequence)
    
    # Encrypt using secure self-power decomposition
    encoded_data, removed_values = secure_encode_number_no_placeholder(number, num_removed)
    
    return encoded_data, removed_values

def encrypt_large_sequence(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Tuple[bytes, List[Tuple[int, List[Tuple[int, int]]]]]:
    """
    Encrypt a large DNA sequence by splitting it into chunks.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        chunk_size: Maximum size of each chunk
        
    Returns:
        Tuple of (encrypted data, chunked keys)
    """
    # Split sequence into chunks
    chunks = [sequence[i:i+chunk_size] for i in range(0, len(sequence), chunk_size)]
    total_chunks = len(chunks)
    print(f"Splitting sequence into {total_chunks:,} chunks of max size {chunk_size:,} bases")
    
    # Encrypt each chunk
    encrypted_chunks = []
    chunked_keys = []
    
    for i, chunk in enumerate(chunks):
        print(f"Encrypting chunk {i+1}/{total_chunks} ({len(chunk):,} bases)...")
        number = dna_to_number(chunk)
        encrypted_chunk, removed_values = secure_encode_number_no_placeholder(number, num_removed)
        encrypted_chunks.append(encrypted_chunk)
        chunked_keys.append((len(chunk), removed_values))
    
    # Combine encrypted chunks
    combined_data = combine_encrypted_chunks(encrypted_chunks)
    print(f"Encryption complete. Total encrypted data size: {len(combined_data):,} bytes")
    
    return combined_data, chunked_keys

def decrypt_sequence(encoded_data: bytes, removed_values: List[Tuple[int, int]], expected_length: int = None) -> str:
    """
    Decrypt a DNA sequence using the encrypted data and key.
    Handles both regular and chunked sequences.
    
    Args:
        encoded_data: Encrypted sequence data
        removed_values: List of removed values (positions and values) or chunked keys
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    """
    # Special case for empty sequences
    if encoded_data == b'\x02' and removed_values == [(0, 0)]:
        return ""
    
    # Check if this is a chunked sequence
    if len(encoded_data) >= 4 and isinstance(removed_values, list) and len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][0], int) and isinstance(removed_values[0][1], list):
        print(f"Detected chunked sequence, processing chunks...")
        return decrypt_large_sequence(encoded_data, removed_values, expected_length)
    
    # Decrypt using secure self-power decomposition
    number = secure_decode_number_no_placeholder(encoded_data, removed_values)
    
    # Convert number back to DNA
    sequence = number_to_dna(number, expected_length)
    
    return sequence

def decrypt_large_sequence(encoded_data: bytes, chunked_keys: List[Tuple[int, List[Tuple[int, int]]]], expected_length: int = None) -> str:
    """
    Decrypt a large DNA sequence that was split into chunks.
    
    Args:
        encoded_data: Combined encrypted data
        chunked_keys: List of (chunk_length, removed_values) for each chunk
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    """
    # Split encoded data back into chunks
    encrypted_chunks = split_encrypted_chunks(encoded_data)
    total_chunks = len(chunked_keys)
    print(f"Processing {total_chunks:,} encrypted chunks...")
    
    if len(encrypted_chunks) != len(chunked_keys):
        raise ValueError(f"Number of encrypted chunks ({len(encrypted_chunks)}) doesn't match number of keys ({len(chunked_keys)})")
    
    # Decrypt each chunk
    decrypted_chunks = []
    
    for i, (encrypted_chunk, (chunk_length, removed_values)) in enumerate(zip(encrypted_chunks, chunked_keys)):
        print(f"Decrypting chunk {i+1}/{total_chunks}...")
        number = secure_decode_number_no_placeholder(encrypted_chunk, removed_values)
        chunk = number_to_dna(number, chunk_length)
        decrypted_chunks.append(chunk)
    
    # Combine decrypted chunks
    decrypted_sequence = ''.join(decrypted_chunks)
    print(f"Decryption complete. Recovered sequence length: {len(decrypted_sequence):,} bases")
    
    # Trim to expected length if provided
    if expected_length is not None and len(decrypted_sequence) > expected_length:
        decrypted_sequence = decrypted_sequence[:expected_length]
    
    return decrypted_sequence

# Optimized chunking using itertools
def _chunk_iter(sequence, chunk_size):
    """
    Efficiently chunk a sequence using itertools.
    
    Args:
        sequence: The sequence to chunk
        chunk_size: Size of each chunk
        
    Returns:
        Iterator of chunks
    """
    it = iter(sequence)
    return iter(lambda: ''.join(islice(it, chunk_size)), '')

# Optimized worker functions
def _encrypt_sequence_worker_optimized(args):
    """
    Optimized worker function for parallel sequence encryption.
    
    Args:
        args: Tuple of (chunk, num_removed, chunk_size)
        
    Returns:
        Tuple of (encoded_data, removed_values)
    """
    chunk, num_removed, chunk_size = args
    number = dna_to_number(chunk)
    encoded_data, removed_values = secure_encode_number_no_placeholder(number, num_removed)
    return encoded_data, removed_values

def _decrypt_sequence_worker_optimized(args):
    """
    Optimized worker function for parallel sequence decryption.
    
    Args:
        args: Tuple of (chunk_data, key, expected_length)
        
    Returns:
        Decrypted sequence
    """
    chunk_data, key, expected_length = args
    number = secure_decode_number_no_placeholder(chunk_data, key)
    return number_to_dna(number, expected_length)

def encrypt_large_sequence_optimized(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Tuple[bytes, List[Tuple[int, List[Tuple[int, int]]]]]:
    """
    Optimized version of encrypt_large_sequence using itertools for chunking.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        chunk_size: Maximum size of each chunk
        
    Returns:
        Tuple of (encrypted data, chunked keys)
    """
    # Calculate total number of chunks
    total_length = len(sequence)
    total_chunks = (total_length + chunk_size - 1) // chunk_size
    print(f"Splitting sequence into {total_chunks:,} chunks of max size {chunk_size:,} bases")
    
    # Create an iterator that yields chunks of the sequence
    chunks_iter = (sequence[i:i+chunk_size] for i in range(0, total_length, chunk_size))
    
    # Encrypt each chunk
    encrypted_chunks = []
    chunked_keys = []
    
    for i, chunk in enumerate(chunks_iter):
        print(f"Encrypting chunk {i+1}/{total_chunks} ({len(chunk):,} bases)...")
        number = dna_to_number(chunk)
        encrypted_chunk, removed_values = secure_encode_number_no_placeholder(number, num_removed)
        encrypted_chunks.append(encrypted_chunk)
        chunked_keys.append((len(chunk), removed_values))
    
    # Combine encrypted chunks
    combined_data = combine_encrypted_chunks(encrypted_chunks)
    print(f"Encryption complete. Total encrypted data size: {len(combined_data):,} bytes")
    
    return combined_data, chunked_keys

def decrypt_large_sequence_optimized(encoded_data: bytes, chunked_keys: List[Tuple[int, List[Tuple[int, int]]]], expected_length: int = None) -> str:
    """
    Optimized version of decrypt_large_sequence.
    
    Args:
        encoded_data: Combined encrypted data
        chunked_keys: List of (chunk_length, removed_values) for each chunk
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    """
    # Split encoded data back into chunks
    encrypted_chunks = split_encrypted_chunks(encoded_data)
    total_chunks = len(chunked_keys)
    print(f"Processing {total_chunks:,} encrypted chunks...")
    
    if len(encrypted_chunks) != len(chunked_keys):
        raise ValueError(f"Number of encrypted chunks ({len(encrypted_chunks)}) doesn't match number of keys ({len(chunked_keys)})")
    
    # Decrypt each chunk
    decrypted_chunks = []
    
    for i, (encrypted_chunk, (chunk_length, removed_values)) in enumerate(zip(encrypted_chunks, chunked_keys)):
        print(f"Decrypting chunk {i+1}/{total_chunks}...")
        number = secure_decode_number_no_placeholder(encrypted_chunk, removed_values)
        chunk = number_to_dna(number, chunk_length)
        decrypted_chunks.append(chunk)
    
    # Combine decrypted chunks
    decrypted_sequence = ''.join(decrypted_chunks)
    print(f"Decryption complete. Recovered sequence length: {len(decrypted_sequence):,} bases")
    
    # Trim to expected length if provided
    if expected_length is not None and len(decrypted_sequence) > expected_length:
        decrypted_sequence = decrypted_sequence[:expected_length]
    
    return decrypted_sequence

def _encrypt_sequence_worker(args):
    """
    Worker function for parallel sequence encryption.
    
    Args:
        args: Tuple of (sequence, num_removed, chunk_size)
        
    Returns:
        Tuple of (encoded_data, removed_values)
    """
    sequence, num_removed, chunk_size = args
    return encrypt_sequence(sequence, num_removed, chunk_size)

def _decrypt_sequence_worker(args):
    """
    Worker function for parallel sequence decryption.
    
    Args:
        args: Tuple of (encoded_data, removed_values, expected_length)
        
    Returns:
        Decrypted sequence
    """
    encoded_data, removed_values, expected_length = args
    return decrypt_sequence(encoded_data, removed_values, expected_length)

def combine_encrypted_chunks(encrypted_chunks: List[bytes]) -> bytes:
    """
    Combine multiple encrypted chunks into a single byte string.
    
    Args:
        encrypted_chunks: List of encrypted chunk data
        
    Returns:
        Combined data with format: [num_chunks (4 bytes)] + [chunk1_size (4 bytes) + chunk1_data] + ...
    """
    num_chunks = len(encrypted_chunks)
    combined_data = struct.pack('<I', num_chunks)
    
    for data in encrypted_chunks:
        combined_data += struct.pack('<I', len(data))
        combined_data += data
    
    return combined_data

def split_encrypted_chunks(combined_data: bytes) -> List[bytes]:
    """
    Split combined encrypted data back into individual chunks.
    
    Args:
        combined_data: Combined encrypted data
        
    Returns:
        List of individual encrypted chunks
    """
    # Read the number of chunks
    num_chunks = struct.unpack('<I', combined_data[:4])[0]
    
    # Extract each chunk's data
    chunks_data = []
    pos = 4
    
    for _ in range(num_chunks):
        chunk_size = struct.unpack('<I', combined_data[pos:pos+4])[0]
        pos += 4
        chunk_data = combined_data[pos:pos+chunk_size]
        pos += chunk_size
        chunks_data.append(chunk_data)
    
    return chunks_data

def encrypt_fasta(input_fasta: str, output_spd: str, output_key: str, num_removed: int = DEFAULT_SECURITY_LEVEL, parallel: bool = True, num_processes: int = None, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
    """
    Encrypt a FASTA file using secure self-power decomposition.
    
    Args:
        input_fasta: Path to input FASTA file
        output_spd: Path to output encrypted file
        output_key: Path to output key file
        num_removed: Number of values to remove for the key
        parallel: Whether to use parallel processing for large sequences
        num_processes: Number of processes to use for parallel processing
        chunk_size: Maximum size of each chunk for large sequences
    """
    print(f"Reading FASTA file: {input_fasta}")
    sequences = []
    headers = []
    
    with open(input_fasta, 'r') as f:
        current_header = None
        current_sequence = []
        
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('>'):
                # Save the previous sequence if it exists
                if current_header is not None:
                    headers.append(current_header)
                    sequences.append(''.join(current_sequence))
                
                # Start a new sequence
                current_header = line[1:]  # Remove the '>' character
                current_sequence = []
            else:
                # Add to the current sequence
                current_sequence.append(line)
        
        # Save the last sequence if it exists
        if current_header is not None:
            headers.append(current_header)
            sequences.append(''.join(current_sequence))
    
    print(f"Found {len(sequences)} sequences in FASTA file")
    
    # Encrypt each sequence
    encrypted_data_list = []
    removed_values_list = []
    
    for i, (header, sequence) in enumerate(zip(headers, sequences)):
        print(f"Encrypting sequence {i+1}/{len(sequences)}: {header} ({len(sequence):,} bases)")
        
        # Encrypt the sequence
        if parallel and len(sequence) > chunk_size:
            encrypted_data, removed_values = encrypt_large_sequence(sequence, num_removed, chunk_size)
        else:
            encrypted_data, removed_values = encrypt_sequence(sequence, num_removed, chunk_size)
        
        encrypted_data_list.append(encrypted_data)
        removed_values_list.append(removed_values)
    
    # Save the encrypted data
    print(f"Saving encrypted data to: {output_spd}")
    with open(output_spd, 'wb') as f:
        # Write the number of sequences
        f.write(struct.pack('<I', len(sequences)))
        
        # Write each header and encrypted data
        for header, encrypted_data in zip(headers, encrypted_data_list):
            # Write the header length and header
            header_bytes = header.encode('utf-8')
            f.write(struct.pack('<I', len(header_bytes)))
            f.write(header_bytes)
            
            # Write the encrypted data length and data
            f.write(struct.pack('<I', len(encrypted_data)))
            f.write(encrypted_data)
    
    # Save the removed values (key)
    print(f"Saving encryption key to: {output_key}")
    with open(output_key, 'wb') as f:
        pickle.dump((headers, removed_values_list), f)
    
    print(f"Encryption complete. Encrypted {len(sequences)} sequences.")

def decrypt_fasta(input_spd: str, input_key: str, output_fasta: str, parallel: bool = True, num_processes: int = None) -> None:
    """
    Decrypt a file encrypted with secure self-power decomposition back to FASTA format.
    
    Args:
        input_spd: Path to input encrypted file
        input_key: Path to input key file
        output_fasta: Path to output FASTA file
        parallel: Whether to use parallel processing for large sequences
        num_processes: Number of processes to use for parallel processing
    """
    print(f"Reading encrypted data from: {input_spd}")
    with open(input_spd, 'rb') as f:
        # Read the number of sequences
        num_sequences = struct.unpack('<I', f.read(4))[0]
        
        # Read each header and encrypted data
        headers = []
        encrypted_data_list = []
        
        for _ in range(num_sequences):
            # Read the header length and header
            header_length = struct.unpack('<I', f.read(4))[0]
            header = f.read(header_length).decode('utf-8')
            headers.append(header)
            
            # Read the encrypted data length and data
            data_length = struct.unpack('<I', f.read(4))[0]
            encrypted_data = f.read(data_length)
            encrypted_data_list.append(encrypted_data)
    
    print(f"Reading encryption key from: {input_key}")
    with open(input_key, 'rb') as f:
        key_headers, removed_values_list = pickle.load(f)
    
    # Verify that the headers match
    if headers != key_headers:
        print("Warning: Headers in encrypted file do not match headers in key file")
    
    print(f"Found {len(headers)} encrypted sequences")
    
    # Decrypt each sequence
    decrypted_sequences = []
    
    for i, (header, encrypted_data, removed_values) in enumerate(zip(headers, encrypted_data_list, removed_values_list)):
        print(f"Decrypting sequence {i+1}/{len(headers)}: {header}")
        
        # Check if this is a chunked sequence
        is_chunked = (len(encrypted_data) >= 4 and 
                     isinstance(removed_values, list) and 
                     len(removed_values) > 0 and 
                     isinstance(removed_values[0], tuple) and 
                     len(removed_values[0]) == 2 and 
                     isinstance(removed_values[0][0], int))
        
        # Decrypt the sequence
        if is_chunked and parallel:
            # Check if the first element of the tuple is a length (for the new format)
            # or an index (for the old format)
            if isinstance(removed_values[0][1], list):
                decrypted_sequence = decrypt_large_sequence(encrypted_data, removed_values)
            else:
                # This is the old format where the first element is an index
                decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        else:
            decrypted_sequence = decrypt_sequence(encrypted_data, removed_values)
        
        decrypted_sequences.append(decrypted_sequence)
    
    # Save the decrypted sequences to FASTA format
    print(f"Saving decrypted sequences to: {output_fasta}")
    with open(output_fasta, 'w') as f:
        for header, sequence in zip(headers, decrypted_sequences):
            f.write(f">{header}\n")
            
            # Write the sequence in lines of 70 characters
            for i in range(0, len(sequence), 70):
                f.write(f"{sequence[i:i+70]}\n")
    
    print(f"Decryption complete. Decrypted {len(headers)} sequences.")

def encrypt_sequence_optimized(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Tuple[bytes, List[Tuple[int, int]]]:
    """
    Optimized version of encrypt_sequence using direct number conversion.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        chunk_size: Maximum size of each chunk for large sequences
        
    Returns:
        Tuple of (encrypted data, removed values)
    """
    # Special case for empty sequences
    if not sequence:
        # Return a special marker for empty sequences
        return b'\x02', [(0, 0)]  # Flag 2 for empty sequence
    
    # Check if sequence is too large and needs chunking
    if len(sequence) > chunk_size:
        print(f"Sequence length ({len(sequence):,} bases) exceeds chunk size ({chunk_size:,} bases), using optimized chunking...")
        return encrypt_large_sequence_optimized(sequence, num_removed, chunk_size)
    
    # Convert DNA to number
    print(f"Converting DNA sequence ({len(sequence):,} bases) to number...")
    number = dna_to_number(sequence)
    
    # Encrypt using secure self-power decomposition
    print(f"Encrypting number using secure self-power decomposition...")
    encoded_data, removed_values = secure_encode_number_no_placeholder(number, num_removed)
    print(f"Encryption complete. Data size: {len(encoded_data):,} bytes")
    
    return encoded_data, removed_values

def decrypt_sequence_optimized(encoded_data: bytes, removed_values: List[Tuple[int, int]], expected_length: int = None) -> str:
    """
    Optimized version of decrypt_sequence using direct number conversion.
    
    Args:
        encoded_data: Encrypted sequence data
        removed_values: List of removed values (positions and values) or chunked keys
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    """
    # Special case for empty sequences
    if encoded_data == b'\x02' and removed_values == [(0, 0)]:
        return ""
    
    # Check if this is a chunked sequence
    if len(encoded_data) >= 4 and isinstance(removed_values, list) and len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][0], int) and isinstance(removed_values[0][1], list):
        print(f"Detected chunked sequence, using optimized chunking for decryption...")
        return decrypt_large_sequence_optimized(encoded_data, removed_values, expected_length)
    
    # Decrypt using secure self-power decomposition
    print(f"Decrypting data ({len(encoded_data):,} bytes) using secure self-power decomposition...")
    number = secure_decode_number_no_placeholder(encoded_data, removed_values)
    
    # Convert number back to DNA
    print(f"Converting number back to DNA sequence...")
    sequence = number_to_dna(number, expected_length)
    print(f"Decryption complete. Recovered sequence length: {len(sequence):,} bases")
    
    return sequence
