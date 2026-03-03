# Contributing to YatsurugiCapture

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/YatsurugiCapture.git
cd YatsurugiCapture
```

### 2. Install Dependencies

**Option A: Using pip (Recommended - Consistent across all platforms)**

```bash
# Install system dependencies
# Arch/CachyOS
sudo pacman -S v4l-utils portaudio

# Ubuntu/Debian
sudo apt-get install v4l-utils portaudio19-dev python3-dev

# Then install Python dependencies
pip install -r requirements-dev.txt  # Includes all dev tools
```

**Option B: Using system packages (Arch/CachyOS only)**

```bash
# Install most dependencies via pacman
sudo pacman -S python-pyqt5 python-opencv v4l-utils portaudio

# Install remaining packages via pip
pip install pyaudio pytest pytest-mock autoflake pylint flake8 black mypy pyinstaller
```

**Why Option A is recommended:**
- ✅ Same versions for all contributors
- ✅ Works on Windows/macOS/Linux
- ✅ PyInstaller builds work consistently
- ✅ Easier dependency management

## Code Quality

We use several tools to maintain code quality:

### Running Code Quality Checks

```bash
# Check for unused imports
autoflake --check --remove-all-unused-imports --recursive src/ tests/

# Run linter (flake8)
flake8 src/ tests/

# Check code formatting (black)
black --check src/ tests/

# Auto-format code
black src/ tests/

# Run all tests
pytest tests/
```

### Pre-commit Checks

Before committing, ensure:
- ✅ No unused imports
- ✅ Code passes flake8 linting
- ✅ Code is formatted with black
- ✅ All tests pass

### Code Style Guidelines

- **Line length**: Maximum 127 characters
- **Formatting**: Use `black` for automatic formatting
- **Imports**: Remove unused imports with `autoflake`
- **Naming**: Follow PEP 8 naming conventions
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clean, readable code
- Add docstrings to new functions/classes
- Update tests if needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run tests
pytest tests/

# Run the application
python3 src/capture_app.py

# Test building
scripts/build_release.sh
```

### 4. Run Quality Checks

```bash
# Check and fix imports
autoflake --in-place --remove-all-unused-imports --recursive src/ tests/

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "type: brief description"
```

**Commit message types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Build process or auxiliary tool changes
- `deps:` Dependency updates

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated if needed
- [ ] No unused imports or code
- [ ] Code formatted with black
- [ ] Commit messages are clear and descriptive

### PR Description

Include in your PR description:
- **What**: What does this PR do?
- **Why**: Why is this change needed?
- **How**: How does it work?
- **Testing**: How was it tested?

## Dependency Management

### Adding New Dependencies

If you need to add a new dependency:

1. Add to `requirements.txt` (runtime) or `requirements-dev.txt` (development)
2. Document why it's needed
3. Ensure it's compatible with Python 3.7+
4. Check for security vulnerabilities

### Updating Dependencies

Dependencies are managed automatically by Dependabot, but you can update manually:

```bash
pip install --upgrade package-name
pip freeze > requirements.txt
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_feature_does_something()`
- Use pytest fixtures for setup/teardown
- Mock external dependencies

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_capture_app.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

## Building and Releasing

### Local Build

```bash
# Build executable
scripts/build_release.sh

# Test the build
./dist/YatsurugiCapture
```

### Creating a Release

Releases are automated via CI/CD:

1. Ensure all changes are committed and pushed
2. Create and push a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions automatically builds and releases

## Getting Help

- 📖 Read the [documentation](../README.md)
- 🐛 [Report bugs](https://github.com/yourusername/YatsurugiCapture/issues)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/YatsurugiCapture/discussions)

## Code of Conduct

Be respectful and constructive. This is an open source project maintained by volunteers.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
