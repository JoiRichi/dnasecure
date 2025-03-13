#!/usr/bin/env python3
"""
DNAsecure Command Line Interface

This module provides a command-line interface for the DNAsecure package,
allowing users to encrypt and decrypt DNA sequences in FASTA files.
"""

import argparse
import os
import sys
import multiprocessing
from typing import List

from dnasecure import (
    encrypt_fasta,
    decrypt_fasta,
    DEFAULT_SECURITY_LEVEL,
    __version__
)

def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DNAsecure - DNA sequence encryption using self-power decomposition",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"DNAsecure v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a FASTA file to SPD format with a separate key file"
    )
    encrypt_parser.add_argument(
        "input_fasta",
        help="Path to input FASTA file"
    )
    encrypt_parser.add_argument(
        "output_spd",
        help="Path to output SPD file"
    )
    encrypt_parser.add_argument(
        "output_key",
        help="Path to output key file"
    )
    encrypt_parser.add_argument(
        "--security-level",
        type=int,
        default=DEFAULT_SECURITY_LEVEL,
        help=f"Number of values to remove for security (default: {DEFAULT_SECURITY_LEVEL})"
    )
    encrypt_parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Use parallel processing for multiple sequences (default: True)"
    )
    encrypt_parser.add_argument(
        "--no-parallel",
        action="store_false",
        dest="parallel",
        help="Disable parallel processing"
    )
    encrypt_parser.add_argument(
        "--num-processes",
        type=int,
        default=None,
        help=f"Number of processes to use for parallel processing (default: number of CPU cores, {multiprocessing.cpu_count()})"
    )
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt an SPD file to FASTA format using the key file"
    )
    decrypt_parser.add_argument(
        "input_spd",
        help="Path to input SPD file"
    )
    decrypt_parser.add_argument(
        "input_key",
        help="Path to input key file"
    )
    decrypt_parser.add_argument(
        "output_fasta",
        help="Path to output FASTA file"
    )
    decrypt_parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Use parallel processing for multiple sequences (default: True)"
    )
    decrypt_parser.add_argument(
        "--no-parallel",
        action="store_false",
        dest="parallel",
        help="Disable parallel processing"
    )
    decrypt_parser.add_argument(
        "--num-processes",
        type=int,
        default=None,
        help=f"Number of processes to use for parallel processing (default: number of CPU cores, {multiprocessing.cpu_count()})"
    )
    
    return parser.parse_args(args)

def main(args: List[str] = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)
    
    try:
        if parsed_args.command == "encrypt":
            print(f"Encrypting {parsed_args.input_fasta}...")
            encrypt_fasta(
                parsed_args.input_fasta,
                parsed_args.output_spd,
                parsed_args.output_key,
                parsed_args.security_level,
                parallel=parsed_args.parallel,
                num_processes=parsed_args.num_processes
            )
            print(f"Encrypted data saved to {parsed_args.output_spd}")
            print(f"Key saved to {parsed_args.output_key}")
            
        elif parsed_args.command == "decrypt":
            print(f"Decrypting {parsed_args.input_spd}...")
            decrypt_fasta(
                parsed_args.input_spd,
                parsed_args.input_key,
                parsed_args.output_fasta,
                parallel=parsed_args.parallel,
                num_processes=parsed_args.num_processes
            )
            print(f"Decrypted data saved to {parsed_args.output_fasta}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 