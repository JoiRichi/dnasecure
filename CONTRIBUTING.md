# Contributing to DNAsecure

Thank you for considering contributing to DNAsecure! This document provides guidelines and instructions for contributing to this project.

## How Can I Contribute?

### Reporting Bugs

If you find a bug in the software, please create an issue on GitHub with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any additional context (e.g., operating system, Python version)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any potential implementation details
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as necessary
6. Submit a pull request

## Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Coding Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. Please ensure your code adheres to this standard.

## Testing

Please add tests for any new features or bugfixes. Run the test suite before submitting a pull request:

```bash
pytest
```

## Documentation

Please update the documentation for any changes to the API or functionality. This includes:

- Docstrings
- README.md
- Examples

## Versioning

This project follows [Semantic Versioning](https://semver.org/). Please ensure that version numbers are updated appropriately in pull requests.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 