# Contributing to MD-EXPLOIT-ENGINE

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Use this tool ethically and legally

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a detailed issue with:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Relevant logs or screenshots

### Suggesting Features

1. Check if the feature has been suggested
2. Create an issue describing:
   - The problem it solves
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/md-exploit-engine.git
   cd md-exploit-engine
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation
   - Keep commits focused and atomic

4. **Test your changes**
   ```bash
   pytest
   python main.py --help
   ```

5. **Submit a pull request**
   - Describe what changed and why
   - Reference related issues
   - Ensure CI passes

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/md-exploit-engine.git
cd md-exploit-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions focused and small
- Use meaningful variable names

### Example

```python
def solve_challenge(self, challenge: Challenge) -> ChallengeResult:
    """
    Solve a CTF challenge
    
    Args:
        challenge: Challenge to solve
    
    Returns:
        ChallengeResult with outcome
    """
    # Implementation
    pass
```

## Adding New Modules

To add a new solver module:

1. Create file in `modules/` directory
2. Inherit from `BaseModule`
3. Implement `solve()` method
4. Add to `ModuleRegistry`
5. Write tests
6. Update documentation

Example:

```python
from .base import BaseModule
from core.challenge import Challenge, ChallengeResult

class NewModule(BaseModule):
    """Description of module"""
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        result = self.create_result(challenge, False)
        
        # Your solving logic here
        
        return result
```

## Testing Guidelines

- Write tests for new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Mock external dependencies
- Test edge cases and error conditions

## Documentation

- Update README.md for major changes
- Add docstrings to new code
- Update relevant docs/ files
- Include usage examples
- Keep documentation clear and concise

## Pull Request Process

1. Update documentation
2. Add tests
3. Ensure all tests pass
4. Update CHANGELOG if applicable
5. Request review from maintainers
6. Address review feedback
7. Squash commits if requested

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Contact maintainers

Thank you for contributing to MD-EXPLOIT-ENGINE!
