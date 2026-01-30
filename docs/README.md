# Comby Skill Documentation

Bienvenido a la documentación de Comby Skill. Usa este índice para navegar según tu necesidad.

---

## 🚀 Primeros Pasos

¿Qué es Comby Skill y cómo te ayuda? Empieza aquí.

- **[Overview](./01-GETTING-STARTED/OVERVIEW.md)** - ¿Qué es Comby Skill y sus 13 familias de patrones?
- **[Workflow Comparison](./01-GETTING-STARTED/WORKFLOW_COMPARISON.md)** - Cómo Comby transforma tu flujo de trabajo (antes con grep/rg, después automático)

---

## 🏗️ Arquitectura y Diseño

Entendimiento profundo de cómo funciona internamente y decisiones técnicas.

- **[Pattern Families](./02-ARCHITECTURE/PATTERN_FAMILIES.md)** - Las 13 familias de patrones que Comby detecta (Phase 1-3)
- **[Memory Layer](./02-ARCHITECTURE/MEMORY_LAYER.md)** - Capa de memoria persistente con SQLite + embeddings vectoriales + grafo de relaciones
- **[Graph Integration](./02-ARCHITECTURE/GRAPH_INTEGRATION.md)** - Análisis de sqlite-graph y su integración como capa de relaciones (Alpha)

---

## 💻 Implementación

Guías prácticas y ejemplos de código funcionando.

- **[Memory Layer Examples](./03-IMPLEMENTATION/MEMORY_EXAMPLES.md)** - 8 casos de uso concretos con ejemplos SQL, API Python, y workflows

---

## 📖 Referencia Rápida

Consulta rápida de capacidades, APIs y performance.

- **[Memory Layer Summary](./04-REFERENCE/MEMORY_SUMMARY.md)** - Quick reference con APIs, CLI commands, performance metrics, y casos de uso

---

## 📊 Roadmap del Proyecto

### Phase 1: MVP Extended (Semanas 1-3)
- PatternMatcher con SQL_INJECTION y MISSING_TYPE_HINTS
- MemoryManager: almacenamiento, embeddings, grafo de relaciones
- sqlite-graph integration
- CLI commands para memory layer
- Tests exhaustivos con Ivoire BDD

### Phase 2: Extended Patterns (Semanas 4-6)
- LOGGING_POINTS, INPUT_VALIDATION, ERROR_HANDLING, PERFORMANCE_HOTSPOTS
- Algoritmos avanzados aprovechando sqlite-graph
- Dashboard básico

### Phase 3: Advanced (Mes 2+)
- TYPE_SAFETY, STATE_MUTATIONS, SECRETS_AND_CONFIG
- Reportes visuales y exportación
- Integración con Claude API para análisis semántico avanzado

---

## 🤔 ¿Qué Necesito?

Encuentra el documento adecuado según tu necesidad:

| Necesidad | Documento |
|---|---|
| **Entender rápido qué es Comby** | [Overview](./01-GETTING-STARTED/OVERVIEW.md) |
| **Ver cómo mejora mi flujo de trabajo** | [Workflow Comparison](./01-GETTING-STARTED/WORKFLOW_COMPARISON.md) |
| **Aprender las 13 familias de patrones** | [Pattern Families](./02-ARCHITECTURE/PATTERN_FAMILIES.md) |
| **Entender la arquitectura completa** | [Memory Layer](./02-ARCHITECTURE/MEMORY_LAYER.md) |
| **Evaluar sqlite-graph** | [Graph Integration](./02-ARCHITECTURE/GRAPH_INTEGRATION.md) |
| **Ver ejemplos de código** | [Implementation Examples](./03-IMPLEMENTATION/MEMORY_EXAMPLES.md) |
| **Referencia rápida de APIs** | [Summary](./04-REFERENCE/MEMORY_SUMMARY.md) |

---

## 📝 Convenciones

- **Lenguaje**: Español (técnico pero accesible)
- **Ejemplos**: Python, JavaScript, TypeScript
- **Enfoque**: Practicidad (casos reales, no teoría pura)
- **Formato**: Markdown con estructura jerárquica

---

## 🔗 Enlaces Útiles

- **GitHub Repository**: https://github.com/argami/comby-skill
- **CI/CD Status**: Check `.github/workflows/` for latest build status
- **Issues & Discussions**: GitHub Issues for bugs and feature requests

---

## 📞 Navegación Rápida

```
docs/
├─ README.md (estás aquí)
│
├─ 01-GETTING-STARTED/
│  ├─ OVERVIEW.md
│  └─ WORKFLOW_COMPARISON.md
│
├─ 02-ARCHITECTURE/
│  ├─ PATTERN_FAMILIES.md
│  ├─ MEMORY_LAYER.md
│  └─ GRAPH_INTEGRATION.md
│
├─ 03-IMPLEMENTATION/
│  └─ MEMORY_EXAMPLES.md
│
└─ 04-REFERENCE/
   └─ MEMORY_SUMMARY.md
```

---

**Última actualización**: 2026-01-30
**Status**: Design phase complete, awaiting implementation approval
