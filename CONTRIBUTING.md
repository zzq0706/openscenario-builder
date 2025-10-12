# Contributing to OpenSCENARIO Builder

Thank you for your interest in contributing to OpenSCENARIO Builder! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant code snippets or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include code examples if applicable

### Contributing Code

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Ensure all tests pass**
5. **Update documentation** as needed
6. **Submit a pull request**

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/openscenario-builder.git
cd openscenario-builder
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks (Optional but Recommended)

```bash
pre-commit install
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Quotes**: Use double quotes for strings
- **Imports**: Use absolute imports, group by standard library, third-party, and local
- **Type hints**: Use type hints for function signatures

### Code Formatting

We use **Black** for code formatting:

```bash
black src/ tests/ examples/
```

### Linting

We use **flake8** for linting:

```bash
flake8 src/ tests/ examples/
```

### Type Checking

We use **mypy** for type checking:

```bash
mypy src/
```

### Running All Checks

```bash
# Format code
black src/ tests/ examples/

# Check linting
flake8 src/ tests/ examples/

# Type check
mypy src/

# Run tests
pytest
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openscenario_builder --cov-report=html

# Run specific test file
pytest tests/test_element.py

# Run tests matching a pattern
pytest -k "test_validation"
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Include docstrings explaining what is being tested

Example:

```python
def test_element_creation():
    """Test that Element can be created with tag and attributes"""
    element = Element("TestElement", {"attr1": "value1"})
    assert element.tag == "TestElement"
    assert element.attrs["attr1"] == "value1"
```

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for notable changes)
- [ ] Commit messages are clear and descriptive

### Commit Messages

Use clear, concise commit messages:

```
Add feature: element validation for nested structures

- Implement recursive validation
- Add tests for nested element validation
- Update documentation

Fixes #123
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce them

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
```

### Review Process

1. At least one maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR

## Project Structure

```
openscenario-builder/
├── src/
│   └── openscenario_builder/    # Main package
│       ├── core/                # Core functionality
│       ├── interfaces/          # Interface definitions
│       └── ui/                  # UI components
├── tests/                       # Test suite
├── examples/                    # Example scripts
├── docs/                        # Documentation
└── .github/                     # GitHub workflows and templates
```

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in GitHub Discussions
- Reach out to the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
