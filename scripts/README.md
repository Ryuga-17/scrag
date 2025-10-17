# Development and Build Scripts

This directory contains scripts for development, building, and maintenance tasks.

## Available Scripts

### Development
- `setup_dev.sh` - Set up development environment
- `install_deps.sh` - Install all dependencies
- `run_tests.sh` - Run the complete test suite
- `lint.sh` - Run code linting and formatting
- `generate_docs.sh` - Generate API documentation

### Build and Release
- `build.sh` - Build the application for production
- `package.sh` - Create distribution packages
- `release.sh` - Automated release process
- `version_bump.sh` - Bump version numbers

### Maintenance
- `cleanup.sh` - Clean temporary files and caches
- `update_deps.sh` - Update dependencies
- `security_audit.sh` - Run security audits
- `performance_profile.sh` - Profile application performance

## Usage

Make scripts executable before running:
```bash
chmod +x scripts/*.sh
```

Run development setup:
```bash
./scripts/setup_dev.sh
```