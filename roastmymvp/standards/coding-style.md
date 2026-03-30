# AI Beta Test — Coding Standards

## Python Style
- Python 3.12+
- Type hints on all function signatures
- `@dataclass(frozen=True)` for all data objects — no mutation
- Functions < 50 lines, files < 400 lines
- One class per file, one responsibility per module

## Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

## Error Handling
- Never silently swallow exceptions
- User-facing errors: clear message + suggestion
- Internal errors: log with context, re-raise

## Dependencies
- Minimize dependencies — stdlib first
- Required: `playwright`, `anthropic`, `click`, `pyyaml`
- No unnecessary abstractions for one-time operations

## File Size Limits
- Module file: < 400 lines
- Function: < 50 lines
- Prompt template: < 200 lines
- Test file: < 300 lines
