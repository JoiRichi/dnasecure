# DNAsecure

DNA sequence encryption and security using self-power decomposition.

## Overview

DNAsecure is a Python package that provides tools for encrypting and decrypting DNA sequences using the self-power decomposition algorithm. It is built on top of the `selfpowerdecomposer` package and provides specialized functionality for working with DNA sequences and FASTA files.

The package uses a secure encryption approach that splits the encryption into two parts:
1. The main encrypted data (stored in `.spd` files)
2. A key file (stored in `.key` files)

Both parts are required to decrypt the data, providing a secure way to store and share DNA sequences.

## Installation

```bash
pip install dnasecure
```

## Dependencies

- selfpowerdecomposer >= 0.1.1
- numpy >= 1.19.0
- biopython >= 1.79

## Usage

### Command Line Interface

DNAsecure provides a command-line interface for easy encryption and decryption of FASTA files:

```bash
# Encrypt a FASTA file
dnasecure encrypt input.fasta output.spd output.key --security-level 5

# Decrypt an SPD file back to FASTA
dnasecure decrypt output.spd output.key decrypted.fasta

# Show help
dnasecure --help
```

### Parallel Processing

DNAsecure supports parallel processing for handling multiple sequences simultaneously, which can significantly improve performance when working with multiFASTA files:

```bash
# Encrypt a FASTA file using parallel processing
dnasecure encrypt input.fasta output.spd output.key --parallel --num-processes 4

# Decrypt an SPD file using parallel processing
dnasecure decrypt output.spd output.key decrypted.fasta --parallel --num-processes 4
```

You can also disable parallel processing if needed:

```bash
dnasecure encrypt input.fasta output.spd output.key --no-parallel
```

#### Performance Improvement

Parallel processing can provide significant speedup when working with multiFASTA files. In our benchmarks with a 30MB FASTA file containing 10 sequences:

- **Encryption**: 5.37x speedup (42.18s → 7.86s)
- **Decryption**: 5.95x speedup (111.53s → 18.75s)

The speedup scales with the number of sequences and available CPU cores.

### Python API

#### Basic Usage

```python
from dnasecure import encrypt_sequence, decrypt_sequence

# Encrypt a DNA sequence
sequence = "ATGCATGCATGCATGC"
encrypted_data, key = encrypt_sequence(sequence)

# Decrypt the sequence
decrypted_sequence = decrypt_sequence(encrypted_data, key)
print(decrypted_sequence)  # Should print the original sequence
```

#### Working with FASTA Files

```python
from dnasecure import encrypt_fasta, decrypt_fasta

# Encrypt a FASTA file
encrypt_fasta("input.fasta", "output.spd", "output.key")

# Decrypt an SPD file back to FASTA
decrypt_fasta("output.spd", "output.key", "decrypted.fasta")
```

#### Using Parallel Processing in Python

```python
from dnasecure import encrypt_fasta, decrypt_fasta

# Encrypt a FASTA file with parallel processing
encrypt_fasta(
    "input.fasta", 
    "output.spd", 
    "output.key", 
    parallel=True, 
    num_processes=4  # Use 4 processes
)

# Decrypt an SPD file with parallel processing
decrypt_fasta(
    "output.spd", 
    "output.key", 
    "decrypted.fasta", 
    parallel=True, 
    num_processes=4  # Use 4 processes
)
```

## Security Features

DNAsecure provides strong security for DNA sequences:

1. **Two-part encryption**: The encryption is split into two parts (data and key), both of which are required for decryption.
2. **Self-power decomposition**: Uses a novel mathematical approach for compression and encryption.
3. **No placeholders**: The encryption does not use placeholders for removed values, making it harder to identify what was removed.
4. **Resistance to brute force**: The encryption is resistant to brute force attacks due to the large key space.

## Examples

See the `examples` directory for more detailed usage examples.

## License

MIT License
