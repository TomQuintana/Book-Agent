"""ASGI server entrypoint for the ASTA API."""

import uvicorn

from src.config.logging_config import setup_logging


def main():
    """Start the FastAPI app with uvicorn."""
    setup_logging()
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
