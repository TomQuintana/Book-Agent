"""Verifica que el checkpointer persiste estado en books.db y aísla conversaciones.

Es la razón de ser del cambio (antes, con InMemorySaver, se perdía todo y no
había noción de conversaciones separadas).

Usage:
    uv run python -m src.scripts.check_checkpointer
"""

from src.graph.checkpointer import checkpointer, list_conversations


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}


def _checkpoint(cp_id: str, x: int) -> dict:
    return {
        "id": cp_id,
        "ts": "2026-07-28T00:00:00+00:00",
        "channel_values": {"x": x},
        "channel_versions": {},
        "versions_seen": {},
    }


def check_persists_and_reads() -> None:
    """Check that a checkpoint is persisted to books.db and read back unchanged."""
    config = _config("_check_thread")
    checkpointer.put(config, _checkpoint("cp-check-1", 42), {"source": "input", "step": 0}, {})

    got = checkpointer.get(config)
    assert got is not None, "el checkpoint debería haberse persistido en books.db"
    assert got["channel_values"]["x"] == 42, "el valor persistido no coincide"

    checkpointer.delete_thread("_check_thread")


def check_conversations_are_isolated() -> None:
    """Check that conversations are isolated by thread_id and listed correctly."""
    checkpointer.put(
        _config("_check_A"), _checkpoint("cp-a", 1), {"source": "input", "step": 0}, {}
    )
    checkpointer.put(
        _config("_check_B"), _checkpoint("cp-b", 2), {"source": "input", "step": 0}, {}
    )

    assert checkpointer.get(_config("_check_A"))["channel_values"]["x"] == 1, "A se contaminó con B"
    assert checkpointer.get(_config("_check_B"))["channel_values"]["x"] == 2, "B se contaminó con A"

    threads = {c["thread_id"] for c in list_conversations()}
    assert {"_check_A", "_check_B"} <= threads, "list_conversations no lista ambas conversaciones"

    checkpointer.delete_thread("_check_A")
    checkpointer.delete_thread("_check_B")


if __name__ == "__main__":
    check_persists_and_reads()
    check_conversations_are_isolated()
