# Arquitecturas de sistemas multi-agente con LangGraph

## Conceptos base

### Nodo
Un nodo es simplemente una función `(state) -> state` registrada en el grafo. Es el bloque
de construcción fundamental. No importa lo que haga adentro (llamar un LLM, ejecutar lógica
pura, invocar un subagente) — desde la perspectiva del grafo, todo es un nodo.

```python
graph.add_node("router", agent_router)   # la función ES el nodo
```

### Tipos de nodo

| Tipo | Descripción | Ejemplo en este proyecto |
|---|---|---|
| Nodo simple | Llama al LLM una vez, sin tools ni loop | `router.py`, `formatter.py` |
| Nodo-subagente | Envuelve un subagente con loop ReAct interno | `modify.py`, `search.py`, `recommend.py` |
| Nodo utilitario | Sin LLM, solo lógica Python | `unknown_node` en `agent_graph.py` |

### Subagente
Un subagente es un agente creado con `create_agent` que vive dentro de un nodo.
Tiene su propio loop interno: razona → elige tool → observa resultado → repite.

```
Nodo modify
└── modify_agent (subagente)
        ├── LLM: "necesito crear un libro"
        ├── → ejecuta create_book(...)
        ├── LLM evalúa el resultado
        └── devuelve respuesta final al nodo
```

### State vs Checkpointer
- **State**: datos en memoria que fluyen entre nodos durante una ejecución. Desaparece al terminar.
- **Checkpointer**: serializa y persiste el state a disco/DB. Permite reanudar entre sesiones usando `thread_id`.

---

## Patrón 1 — Agente único (proyectos simples)

Un solo agente con acceso a todas las tools. El LLM decide qué tool usar en cada caso.

```
src/
├── agent.py        # graph + nodos + tools en un archivo
├── state.py
└── tools.py
```

```
Usuario → [agente_unico] → END
               │
               ├── tool: create_book
               ├── tool: search_book
               └── tool: delete_book
```

**Pros**: simple de implementar, fácil de entender  
**Contras**: el LLM tiene que manejar todo el dominio solo, los prompts crecen, difícil de escalar  
**Cuándo usarlo**: prototipos, proyectos con pocos tools y un dominio acotado

---

## Patrón 2 — Supervisor con subagentes (este proyecto)

Un orquestador clasifica la intención y delega a subagentes especializados.
Cada subagente tiene acceso solo a las tools de su dominio.

```
src/
├── graph/
│   ├── agent_graph.py      # definición del grafo y aristas
│   ├── state.py            # schemas de estado compartidos
│   └── nodes/              # funciones nodo (wrappers y nodos simples)
│       ├── router.py
│       ├── formatter.py
│       ├── modify.py
│       ├── search.py
│       └── recommend.py
├── agents/                 # definiciones de subagentes (create_agent)
│   ├── modify_agent.py
│   ├── search_agent.py
│   └── recommend_agent.py
├── tools/
├── database/
├── api/
└── config/
```

```
Usuario
  │
  ▼
[router]             ← nodo simple: clasifica intención
  │
  ├── "search"   → [search_node]    ← nodo-subagente (tools: list_books, get_book)
  ├── "modify"   → [modify_node]    ← nodo-subagente (tools: create, update, delete)
  └── "recommend"→ [recommend_node] ← nodo-subagente (tools: get_read_books)
                        │
                        ▼
                   [formatter]      ← nodo simple: formatea la respuesta
                        │
                        ▼
                       END
```

**Pros**: separación clara de responsabilidades, prompts más cortos y específicos, fácil de agregar nuevos dominios  
**Contras**: más archivos, el router puede equivocarse en la clasificación  
**Cuándo usarlo**: proyectos con dominios claramente separados (buscar ≠ modificar ≠ recomendar)

---

## Patrón 3 — Pipeline lineal

El flujo siempre pasa por todos los nodos en orden. No hay routing condicional.
Cada nodo transforma el estado y lo pasa al siguiente.

```
src/
├── graph/
│   ├── graph.py
│   ├── state.py
│   └── nodes/
│       ├── extractor.py
│       ├── enricher.py
│       ├── validator.py
│       └── formatter.py
└── tools/
```

```
Usuario → [extractor] → [enricher] → [validator] → [formatter] → END
```

**Pros**: predecible, fácil de debuggear, sin lógica de routing  
**Contras**: inflexible, todos los mensajes pasan por todos los nodos aunque no sea necesario  
**Cuándo usarlo**: flujos ETL, procesamiento de documentos, pipelines de datos

---

## Patrón 4 — Multi-agente colaborativo (proyectos complejos)

Los agentes se pasan trabajo entre sí. No hay un supervisor central; cada agente
puede delegar a otro según lo que necesite.

```
src/
├── graph/
│   ├── graph.py
│   ├── state.py
│   └── nodes/
│       ├── researcher.py
│       ├── writer.py
│       └── reviewer.py
└── agents/
    ├── researcher_agent.py
    ├── writer_agent.py
    └── reviewer_agent.py
```

```
Usuario → [researcher] ←→ [writer] ←→ [reviewer] → END
               ↑_____________________________|
                     (iteraciones hasta aprobar)
```

**Pros**: muy potente para tareas que requieren múltiples perspectivas o iteraciones  
**Contras**: difícil de controlar, puede entrar en loops, costoso en tokens  
**Cuándo usarlo**: generación de contenido complejo, revisión de código, research automatizado

---

## Patrón 5 — Por dominio (enterprise)

Cuando el proyecto tiene múltiples dominios independientes que crecen a distinto ritmo.
Cada dominio es un subgrafo con sus propios agentes, tools y estado.

```
src/
├── books/
│   ├── agents/
│   ├── nodes/
│   ├── tools/
│   └── state.py
├── users/
│   ├── agents/
│   └── tools/
├── core/
│   ├── graph.py         # grafo principal que conecta dominios
│   └── base_state.py
└── config/
```

**Pros**: equipos independientes, dominios encapsulados, escala horizontalmente  
**Contras**: overhead de coordinación entre dominios, imports más complejos  
**Cuándo usarlo**: equipos grandes, múltiples dominios de negocio, necesidad de despliegue independiente

---

## Resumen de decisión

```
¿Cuántos dominios distintos tiene el problema?
│
├── Uno solo, pocas tools → Patrón 1 (agente único)
│
├── Varios dominios separados → Patrón 2 (supervisor) ← este proyecto
│
├── Flujo siempre igual → Patrón 3 (pipeline)
│
├── Requiere iteración/colaboración → Patrón 4 (colaborativo)
│
└── Múltiples dominios + equipos grandes → Patrón 5 (por dominio)
```
