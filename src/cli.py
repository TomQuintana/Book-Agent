"""ASTA CLI - terminal interface for the multi-agent book assistant."""

import os
import uuid

import httpx
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.theme import Theme

from src.config.logging_config import setup_logging
from src.database.connection import init_db
from src.graph.graph_service import GraphService

ASTA_THEME = Theme(
    {
        "info": "dim white",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "cat": "bold white",
        "prompt": "bold white",
        "border": "dim white",
        "title": "bold white",
        "response": "white",
        "dim": "dim white",
    }
)

console = Console(theme=ASTA_THEME)

API_BASE_URL = os.getenv("ASTA_API_URL", "http://localhost:8000")

CAT_LOGO = r"""
  /\_/\
 ( o.o )
  > ^ <
"""

COMMANDS = {
    "/help": "Muestra los comandos disponibles",
    "/new": "Inicia una nueva conversación (nuevo thread)",
    "/conversations": "Lista conversaciones y salta a una previa",
    "/clear": "Limpia la pantalla",
    "/exit": "Salir de ASTA CLI",
}


def print_header():
    """Displays the header with the cat logo."""
    cat_text = Text(CAT_LOGO, style="cat")
    title = Text("ASTA CLI", style="title")
    subtitle = Text("v0.1.0 · Book Management Agent", style="dim")

    content = Text()
    content.append_text(cat_text)
    content.append_text(title)
    content.append("\n")
    content.append_text(subtitle)

    console.print(
        Panel(
            content,
            border_style="border",
            padding=(0, 2),
        )
    )
    console.print()


def print_help():
    """Displays the available commands."""
    lines = Text()
    for cmd, desc in COMMANDS.items():
        lines.append(f"  {cmd:<12}", style="bold white")
        lines.append(f"{desc}\n", style="dim")

    console.print(Panel(lines, title="Comandos", border_style="border", padding=(0, 1)))


def print_response(result: dict):
    """Displays the agent response."""
    if result["success"]:
        intent_label = result.get("intent") or "unknown"
        response_text = result.get("response", "Sin respuesta")

        console.print()
        console.print(
            Panel(
                response_text,
                title=f"[dim]intent: {intent_label}[/dim]",
                border_style="border",
                padding=(1, 2),
            )
        )
    else:
        console.print()
        console.print(
            Panel(
                result.get("error", "Error desconocido"),
                title="Error",
                border_style="error",
                padding=(1, 2),
            )
        )
    console.print()


def get_prompt_text():
    """Returns the styled prompt with ANSI codes."""
    return ANSI("\033[1;37m🐱 asta\033[0m \033[2;37m>\033[0m ")


def switch_conversation(session: PromptSession) -> str | None:
    """Lista conversaciones vía la API y deja elegir una para saltar a ella.

    Devuelve el thread_id elegido, o None si se cancela / hay error.
    """
    try:
        resp = httpx.get(f"{API_BASE_URL}/conversations", timeout=5)
        resp.raise_for_status()
        conversations = resp.json().get("conversations", [])
    except httpx.HTTPError:
        console.print(
            f"\n  No se pudo contactar la API en {API_BASE_URL}. ¿Está levantado el server?\n",
            style="error",
        )
        return None

    if not conversations:
        console.print("\n  No hay conversaciones previas.\n", style="dim")
        return None

    lines = Text()
    for i, conv in enumerate(conversations, start=1):
        thread_id = conv["thread_id"]
        turns = conv.get("checkpoints", 0)
        lines.append(f"  {i:>2}. ", style="bold white")
        lines.append(f"{thread_id[:8]}", style="response")
        lines.append(f"  ({turns} turnos)\n", style="dim")
    console.print(Panel(lines, title="Conversaciones", border_style="border", padding=(0, 1)))

    choice = session.prompt("  Elegí un número (Enter para cancelar): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(conversations)):
        console.print("  Cancelado.\n", style="dim")
        return None

    thread_id = conversations[int(choice) - 1]["thread_id"]

    try:
        resp = httpx.get(f"{API_BASE_URL}/conversations/{thread_id}", timeout=5)
        resp.raise_for_status()
        messages = resp.json().get("messages", [])
    except httpx.HTTPError:
        console.print("\n  No se pudo cargar el historial.\n", style="error")
        return None

    history = Text()
    for m in messages:
        history.append(f"{m['role']}: ", style="bold white")
        history.append(f"{m['content']}\n", style="response")
    console.print(
        Panel(
            history if messages else Text("(sin mensajes)", style="dim"),
            title=f"[dim]historial: {thread_id[:8]}[/dim]",
            border_style="border",
            padding=(1, 2),
        )
    )
    console.print()
    return thread_id


def main():
    """Main CLI loop."""
    setup_logging()
    init_db()
    graph_service = GraphService()

    console.clear()
    print_header()
    console.print("  Escribí tu consulta o [bold]/help[/bold] para ver comandos.\n", style="dim")

    session = PromptSession(
        history=FileHistory(".asta_history"),
    )

    # Una conversación por sesión de CLI; /new arranca otra.
    thread_id = str(uuid.uuid4())

    while True:
        try:
            user_input = session.prompt(get_prompt_text()).strip()

            if not user_input:
                continue

            if user_input.lower() == "/exit":
                console.print("\n  Hasta luego 🐱\n", style="dim")
                break

            if user_input.lower() == "/clear":
                console.clear()
                print_header()
                continue

            if user_input.lower() == "/help":
                print_help()
                continue

            if user_input.lower() == "/new":
                thread_id = str(uuid.uuid4())
                console.print("\n  Nueva conversación iniciada 🐱\n", style="success")
                continue

            if user_input.lower() == "/conversations":
                picked = switch_conversation(session)
                if picked:
                    thread_id = picked
                    console.print(f"  Continuando conversación {picked[:8]} 🐱\n", style="success")
                continue

            if user_input.startswith("/"):
                console.print(f"  Comando no reconocido: {user_input}", style="warning")
                console.print(
                    "  Escribí [bold]/help[/bold] para ver los comandos disponibles.\n", style="dim"
                )
                continue

            # Procesar con el agente
            with Live(
                Spinner("dots", text="Procesando...", style="dim"),
                console=console,
                transient=True,
            ):
                result = graph_service.process_query(user_input, thread_id=thread_id)

            print_response(result)

        except KeyboardInterrupt:
            console.print("\n  Usa [bold]/exit[/bold] para salir.\n", style="dim")
            continue
        except EOFError:
            console.print("\n  Hasta luego 🐱\n", style="dim")
            break


if __name__ == "__main__":
    main()
