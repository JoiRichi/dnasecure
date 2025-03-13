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

# Maximum chunk size for large sequences (to avoid overflow)
MAX_CHUNK_SIZE = 10000  # Only chunk sequences larger than 10,000 bases

def dna_to_number(sequence: str) -> int:
    """
    Convert a DNA sequence to a single large integer.
    Each base is represented as a digit in base-6 (A=1, C=2, G=3, T=4, N=5).
    
    Args:
        sequence: DNA sequence string (ACGTN)
        
    Returns:
        Integer representation of the sequence
    """
    number = 0
    for base in sequence:
        number = number * 6 + BASE_TO_NUM.get(base.upper(), 5)  # Default to N (5) for unknown bases
    return number

def number_to_dna(number: int, length: int = None) -> str:
    """
    Convert a number back to a DNA sequence.
    
    Args:
        number: Integer representation of the sequence
        length: Expected length of the sequence (if known)
        
    Returns:
        DNA sequence string
    """
    sequence = []
    
    while number > 0:
        base_num = number % 6
        if base_num == 0:  # Skip 0, as our mapping starts from 1
            number //= 6
            continue
        sequence.append(NUM_TO_BASE[base_num])
        number //= 6
    
    # Reverse the sequence (since we built it backwards)
    sequence.reverse()
    
    # Pad with 'A's if length is specified
    if length and len(sequence) < length:
        sequence = ['A'] * (length - len(sequence)) + sequence
        
    return ''.join(sequence)

def encrypt_sequence(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL) -> Tuple[bytes, List[Tuple[int, int]]]:
    """
    Encrypt a DNA sequence using secure self-power decomposition.
    For large sequences (>10,000 bases), splits into chunks to avoid overflow.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        
    Returns:
        Tuple of (encrypted data, removed values)
    """
    # Check if sequence is too large and needs chunking
    if len(sequence) > MAX_CHUNK_SIZE:
        return encrypt_large_sequence(sequence, num_removed)
    
    # Convert DNA to number
    number = dna_to_number(sequence)
    print(f"[DEBUG] Original sequence: {sequence}")
    print(f"[DEBUG] Converted number: {number}")
    
    # Encrypt using secure self-power decomposition
    encoded_data, removed_values = secure_encode_number_no_placeholder(number, num_removed)
    print(f"[DEBUG] Encrypted data size: {len(encoded_data)}")
    print(f"[DEBUG] Removed values: {removed_values}")
    
    return encoded_data, removed_values

def encrypt_large_sequence(sequence: str, num_removed: int = DEFAULT_SECURITY_LEVEL) -> Tuple[bytes, List[Tuple[int, int]]]:
    """
    Encrypt a large DNA sequence by splitting it into chunks.
    
    Args:
        sequence: DNA sequence string
        num_removed: Number of values to remove for the key
        
    Returns:
        Tuple of (encrypted data, removed values)
    """
    # Split the sequence into chunks
    chunks = [sequence[i:i+MAX_CHUNK_SIZE] for i in range(0, len(sequence), MAX_CHUNK_SIZE)]
    num_chunks = len(chunks)
    
    # Encrypt each chunk
    chunk_data = []
    chunk_keys = []
    
    for chunk in chunks:
        # Convert DNA to number
        number = dna_to_number(chunk)
        
        # Encrypt using secure self-power decomposition
        # Use fewer removed values for each chunk to keep key size reasonable
        chunk_num_removed = max(1, num_removed // num_chunks)
        encoded_data, removed_values = secure_encode_number_no_placeholder(number, chunk_num_removed)
        
        chunk_data.append(encoded_data)
        chunk_keys.append(removed_values)
    
    # Combine the encrypted data
    # Format: [num_chunks (4 bytes)] + [chunk1_size (4 bytes) + chunk1_data] + [chunk2_size (4 bytes) + chunk2_data] + ...
    combined_data = struct.pack('<I', num_chunks)
    
    for data in chunk_data:
        combined_data += struct.pack('<I', len(data))
        combined_data += data
    
    # Store chunk keys with their indices
    # Format: [(chunk_index, key_values)]
    combined_keys = []
    for i, key in enumerate(chunk_keys):
        combined_keys.append((i, key))
    
    return combined_data, combined_keys

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
    # Check if this is a chunked sequence
    if len(encoded_data) >= 4 and isinstance(removed_values, list) and len(removed_values) > 0 and isinstance(removed_values[0], tuple) and len(removed_values[0]) == 2 and isinstance(removed_values[0][0], int) and isinstance(removed_values[0][1], list):
        return decrypt_large_sequence(encoded_data, removed_values, expected_length)
    
    # Decrypt using secure self-power decomposition
    number = secure_decode_number_no_placeholder(encoded_data, removed_values)
    print(f"[DEBUG] Decrypted number: {number}")
    
    # Convert number back to DNA
    sequence = number_to_dna(number, expected_length)
    print(f"[DEBUG] Decrypted sequence: {sequence}")
    
    return sequence

def decrypt_large_sequence(encoded_data: bytes, chunk_keys: List[Tuple[int, List[Tuple[int, int]]]], expected_length: int = None) -> str:
    """
    Decrypt a large DNA sequence that was split into chunks.
    
    Args:
        encoded_data: Encrypted sequence data
        chunk_keys: List of (chunk_index, key_values) tuples
        expected_length: Expected length of the original sequence
        
    Returns:
        Decrypted DNA sequence
    """
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
            chunk_length = MAX_CHUNK_SIZE if i < num_chunks - 1 else None
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

def _encrypt_sequence_worker(args):
    """
    Worker function for parallel sequence encryption.
    
    Args:
        args: Tuple of (sequence, num_removed)
        
    Returns:
        Tuple of (encoded_data, removed_values)
    """
    sequence, num_removed = args
    return encrypt_sequence(sequence, num_removed)

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

def encrypt_fasta(input_fasta: str, output_spd: str, output_key: str, num_removed: int = DEFAULT_SECURITY_LEVEL, parallel: bool = True, num_processes: int = None) -> None:
    """
    Encrypt a FASTA file to SPD format with a separate key file.
    
    Args:
        input_fasta: Path to input FASTA file
        output_spd: Path to output SPD file
        output_key: Path to output key file
        num_removed: Number of values to remove for the key
        parallel: Whether to use parallel processing for multiple sequences
        num_processes: Number of processes to use (defaults to number of CPU cores)
    """
    # Read sequences from FASTA file
    sequences = []
    seq_lengths = []
    seq_ids = []
    seq_descriptions = []
    
    with open(input_fasta, 'r') as fasta_file:
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequences.append(str(record.seq))
            seq_lengths.append(len(record.seq))
            seq_ids.append(record.id)
            seq_descriptions.append(record.description)
    
    # Encrypt each sequence
    encrypted_data = []
    all_removed_values = []
    
    # Use parallel processing if enabled and there are multiple sequences
    if parallel and len(sequences) > 1:
        # Determine number of processes
        if num_processes is None:
            num_processes = min(multiprocessing.cpu_count(), len(sequences))
        
        print(f"Using {num_processes} processes to encrypt {len(sequences)} sequences")
        
        # Prepare arguments for each sequence
        args = [(sequences[i], num_removed) for i in range(len(sequences))]
        
        # Process sequences in parallel
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map(_encrypt_sequence_worker, args)
            
            # Collect results
            encrypted_data = [result[0] for result in results]
            all_removed_values = [result[1] for result in results]
    else:
        # Sequential processing
        for sequence in sequences:
            encoded_data, removed_values = encrypt_sequence(sequence, num_removed)
            encrypted_data.append(encoded_data)
            all_removed_values.append(removed_values)
    
    # Write encrypted data to SPD file
    with open(output_spd, 'wb') as f:
        # Write header
        f.write(b'DNASP001')  # Magic number and version
        f.write(struct.pack('<I', len(sequences)))  # Number of sequences
        
        # Write sequence metadata
        for i in range(len(sequences)):
            # Write sequence ID and description
            id_bytes = seq_ids[i].encode('utf-8')
            desc_bytes = seq_descriptions[i].encode('utf-8')
            
            f.write(struct.pack('<I', len(id_bytes)))
            f.write(id_bytes)
            
            f.write(struct.pack('<I', len(desc_bytes)))
            f.write(desc_bytes)
            
            # Write sequence length
            f.write(struct.pack('<I', seq_lengths[i]))
            
            # Write encrypted data
            f.write(struct.pack('<I', len(encrypted_data[i])))
            f.write(encrypted_data[i])
    
    # Write key data to key file
    with open(output_key, 'wb') as f:
        # Write header
        f.write(b'DNAKY001')  # Magic number and version
        f.write(struct.pack('<I', len(sequences)))  # Number of sequences
        
        # Write removed values for each sequence
        for i in range(len(sequences)):
            # Write sequence ID
            id_bytes = seq_ids[i].encode('utf-8')
            f.write(struct.pack('<I', len(id_bytes)))
            f.write(id_bytes)
            
            # Create a temporary file for the removed values
            fd, temp_file = tempfile.mkstemp(suffix='.tmp')
            os.close(fd)
            
            try:
                # Serialize the removed values
                # For chunked sequences, we need to serialize the chunk keys differently
                if isinstance(all_removed_values[i], list) and len(all_removed_values[i]) > 0 and isinstance(all_removed_values[i][0], tuple) and len(all_removed_values[i][0]) == 2 and isinstance(all_removed_values[i][0][0], int) and isinstance(all_removed_values[i][0][1], list):
                    # This is a chunked sequence
                    with open(temp_file, 'wb') as temp:
                        # Write a flag indicating this is a chunked sequence
                        temp.write(b'CHUNK001')
                        
                        # Write the number of chunks
                        temp.write(struct.pack('<I', len(all_removed_values[i])))
                        
                        # Write each chunk's key
                        for chunk_idx, chunk_key in all_removed_values[i]:
                            # Write chunk index
                            temp.write(struct.pack('<I', chunk_idx))
                            
                            # Create a nested temporary file for the chunk key
                            fd_chunk, chunk_temp_file = tempfile.mkstemp(suffix='.tmp')
                            os.close(fd_chunk)
                            
                            try:
                                # Save chunk key to temporary file
                                save_removed_info_no_placeholder(chunk_key, chunk_temp_file)
                                
                                # Read the chunk key file and write its contents
                                with open(chunk_temp_file, 'rb') as chunk_temp:
                                    chunk_key_data = chunk_temp.read()
                                    temp.write(struct.pack('<I', len(chunk_key_data)))
                                    temp.write(chunk_key_data)
                            finally:
                                # Clean up the chunk temporary file
                                if os.path.exists(chunk_temp_file):
                                    os.remove(chunk_temp_file)
                else:
                    # This is a regular sequence
                    save_removed_info_no_placeholder(all_removed_values[i], temp_file)
                
                # Read the temporary file and write its contents to the key file
                with open(temp_file, 'rb') as temp:
                    key_data = temp.read()
                    f.write(struct.pack('<I', len(key_data)))
                    f.write(key_data)
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)

def decrypt_fasta(input_spd: str, input_key: str, output_fasta: str, parallel: bool = True, num_processes: int = None) -> None:
    """
    Decrypt an SPD file to FASTA format using the key file.
    
    Args:
        input_spd: Path to input SPD file
        input_key: Path to input key file
        output_fasta: Path to output FASTA file
        parallel: Whether to use parallel processing for multiple sequences
        num_processes: Number of processes to use (defaults to number of CPU cores)
    """
    # Read encrypted data from SPD file
    with open(input_spd, 'rb') as f:
        # Read header
        magic = f.read(8)
        if magic != b'DNASP001':
            raise ValueError("Invalid SPD file format")
        
        num_sequences = struct.unpack('<I', f.read(4))[0]
        
        # Read sequence data
        seq_ids = []
        seq_descriptions = []
        seq_lengths = []
        encrypted_data = []
        
        for _ in range(num_sequences):
            # Read sequence ID and description
            id_len = struct.unpack('<I', f.read(4))[0]
            id_bytes = f.read(id_len)
            
            desc_len = struct.unpack('<I', f.read(4))[0]
            desc_bytes = f.read(desc_len)
            
            seq_ids.append(id_bytes.decode('utf-8'))
            seq_descriptions.append(desc_bytes.decode('utf-8'))
            
            # Read sequence length
            seq_len = struct.unpack('<I', f.read(4))[0]
            seq_lengths.append(seq_len)
            
            # Read encrypted data
            data_len = struct.unpack('<I', f.read(4))[0]
            data = f.read(data_len)
            encrypted_data.append(data)
    
    # Read key data from key file
    with open(input_key, 'rb') as f:
        # Read header
        magic = f.read(8)
        if magic != b'DNAKY001':
            raise ValueError("Invalid key file format")
        
        key_num_sequences = struct.unpack('<I', f.read(4))[0]
        if key_num_sequences != num_sequences:
            raise ValueError("Key file does not match SPD file")
        
        # Read removed values for each sequence
        all_removed_values = []
        
        for _ in range(num_sequences):
            # Read sequence ID
            id_len = struct.unpack('<I', f.read(4))[0]
            id_bytes = f.read(id_len)
            
            # Create a temporary file for the removed values
            fd, temp_file = tempfile.mkstemp(suffix='.tmp')
            os.close(fd)
            
            try:
                # Read key data length
                key_data_len = struct.unpack('<I', f.read(4))[0]
                key_data = f.read(key_data_len)
                
                # Write key data to temporary file
                with open(temp_file, 'wb') as temp:
                    temp.write(key_data)
                
                # Check if this is a chunked sequence
                with open(temp_file, 'rb') as temp:
                    magic_check = temp.read(8)
                    if magic_check == b'CHUNK001':
                        # This is a chunked sequence
                        chunk_keys = []
                        
                        # Read the number of chunks
                        with open(temp_file, 'rb') as temp:
                            temp.seek(8)  # Skip the magic number
                            num_chunks = struct.unpack('<I', temp.read(4))[0]
                            
                            # Read each chunk's key
                            for _ in range(num_chunks):
                                # Read chunk index
                                chunk_idx = struct.unpack('<I', temp.read(4))[0]
                                
                                # Read chunk key data
                                chunk_key_len = struct.unpack('<I', temp.read(4))[0]
                                chunk_key_data = temp.read(chunk_key_len)
                                
                                # Create a temporary file for the chunk key
                                fd_chunk, chunk_temp_file = tempfile.mkstemp(suffix='.tmp')
                                os.close(fd_chunk)
                                
                                try:
                                    # Write chunk key data to temporary file
                                    with open(chunk_temp_file, 'wb') as chunk_temp:
                                        chunk_temp.write(chunk_key_data)
                                    
                                    # Load chunk key from temporary file
                                    chunk_key = load_removed_info_no_placeholder(chunk_temp_file)
                                    chunk_keys.append((chunk_idx, chunk_key))
                                finally:
                                    # Clean up the chunk temporary file
                                    if os.path.exists(chunk_temp_file):
                                        os.remove(chunk_temp_file)
                        
                        all_removed_values.append(chunk_keys)
                    else:
                        # This is a regular sequence
                        removed_values = load_removed_info_no_placeholder(temp_file)
                        all_removed_values.append(removed_values)
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    # Decrypt sequences
    # Use parallel processing if enabled and there are multiple sequences
    if parallel and num_sequences > 1:
        # Determine number of processes
        if num_processes is None:
            num_processes = min(multiprocessing.cpu_count(), num_sequences)
        
        print(f"Using {num_processes} processes to decrypt {num_sequences} sequences")
        
        # Prepare arguments for each sequence
        args = [(encrypted_data[i], all_removed_values[i], seq_lengths[i]) for i in range(num_sequences)]
        
        # Process sequences in parallel
        with multiprocessing.Pool(processes=num_processes) as pool:
            decrypted_sequences = pool.map(_decrypt_sequence_worker, args)
    else:
        # Sequential processing
        decrypted_sequences = []
        for i in range(num_sequences):
            sequence = decrypt_sequence(encrypted_data[i], all_removed_values[i], seq_lengths[i])
            decrypted_sequences.append(sequence)
    
    # Write decrypted sequences to FASTA file
    with open(output_fasta, 'w') as f:
        for i in range(num_sequences):
            f.write(f">{seq_descriptions[i]}\n")
            
            # Write sequence with line wrapping at 60 characters
            seq = decrypted_sequences[i]
            for j in range(0, len(seq), 60):
                f.write(seq[j:j+60] + "\n")
