"""Vercel serverless entrypoint. Vercel's Python runtime detects the `app`
ASGI instance in this file and wraps it automatically -- no adapter needed."""
from backend.main import app  # noqa: F401
