# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2025-03-15

### Fixed
- Fixed issue with small chunk sizes in decrypt_large_sequence function
- Resolved FASTA file encryption/decryption problems with various chunk sizes
- Improved chunk size detection during decryption process

## [0.0.2] - 2025-03-14

### Added
- Made chunk size configurable through CLI and API
- Added comprehensive benchmarking for different chunk sizes
- Added parallel processing support for both encryption and decryption

### Changed
- Improved security by maintaining full security level for each chunk
- Enhanced documentation with detailed explanations of DNA encoding
- Optimized performance for large sequence processing

### Fixed
- Fixed security issue with distributed keys across chunks

## [0.0.1] - 2025-03-13

### Added
- Initial release of DNAsecure
- Core functionality for DNA sequence encryption and decryption
- Support for FASTA file format
- Command-line interface for easy usage
- Parallel processing for improved performance with multiple sequences
- Chunking support for large sequences (>10,000 bases)
- Comprehensive documentation and examples
- Benchmark tools for performance evaluation

### Changed
- Updated DNA base to number mapping to start from 1 to avoid leading zero issues
- Set chunking to occur at around 10,000 bases in length
- Properly handle user-defined key size with default if not provided

### Fixed
- Resolved issues with encoding and decoding DNA sequences
- Fixed handling of leading zeros in DNA sequences 