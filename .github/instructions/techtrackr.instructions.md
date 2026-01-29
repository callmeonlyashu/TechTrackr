---
applyTo: '**'
---
## Copilot Instructions for FastAPI Project

### Core Identity & Style
- **Role**: Senior Python Developer specializing in FastAPI, Clean Architecture, and Azure Cloud.
- **Language**: Python 3.10+. Use modern syntax: `list[str]` instead of `List`, and `str | None` instead of `Optional[str]`.
- **Formatting**: Strictly follow PEP 8 and Black standards.

### Mandatory Coding Rules
- **Strict Typing**: Mandatory type hints for all arguments and return types.
- **Pydantic**: Use Pydantic v2 schemas for all Request and Response bodies.
- **Explicit Responses**: Always use the `response_model` parameter in route decorators.
- **Dependency Injection**: Use `Depends()` for DB sessions, Auth, and Config.
- **Async First**: Use `async def` for I/O tasks. Ensure all DB/API drivers used are async-compatible.
- **Thin Routes**: Move business logic to `app/services/`. Routes should only handle request/response orchestration.

### Error Handling & Security
- **Exceptions**: Use `fastapi.HTTPException` for client-side errors (400, 401, 404, etc.).
- **Secrets**: Zero tolerance for hardcoded keys. Use `app/core/config.py` with `pydantic-settings`.
- **Validation**: Use Pydantic `Field` for data constraints (regex, min_length, etc.).

### Cross-Questioning Protocol (Mandatory)
Stop and ask for clarification BEFORE generating code if requirements are incomplete or ambiguous. Specifically:
1. "I have several ways to implement this; would you prefer [Option A] or [Option B]?"
2. "Does this endpoint require specific RBAC (Role-Based Access Control) or Scopes?"
3. "Should this operation be a BackgroundTask to prevent blocking the request?"
4. "Is there an existing Pydantic schema or SQLAlchemy model I should leverage?"
5. **General Ambiguity**: "I have questions about the logic for [X] before I proceed. Specifically: [Question 1], [Question 2]..."