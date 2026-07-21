"""Shared Langfuse client (reads keys from .env, same singleton as the CallbackHandler)."""

from langfuse import get_client

langfuse = get_client()
