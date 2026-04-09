from datetime import date

from langchain_core.tools import tool

from ..database.book_service import BookService

from ..database.models import BookCreate, BookUpdate

book_service = BookService()


@tool
def create_book(
    title: str,
    author: str = None,
    status: str = None,
    type: str = None,
    description: str = None,
    is_physically: bool = False,
    finished: str = None,
) -> str:
    """Crea un nuevo libro en la base de datos.

    Args:
        title: Título del libro (requerido)
        author: Autor del libro (opcional)
        status: Estado de lectura como 'reading', 'completed', 'pending' (opcional)
        type: Tipo de libro como 'fiction', 'non-fiction', 'technical', 'emprendimiento' (opcional)
        description: Descripción del libro (opcional)
        is_physically: Si el libro es físico (opcional, default False)
        finished: Fecha de finalización en formato YYYY-MM-DD (opcional)

    Returns:
        Mensaje de confirmación con los detalles del libro creado
    """
    try:
        book_data = BookCreate(
            title=title,
            author=author,
            status=status,
            type=type,
            description=description,
            is_physically=is_physically,
            finished=date.fromisoformat(finished) if finished else None,
        )
        book = book_service.create_book(book_data)
        return f"Libro '{book.title}' creado exitosamente con ID {book.id}"
    except Exception as e:
        return f"Error al crear el libro: {str(e)}"


@tool
def get_book(book_id: int) -> str:
    """Obtiene información detallada de un libro por su ID.

    Args:
        book_id: ID único del libro

    Returns:
        Información completa del libro o mensaje de error si no existe
    """
    try:
        book = book_service.get_book(book_id)
        if not book:
            return f"No se encontró ningún libro con ID {book_id}"

        return f"""Libro encontrado:
        - ID: {book.id}
        - Título: {book.title}
        - Autor: {book.author or "No especificado"}
        - Estado: {book.status or "No especificado"}
        - Tipo: {book.type or "No especificado"}
        - Descripción: {book.description or "Sin descripción"}
        - Es físico: {"Sí" if book.is_physically else "No"}
        - Fecha de finalización: {book.finished or "No finalizado"}
            """
    except Exception as e:
        return f"Error al obtener el libro: {str(e)}"


@tool
def update_book(
    book_id: int,
    title: str = None,
    author: str = None,
    status: str = None,
    description: str = None,
) -> str:
    """Actualiza la información de un libro existente.

    Args:
        book_id: ID del libro a actualizar (requerido)
        title: Nuevo título del libro (opcional)
        author: Nuevo autor del libro (opcional)
        status: Nuevo estado de lectura (opcional)
        description: Nueva descripción (opcional)

    Returns:
        Mensaje de confirmación con los datos actualizados
    """
    try:
        book_data = BookUpdate(
            title=title, author=author, status=status, description=description
        )
        book = book_service.update_book(book_id, book_data)
        if not book:
            return f"No se encontró ningún libro con ID {book_id}"

        return f"Libro '{book.title}' (ID: {book_id}) actualizado correctamente"
    except Exception as e:
        return f"Error al actualizar el libro: {str(e)}"


@tool
def delete_book(book_id: int) -> str:
    """Elimina un libro de la base de datos.

    Args:
        book_id: ID del libro a eliminar

    Returns:
        Mensaje de confirmación o error
    """
    try:
        deleted = book_service.delete_book(book_id)
        if deleted:
            return f"Libro con ID {book_id} eliminado exitosamente"
        else:
            return f"No se encontró ningún libro con ID {book_id}"
    except Exception as e:
        return f"Error al eliminar el libro: {str(e)}"


@tool
def list_books(status: str = None, author: str = None, title: str = None) -> str:
    """Lista y busca libros de la base de datos con filtros opcionales.

    Usa esta herramienta para:
    - Listar todos los libros (sin parámetros)
    - Buscar por título específico (ej: "1984", "Cien años de soledad")
    - Buscar por autor (ej: "García Márquez", "George Orwell")
    - Filtrar por estado de lectura (ej: "completed", "reading", "pending")
    - Combinar filtros (ej: autor + estado)

    Args:
        title: Buscar por título del libro (búsqueda parcial, case-insensitive) (opcional)
        author: Filtrar por autor (búsqueda parcial, case-insensitive) (opcional)
        status: Filtrar por estado de lectura como 'reading', 'completed', 'pending' (opcional)

    Returns:
        Lista formateada de libros encontrados con sus detalles

    Ejemplos:
        - list_books(title="1984") → Busca libros con "1984" en el título
        - list_books(author="Orwell") → Busca libros de autores que contengan "Orwell"
        - list_books(status="completed") → Lista libros completados
        - list_books() → Lista todos los libros
    """
    try:
        books = book_service.list_books(status=status, author=author)

        # Filtrar por título si se especifica
        if title and books:
            title_lower = title.lower()
            books = [
                book
                for book in books
                if book.title and title_lower in book.title.lower()
            ]

        if not books:
            filters = []
            if title:
                filters.append(f"title='{title}'")
            if status:
                filters.append(f"status='{status}'")
            if author:
                filters.append(f"author='{author}'")
            filter_str = " con filtros: " + ", ".join(filters) if filters else ""
            return f"No se encontraron libros{filter_str}"

        result = f"Encontrados {len(books)} libro(s):\n\n"
        for book in books:
            result += f"[ID: {book.id}] {book.title}\n"
            result += f"    Autor: {book.author or 'No especificado'}\n"
            result += f"    Estado: {book.status or 'No especificado'}\n"
            if book.description:
                desc = (
                    book.description[:100] + "..."
                    if len(book.description) > 100
                    else book.description
                )
                result += f"    Descripción: {desc}\n"
            result += "\n"

        return result
    except Exception as e:
        return f"Error al listar libros: {str(e)}"


@tool
def get_read_books() -> str:
    """Obtiene el historial de libros leídos o en progreso del usuario desde la base de datos.

    Usa esta herramienta para conocer qué libros ha leído el usuario antes de hacer recomendaciones.
    Retorna libros con estado 'completed' (terminados) y 'reading' (en progreso).

    Returns:
        Lista formateada de libros leídos con título, autor y tipo
    """
    try:
        completed = book_service.list_books(status="completed")
        reading = book_service.list_books(status="reading")
        all_read = completed + reading

        if not all_read:
            return "El usuario no tiene libros registrados como leídos o en progreso en su biblioteca."

        result = f"Historial de lectura del usuario ({len(all_read)} libro(s)):\n\n"

        if completed:
            result += "📚 Libros terminados:\n"
            for book in completed:
                result += f"  - {book.title}"
                if book.author:
                    result += f" (de {book.author})"
                if book.type:
                    result += f" [{book.type}]"
                result += "\n"

        if reading:
            result += "\n📖 Libros en progreso:\n"
            for book in reading:
                result += f"  - {book.title}"
                if book.author:
                    result += f" (de {book.author})"
                if book.type:
                    result += f" [{book.type}]"
                result += "\n"

        return result
    except Exception as e:
        return f"Error al obtener el historial de lectura: {str(e)}"


# Lista de todas las tools disponibles para exportar
book_tools = [create_book, get_book, update_book, delete_book, list_books, get_read_books]
