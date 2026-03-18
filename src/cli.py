"""ASTA CLI - Terminal interface para el agente multiagente de libros"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.live import Live
from rich.spinner import Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import ANSI

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

CAT_LOGO = r"""
  /\_/\
 ( o.o )
  > ^ <
"""

COMMANDS = {
    "/help": "Muestra los comandos disponibles",
    "/clear": "Limpia la pantalla",
    "/exit": "Salir de ASTA CLI",
}


def print_header():
    """Muestra el header con el logo del gato"""
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
    """Muestra los comandos disponibles"""
    lines = Text()
    for cmd, desc in COMMANDS.items():
        lines.append(f"  {cmd:<12}", style="bold white")
        lines.append(f"{desc}\n", style="dim")

    console.print(
        Panel(lines, title="Comandos", border_style="border", padding=(0, 1))
    )


def print_response(result: dict):
    """Muestra la respuesta del agente"""
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
    """Retorna el prompt estilizado con ANSI codes"""
    return ANSI("\033[1;37m🐱 asta\033[0m \033[2;37m>\033[0m ")


def main():
    """Loop principal del CLI"""
    init_db()
    graph_service = GraphService()

    console.clear()
    print_header()
    console.print("  Escribí tu consulta o [bold]/help[/bold] para ver comandos.\n", style="dim")

    session = PromptSession(
        history=FileHistory(".asta_history"),
    )

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

            if user_input.startswith("/"):
                console.print(f"  Comando no reconocido: {user_input}", style="warning")
                console.print("  Escribí [bold]/help[/bold] para ver los comandos disponibles.\n", style="dim")
                continue

            # Procesar con el agente
            with Live(
                Spinner("dots", text="Procesando...", style="dim"),
                console=console,
                transient=True,
            ):
                result = graph_service.process_query(user_input)

            print_response(result)

        except KeyboardInterrupt:
            console.print("\n  Usa [bold]/exit[/bold] para salir.\n", style="dim")
            continue
        except EOFError:
            console.print("\n  Hasta luego 🐱\n", style="dim")
            break


if __name__ == "__main__":
    main()
