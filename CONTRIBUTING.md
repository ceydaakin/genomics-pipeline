# Contributing to Genomics Pipeline

Thank you for your interest in contributing to the Genomics Pipeline project! 🧬

## How to Contribute

### 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/ceydaakin/genomics-pipeline/issues)
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, conda environment)
   - Log files if available

### 🚀 Suggesting Enhancements

1. Check existing [Issues](https://github.com/ceydaakin/genomics-pipeline/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the enhancement
   - Use case and motivation
   - Proposed implementation approach

### 🔧 Code Contributions

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ceydaakin/genomics-pipeline.git
cd genomics-pipeline

# Install development dependencies
./scripts/install_comprehensive_genomics_tools.sh

# Run tests
python tests/test_complete_pipeline.py
```

#### Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Run the test suite: `python tests/test_complete_pipeline.py`
6. Commit your changes: `git commit -m "feat: add amazing feature"`
7. Push to your branch: `git push origin feature/amazing-feature`
8. Create a Pull Request

#### Commit Messages

Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring

### 📝 Documentation

- Update README.md if your changes affect usage
- Add docstrings to new functions and classes
- Update installation guide if dependencies change
- Add examples for new features

### 🧪 Testing

- Add tests for new features
- Ensure all existing tests pass
- Test with different bacterial genome datasets
- Verify pipeline works end-to-end

### 🏗️ Project Structure

```
genomics-pipeline/
├── src/                    # Core Python modules
├── scripts/               # Shell scripts for installation and execution
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/             # Usage examples
├── configs/              # Configuration templates
└── data/                 # Data directory structure
```

### 🔧 Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small
- Use type hints where appropriate

### 🛡️ Security

- Never commit sensitive information (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices for bioinformatics tools

### 📊 Adding New Analysis Tools

When adding new bioinformatics tools:

1. Update `install_comprehensive_genomics_tools.sh`
2. Add tool configuration to `genomics_config.py`
3. Create analysis function in appropriate module
4. Add strain name handling
5. Update output organization
6. Add tests
7. Update documentation

### 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

### 📞 Getting Help

- Open an [Issue](https://github.com/ceydaakin/genomics-pipeline/issues) for questions
- Join discussions about improvements
- Ask for clarification if contribution guidelines are unclear

---

**Thank you for contributing to making genomics analysis more accessible! 🧬✨**