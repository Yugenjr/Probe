# Contributing to DriftGuard Probe

Thank you for investing your time in contributing to DriftGuard Probe! We build our open-source MLOps tools around strict clean architecture principles, high code reliability, and extensible plugin designs.

## Development Standards
1. **Python 3.12+ Required**: Utilize modern type hints and syntax.
2. **Strict Typing & Linting**: All incoming code must pass `mypy` type validation and `ruff` lint rules.
3. **No Direct Platform Coupling**: When interacting with external platforms (DriftGuard, MCP, etc.), ALWAYS utilize or implement the appropriate protocol inside `probe/interfaces/`. Never import external platform packages directly into core agent logic.
4. **Structured Testing**: Every new capability or agent must be accompanied by non-blocking unit tests in `tests/`.

## PR Process
- Create a topic branch from `main`.
- Include meaningful docstrings on public methods and Pydantic v2 domain schemas.
- Run `pytest` and ensure all tests pass with clear tracebacks.
