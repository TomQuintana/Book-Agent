"""Helper functions for graph debugging."""


def snapshot(s) -> dict:
    """Returns a snapshot of the graph's state for debugging."""
    return {
        "checkpoint_id": s.config["configurable"].get("checkpoint_id"),
        "next": list(s.next),
        "step": s.metadata.get("step") if s.metadata else None,
        "values": {k: str(v)[:300] for k, v in s.values.items()},
        "pending": [{"node": t.name, "error": str(t.error) if t.error else None} for t in s.tasks],
    }
