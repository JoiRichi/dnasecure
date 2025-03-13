"""
DNAsecure - DNA sequence encryption using self-power decomposition

This package provides tools for encrypting and decrypting DNA sequences using
the self-power decomposition algorithm from the selfpowerdecomposer package.

Main functions:
- encrypt_fasta: Encrypt a FASTA file to SPD format with a separate key file
- decrypt_fasta: Decrypt an SPD file to FASTA format using the key file
- encrypt_sequence: Encrypt a single DNA sequence
- decrypt_sequence: Decrypt a single DNA sequence
"""

from .core import (
    encrypt_fasta,
    decrypt_fasta,
    encrypt_sequence,
    decrypt_sequence,
    dna_to_number,
    number_to_dna,
    DEFAULT_SECURITY_LEVEL
)

__version__ = '0.0.1'
