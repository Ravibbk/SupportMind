# Contributing to SupportMind

Thank you for your interest in contributing to SupportMind! This project follows production-grade software engineering and machine learning engineering standards.

## Development Workflow

1. **Branching Strategy**:
   - Feature branches: `feat/<feature-name>` (e.g., `feat/rag-hybrid`, `feat/ui-chat`)
   - Bug fixes: `fix/<issue-name>`
   - Documentation & Chore: `docs/<name>`, `chore/<name>`

2. **Commit Conventions**:
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(rag): ...`
   - `feat(agents): ...`
   - `feat(ml): ...`
   - `test(api): ...`
   - `chore(devops): ...`

3. **Running Checks Locally**:
   - Python Linting: `ruff check backend/`
   - Unit Tests: `pytest backend/tests/`
   - Frontend Tests: `npm test` inside `frontend/`

4. **Security & Secrets**:
   - Never commit `.env` files or API keys.
   - Guardrails and sanitizers are enforced across the codebase.
