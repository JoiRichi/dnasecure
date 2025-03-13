#!/usr/bin/env python3
"""
Generate a large FASTA file with multiple sequences for testing.
"""

import os
import random
import argparse
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def generate_random_dna(length):
    """Generate a random DNA sequence of the specified length."""
    return ''.join(random.choice('ACGT') for _ in range(length))

def generate_large_fasta(output_file, total_size_mb=30, num_sequences=10):
    """
    Generate a large FASTA file with multiple sequences.
    
    Args:
        output_file: Path to output FASTA file
        total_size_mb: Total size of the FASTA file in MB
        num_sequences: Number of sequences to generate
    """
    # Calculate the size of each sequence
    total_size_bytes = total_size_mb * 1024 * 1024
    # Account for headers and newlines in the size calculation
    # Assuming average header length of 50 characters and 60 characters per line
    estimated_overhead_per_seq = 50 + (total_size_bytes / num_sequences / 60)
    seq_size = int((total_size_bytes / num_sequences) - estimated_overhead_per_seq)
    
    # Generate sequences
    records = []
    for i in range(num_sequences):
        # Generate a random DNA sequence
        seq = generate_random_dna(seq_size)
        
        # Create a SeqRecord
        record = SeqRecord(
            Seq(seq),
            id=f"Seq{i+1}",
            description=f"Random DNA sequence {i+1} for testing"
        )
        
        records.append(record)
    
    # Write sequences to FASTA file
    with open(output_file, 'w') as f:
        SeqIO.write(records, f, "fasta")
    
    # Get actual file size
    actual_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"Generated {num_sequences} sequences in {output_file}")
    print(f"Total file size: {actual_size_mb:.2f} MB")
    print(f"Average sequence length: {seq_size:,} bases")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate a large FASTA file with multiple sequences for testing"
    )
    parser.add_argument(
        "output_file",
        help="Path to output FASTA file"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=30,
        help="Total size of the FASTA file in MB (default: 30)"
    )
    parser.add_argument(
        "--num-sequences",
        type=int,
        default=10,
        help="Number of sequences to generate (default: 10)"
    )
    
    args = parser.parse_args()
    
    generate_large_fasta(args.output_file, args.size, args.num_sequences)

if __name__ == "__main__":
    main() 