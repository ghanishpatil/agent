# Architecture Documentation

## Overview

MD-EXPLOIT-ENGINE follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│              User Interface Layer               │
│  (CLI, Web Dashboard, API)                      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Core Engine Layer                  │
│  - ExploitEngine (Orchestrator)                 │
│  - ChallengeClassifier (ML-based)               │
│  - Config Manager                               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Module Registry Layer                │
│  (Dynamic module loading and management)        │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           Solver Modules Layer                  │
│  - WebModule                                    │
│  - CryptoModule                                 │
│  - PwnModule                                    │
│  - ReversingModule                              │
│  - ForensicsModule                              │
│  - OSINTModule                                  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Utilities Layer                      │
│  - Logger                                       │
│  - Database                                     │
│  - External Tool Wrappers                       │
└─────────────────────────────────────────────────┘
```

## Core Components

### ExploitEngine

The main orchestrator that:
- Receives challenge input
- Classifies challenges
- Routes to appropriate modules
- Manages timeouts and retries
- Aggregates results

### ChallengeClassifier

Uses ML and heuristics to:
- Analyze challenge metadata
- Classify into categories
- Extract key information
- Provide confidence scores

### Module Registry

Manages solver modules:
- Dynamic loading
- Enable/disable modules
- Module configuration
- Dependency injection

### Solver Modules

Each module implements `BaseModule` and provides:
- `solve(challenge)` method
- Category-specific techniques
- Flag extraction
- Result reporting

## Data Flow

1. **Input**: Challenge file/URL/description
2. **Parsing**: Extract metadata and files
3. **Classification**: Determine category
4. **Module Selection**: Choose appropriate solver
5. **Execution**: Run solving techniques
6. **Flag Extraction**: Parse output for flags
7. **Result**: Return success/failure with details

## Design Patterns

### Strategy Pattern
Each solver module is a strategy for solving a specific category of challenges.

### Factory Pattern
ModuleRegistry acts as a factory for creating solver instances.

### Observer Pattern
Logging and progress tracking use observer pattern.

### Template Method
BaseModule defines the template for all solvers.

## Extensibility

### Adding New Modules

1. Create new module in `modules/`
2. Inherit from `BaseModule`
3. Implement `solve()` method
4. Register in `ModuleRegistry`

Example:

```python
from .base import BaseModule

class CustomModule(BaseModule):
    def solve(self, challenge):
        # Implementation
        pass
```

### Adding New Techniques

Add methods to existing modules:

```python
def _new_technique(self, data, result):
    # Implementation
    return flag
```

## Performance Considerations

- Multi-threading for parallel solving
- Timeout mechanisms to prevent hanging
- Resource cleanup after each attempt
- Caching of intermediate results
- Docker isolation for safety

## Security

- Safe mode prevents dangerous operations
- Docker isolation for untrusted code
- Rate limiting on API
- Authorization checks
- Audit logging

## Testing Strategy

- Unit tests for each module
- Integration tests for workflows
- Mock external dependencies
- Test with sample challenges
- Performance benchmarks
