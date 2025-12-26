# Antigravity Project Rules

You are an expert Python/Django developer working on `senhaunica-socialite-python`.
Follow these strict guidelines when generating or refactoring code.

## 1. Code Standards (PEP 8 & Type Hints)
- **Static Typing**: MUST use modern Python 3.12+ Type Hints for ALL function arguments and return values.
  - Incorrect: `def authenticate(request):`
  - Correct: `def authenticate(request: HttpRequest) -> Optional[AbstractBaseUser]:`
- **Docstrings**: ALL public classes and methods MUST have Google Style docstrings (PEP 257).

## 2. Structure & Imports
- **Import Order**: Standard Library > Third Party (Django, Authlib, SQLAlchemy) > Local Imports.
- **Prohibited**: Do NOT use `from module import *`.

## 3. OAuth 1.0 Specifics (Authlib)
- **Class Implementation**: Prioritize `authlib.integrations.requests_client.OAuth1Session` for connection logic.
- **USP Endpoint Quirk**: The `request_token` endpoint returns a query-encoded string, NOT JSON. You MUST handle parsing manually or verify strict library support for this content type. Do not assume JSON response.
