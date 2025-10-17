# Development Setup Guide

This guide helps developers set up a complete development environment for contributing to Scrag.

## Development Prerequisites

- Python 3.8+
- Git
- Docker (optional, for containerized development)
- Node.js (for web interface development)
- Make (for using Makefile commands)

## Setting Up Development Environment

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/scrag.git
cd scrag
```

### 2. Development Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Add API keys, database URLs, etc.
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run tests with coverage
pytest --cov=src/scrag --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Security audit
bandit -r src/
```

### Documentation

```bash
# Generate API docs
cd docs
make html

# Serve docs locally
cd docs/_build/html
python -m http.server 8000
```

## Project Structure for Developers

### Core Modules

- `src/scrag/extractors/` - Implement new extraction strategies here
- `src/scrag/processors/` - Add content processing logic
- `src/scrag/storage/` - Create storage adapters
- `src/scrag/rag/` - RAG pipeline components

### Adding New Features

1. **Create a new extractor**:
   - Implement `BaseExtractor` interface
   - Add configuration schema
   - Write comprehensive tests
   - Update documentation

2. **Add a new processor**:
   - Implement `BaseProcessor` interface
   - Define processing parameters
   - Add to processing pipeline
   - Write unit tests

3. **Create a storage adapter**:
   - Implement `StorageAdapter` interface
   - Handle connection management
   - Add integration tests
   - Update configuration schemas

## Testing Guidelines

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Aim for 90%+ code coverage
- Use pytest fixtures for test data

### Integration Tests
- Test component interactions
- Use real but controlled environments
- Test error handling and edge cases
- Include performance considerations

### Performance Tests
- Benchmark critical paths
- Test scalability limits
- Monitor memory usage
- Use pytest-benchmark

## Contributing Workflow

### Before Making Changes

1. Create a new branch from main
2. Write or update tests first (TDD approach)
3. Implement the feature/fix
4. Ensure all tests pass
5. Update documentation

### Submitting Changes

1. Run the full test suite
2. Check code quality metrics
3. Update CHANGELOG.md
4. Create a detailed pull request
5. Address review feedback

## Debugging

### Common Development Issues

1. **Import errors**: Check PYTHONPATH and virtual environment
2. **Test failures**: Ensure test dependencies are installed
3. **Configuration issues**: Verify config file syntax and paths
4. **Performance issues**: Use profiling tools

### Debugging Tools

```bash
# Python debugger
python -m pdb script.py

# Performance profiling
python -m cProfile -o profile.stats script.py

# Memory profiling
mprof run script.py
mprof plot
```

## IDE Setup

### VS Code
Recommended extensions:
- Python
- Python Docstring Generator
- Black Formatter
- Pylance
- GitLens

### PyCharm
Recommended configuration:
- Enable type checking
- Configure code style (Black)
- Set up run configurations
- Enable pytest as test runner

## Continuous Integration

The project uses GitHub Actions for CI/CD:
- Automated testing on multiple Python versions
- Code quality checks
- Security scanning
- Documentation building
- Automated releases

Local CI simulation:
```bash
# Run the same checks as CI
./scripts/ci_checks.sh
```

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Automated deployment to PyPI

## Getting Help

- Read existing code and tests for patterns
- Check the [Architecture documentation](../../ARCHITECTURE.md)
- Join development discussions on GitHub
- Ask questions in pull request reviews