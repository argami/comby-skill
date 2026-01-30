# Comby Skill Memory Layer Design

> 💡 **¿Cómo Comby mejora tu flujo de trabajo?** Consulta [Workflow Comparison](../01-GETTING-STARTED/WORKFLOW_COMPARISON.md) para ver casos reales de uso (antes/después con grep/rg vs Comby + Memory)

## Objetivo
Crear una capa de memoria **ligera, embebida y persistente** para Comby Skill que permita:
1. **Almacenar resultados de análisis** de un repositorio único a través del tiempo
2. **Establecer relaciones semánticas** entre patrones detectados (grafo)
3. **Buscar por similitud** y contexto usando embeddings vectoriales
4. **Entender la evolución** del código en el repositorio

## Visión General

```
┌─────────────────────────────────────────────────────┐
│ Comby Skill Memory Layer                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ Vector Database (SQLite + Vector Extension)│   │
│  │ - Embeddings de patrones detectados        │   │
│  │ - Búsqueda por similitud                   │   │
│  │ - Indexado automático                      │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ Graph Relations (Tablas normalizadas)      │   │
│  │ - Relaciones entre patrones                │   │
│  │ - Dependencias entre archivos              │   │
│  │ - Histórico de evolución                   │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ SQLite Database (Single File)              │   │
│  │ - Persistencia embebida                    │   │
│  │ - Sin server, sin dependencias externas    │   │
│  │ - Ubicación: .comby/memory.db              │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Arquitectura de Almacenamiento

### 1. Ubicación de Datos
```
<project-root>/
├── .comby/
│   ├── memory.db                    # SQLite database (único archivo)
│   ├── config.json                  # Configuración de memoria
│   └── .gitignore                   # Excluir de Git (excepto config)
└── ...
```

**Consideraciones**:
- `.comby/memory.db` NO se comitea a Git (almacenamiento local)
- `.comby/config.json` OPCIONAL: puede cometerse para compartir configuración
- SQLite es un único archivo binario, sin dependencias externas

### 2. Schema del Database

#### **Tabla: `patterns` (Patrones detectados)**
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_hash TEXT NOT NULL,                    -- Hash del repo para invalidar caché
    file_path TEXT NOT NULL,                    -- Ruta relativa del archivo
    pattern_type TEXT NOT NULL,                 -- 'SQL_INJECTION', 'MISSING_TYPE_HINTS', etc
    line_number INTEGER NOT NULL,               -- Línea donde se detectó
    code_snippet TEXT NOT NULL,                 -- El código exacto
    severity TEXT NOT NULL,                     -- 'CRITICAL', 'MEDIUM', 'LOW'
    embedding BLOB,                             -- Vector embeddings (float32 array)
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(file_path, pattern_type, line_number)
);

-- Índices para búsqueda rápida
CREATE INDEX idx_patterns_file ON patterns(file_path);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_severity ON patterns(severity);
CREATE INDEX idx_patterns_timestamp ON patterns(detected_at DESC);
```

#### **Tabla: `pattern_relations` (Relaciones entre patrones - Grafo)**
```sql
CREATE TABLE pattern_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_pattern_id INTEGER NOT NULL,         -- Pattern A
    target_pattern_id INTEGER NOT NULL,         -- Pattern B
    relation_type TEXT NOT NULL,                -- 'depends_on', 'conflicts_with', 'same_file', 'related_function'
    confidence REAL,                            -- 0.0 a 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(source_pattern_id) REFERENCES patterns(id) ON DELETE CASCADE,
    FOREIGN KEY(target_pattern_id) REFERENCES patterns(id) ON DELETE CASCADE,
    UNIQUE(source_pattern_id, target_pattern_id, relation_type)
);

-- Índices para traversal de grafo
CREATE INDEX idx_relations_source ON pattern_relations(source_pattern_id);
CREATE INDEX idx_relations_target ON pattern_relations(target_pattern_id);
CREATE INDEX idx_relations_type ON pattern_relations(relation_type);
```

#### **Tabla: `file_snapshots` (Snapshots de archivos analizados)**
```sql
CREATE TABLE file_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,                    -- Hash del contenido (SHA256)
    total_patterns INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(file_path, file_hash)
);

CREATE INDEX idx_snapshots_file ON file_snapshots(file_path);
CREATE INDEX idx_snapshots_analyzed ON file_snapshots(analyzed_at DESC);
```

#### **Tabla: `analysis_history` (Histórico de análisis)**
```sql
CREATE TABLE analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_state_hash TEXT,                       -- Hash del estado del repo
    total_files_analyzed INTEGER,
    total_patterns_found INTEGER,
    critical_patterns INTEGER,
    analysis_duration_ms FLOAT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT                                  -- Anotaciones opcionalesanal
);

CREATE INDEX idx_history_analyzed ON analysis_history(analyzed_at DESC);
```

#### **Tabla: `annotations` (Anotaciones y notas del usuario)**
```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER,                         -- Relacionado a un patrón (opcional)
    file_path TEXT,
    tag TEXT,                                   -- 'false_positive', 'urgent', 'refactor_candidate', etc
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(pattern_id) REFERENCES patterns(id) ON DELETE SET NULL,
    INDEX idx_annotations_tag(tag)
);
```

---

## Capa de Vectores (Embeddings)

### 1. Estrategia de Embeddings

**Opción A: Lightweight (Recomendada para MVP)**
- Usar embeddings simples basados en código
- NO requiere modelos ML complejos
- Dos estrategias:
  - **Hash-based**: Transformar código en vector simple (determinístico, rápido)
  - **Sentence transformers ligero**: Si se requiere, usar modelo mínimo como `all-MiniLM-L6-v2`

**Opción B: Integración Claude AI (Futuro)**
- Usar embeddings de Claude a través de API
- Requiere key API disponible
- Mejor calidad semántica
- Fallback a estrategia lightweight si no hay API key

### 2. Implementación de Embeddings Simples

```python
class CodeEmbedding:
    """Genera embeddings determinísticos para código."""

    @staticmethod
    def embed_code_snippet(code: str, pattern_type: str) -> List[float]:
        """
        Crea un embedding simple de un snippet de código.

        Vector de 768 dimensiones compuesto por:
        - 200 dim: características léxicas (palabras clave, operadores)
        - 200 dim: características estructurales (indentación, complejidad)
        - 200 dim: características semánticas (patrón, contexto)
        - 168 dim: hash del contenido
        """

        # Feature 1: Análisis léxico
        lexical = extract_lexical_features(code)         # 200 dim

        # Feature 2: Análisis estructural
        structural = extract_structural_features(code)   # 200 dim

        # Feature 3: Características del patrón
        semantic = extract_semantic_features(code, pattern_type)  # 200 dim

        # Feature 4: Hash del código (para búsqueda exacta)
        content_hash = normalize_hash(code)              # 168 dim

        return np.concatenate([lexical, structural, semantic, content_hash])
```

**Ventajas**:
- ✅ Determinístico (mismo código siempre genera mismo vector)
- ✅ Sin dependencias ML pesadas
- ✅ Rápido: generación en <1ms por snippet
- ✅ Explicable: cada dimensión representa característica específica

### 3. Búsqueda por Similitud

```python
class VectorSearch:
    """Búsqueda semántica de patrones similares."""

    def find_similar_patterns(
        self,
        query_embedding: List[float],
        pattern_type: str = None,
        threshold: float = 0.75,
        limit: int = 10
    ) -> List[Dict]:
        """
        Encuentra patrones similares usando similitud del coseno.

        Args:
            query_embedding: Vector de búsqueda
            pattern_type: Filtrar por tipo de patrón (opcional)
            threshold: Umbral de similitud (0.0 a 1.0)
            limit: Número máximo de resultados

        Returns:
            Lista de patrones similares ordenados por similitud
        """
        # SQL: SELECT patterns + COSINE SIMILARITY
        # Implementación: usar sqlite3 con extensión vectorial
```

---

## Capa de Grafo (Relaciones)

### 1. Tipos de Relaciones

```python
class RelationType:
    """Tipos de relaciones entre patrones."""

    # Relaciones semánticas
    DEPENDS_ON = "depends_on"           # A depende de B
    CONFLICTS_WITH = "conflicts_with"   # A y B son contradictorios
    SAME_ROOT_CAUSE = "same_root_cause" # A y B vienen de mismo problema

    # Relaciones espaciales
    SAME_FILE = "same_file"             # Ambos en mismo archivo
    SAME_FUNCTION = "same_function"     # Ambos en misma función
    SAME_CLASS = "same_class"           # Ambos en misma clase

    # Relaciones temporales
    PRECEDES = "precedes"               # A aparece antes que B
    FIXES = "fixes"                     # A arregla el problema de B

    # Relaciones de contexto
    RELATED_TO = "related_to"           # Relacionado (general)
```

### 2. Construcción Automática de Relaciones

Al detectar patrones, el sistema automáticamente establece relaciones:

```python
class GraphBuilder:
    """Construye el grafo de relaciones automáticamente."""

    def build_relations_from_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """
        Analiza patrones y establece relaciones automáticas.

        Reglas:
        1. Si dos patrones están en el mismo archivo → same_file
        2. Si están en la misma función → same_function (parse AST)
        3. Si son del mismo tipo y similares → related_to (similitud vectorial)
        4. Si una es SQL_INJECTION y otra INPUT_VALIDATION en mismo flujo → depends_on
        5. Si hay AUTH_BOUNDARIES y API_ENDPOINT → same_file
        """
        pass
```

### 3. Queries de Grafo

```python
class GraphQueries:
    """Queries útiles sobre el grafo."""

    def get_pattern_context(self, pattern_id: int, depth: int = 2) -> Dict:
        """
        Retorna un patrón con su contexto completo (grafo de relaciones).

        Ejemplo:
        {
            "pattern": {...},
            "related": [
                {
                    "pattern": {...},
                    "relation": "depends_on",
                    "confidence": 0.92
                }
            ],
            "dependents": [...],
            "in_same_file": [...]
        }
        """
        pass

    def find_connected_components(self, pattern_type: str = None) -> List[List[int]]:
        """
        Encuentra clusters de patrones conectados (componentes conexas).
        Útil para entender problemas relacionados.
        """
        pass

    def get_critical_path(self) -> List[int]:
        """
        Retorna el camino crítico: secuencia de patrones que deben arreglarse
        en orden de dependencias.
        """
        pass
```

---

## Interfaz de la Capa de Memoria

### 1. Clase Principal: `MemoryManager`

```python
class MemoryManager:
    """
    Gestor central de la capa de memoria.

    Responsabilidades:
    - Inicializar/migrar database
    - Almacenar y recuperar patrones
    - Construir y consultar grafo
    - Manejar embeddings
    """

    def __init__(self, repo_path: str, db_path: str = None):
        """
        Args:
            repo_path: Ruta al repositorio
            db_path: Ruta a la base de datos (default: repo/.comby/memory.db)
        """
        self.repo_path = Path(repo_path)
        self.db_path = Path(db_path or repo_path / ".comby" / "memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    # === OPERACIONES BÁSICAS ===

    def save_analysis_results(
        self,
        file_path: str,
        patterns: List[Dict[str, Any]]
    ) -> None:
        """
        Guarda los resultados de análisis de un archivo.

        Args:
            file_path: Ruta relativa del archivo analizado
            patterns: Lista de patrones detectados
        """
        pass

    def get_patterns(
        self,
        file_path: str = None,
        pattern_type: str = None,
        severity: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Recupera patrones con filtros opcionales.
        """
        pass

    # === OPERACIONES DE VECTORES ===

    def find_similar_patterns(
        self,
        pattern_id: int,
        threshold: float = 0.75,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Encuentra patrones similares a uno dado.
        """
        pass

    def semantic_search(
        self,
        query: str,
        pattern_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica: busca patrones por descripción natural.

        Ejemplo:
        memory.semantic_search("SQL injection with user input")
        """
        pass

    # === OPERACIONES DE GRAFO ===

    def get_pattern_context(
        self,
        pattern_id: int,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Retorna un patrón con su contexto relacional completo.
        """
        pass

    def get_connected_patterns(self, pattern_id: int) -> List[Dict]:
        """
        Retorna todos los patrones conectados a uno dado.
        """
        pass

    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analiza el grafo completo de dependencias.

        Retorna:
        {
            "clusters": [...],
            "critical_paths": [...],
            "cycles": [...],
            "orphaned": [...]
        }
        """
        pass

    # ===OPERACIONES DE HISTÓRICO ===

    def get_evolution(self, file_path: str) -> List[Dict]:
        """
        Retorna la evolución de patrones en un archivo a través del tiempo.
        """
        pass

    def compare_snapshots(self, snapshot1_id: int, snapshot2_id: int) -> Dict:
        """
        Compara dos análisis (snapshots) del repositorio.

        Retorna:
        {
            "new_patterns": [...],
            "fixed_patterns": [...],
            "changed_severity": [...]
        }
        """
        pass

    # === ANOTACIONES ===

    def annotate_pattern(
        self,
        pattern_id: int,
        tag: str,
        note: str = None
    ) -> None:
        """
        Añade anotación a un patrón.

        Tags comunes:
        - 'false_positive': No es realmente un problema
        - 'urgent': Arreglar inmediatamente
        - 'refactor_candidate': Buen candidato para refactor
        - 'accepted_risk': Riesgo aceptado
        """
        pass

    def get_annotations(self, pattern_id: int = None) -> List[Dict]:
        """
        Recupera anotaciones, opcionalmente filtradas.
        """
        pass

    # === MANTENIMIENTO ===

    def clear(self) -> None:
        """Limpia toda la base de datos."""
        pass

    def export_json(self, output_path: str) -> None:
        """Exporta la memoria a JSON (para debugging/sharing)."""
        pass

    def import_json(self, input_path: str) -> None:
        """Importa memoria desde JSON."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de la memoria.

        {
            "total_patterns": 123,
            "by_severity": {"CRITICAL": 15, "MEDIUM": 60, "LOW": 48},
            "by_type": {"SQL_INJECTION": 10, ...},
            "files_analyzed": 45,
            "last_analysis": "2026-01-30T10:59:49Z"
        }
        """
        pass
```

### 2. Integración con CLI

```bash
# Comandos nuevos de la CLI

# Ver patrones guardados
$ comby-skill memory patterns --type SQL_INJECTION --severity CRITICAL

# Ver patrones similares a uno dado
$ comby-skill memory similar --pattern-id 42

# Búsqueda semántica
$ comby-skill memory search "user input in database query"

# Ver contexto de un patrón
$ comby-skill memory context --pattern-id 42

# Analizar dependencias
$ comby-skill memory analyze

# Ver evolución de un archivo
$ comby-skill memory history --file src/auth.py

# Comparar dos análisis
$ comby-skill memory compare --snapshot-1 1 --snapshot-2 2

# Anotar un patrón
$ comby-skill memory annotate --pattern-id 42 --tag "false_positive" --note "This is a parameterized query"

# Exportar/importar
$ comby-skill memory export --output memory.json
$ comby-skill memory import --input memory.json

# Estadísticas
$ comby-skill memory stats
```

---

## Consideraciones de Implementación

### 1. Tecnologías

**SQLite**
- ✅ Ligero, embebido, sin servidor
- ✅ ACID, transacciones, índices
- ✅ Soporte para extensiones
- ❌ No paralelización masiva (no aplica aquí)

**Extensión Vectorial: `sqlite-vec`**
- Extensión SQLite para operaciones vectoriales
- Soporte para búsqueda por similitud (coseno, euclidiana)
- Indexado HNSW automático
- URL: https://github.com/asg017/sqlite-vec

**Embeddings**
- Opción MVP: Hash-based + características simples (768 dim, ~3KB por patrón)
- Opción futura: Sentence transformers o Claude embeddings

### 2. Rendimiento

**Tamaño de Database**
- Por patrón: ~5KB (incluidos embeddings)
- Para 1000 patrones: ~5MB
- Para 10,000 patrones: ~50MB
- → Escalable a proyectos medianos sin problema

**Tiempo de Query**
- Búsqueda por tipo/severidad: <10ms
- Búsqueda vectorial (con índice): <50ms
- Traversal de grafo (depth 2): <100ms
- → Suficientemente rápido para interactividad

### 3. Integridad de Datos

**Invalidación de Caché**
```python
# Si el repo cambió, datos podrían estar obsoletos
repo_hash = compute_repo_hash()  # Hash de .git/HEAD + archivos principales
stored_hash = get_stored_repo_hash()

if repo_hash != stored_hash:
    # Opcional: invalidar todo
    # O: marcar patrones como "potentially_stale"
```

**Deduplicación**
```sql
-- Evitar duplicados exactos (mismo archivo, línea, tipo)
UNIQUE(file_path, pattern_type, line_number)
```

### 4. Migración de Datos

```python
class DatabaseMigration:
    """Manejo de versiones de schema."""

    # v1.0: Schema inicial
    # v1.1: Agregar tabla de anotaciones
    # v2.0: Agregar tabla de historia de análisis

    def migrate(self, from_version: str, to_version: str) -> None:
        """Ejecuta migraciones necesarias."""
        pass
```

---

## Casos de Uso

### 1. "Mostrame los problemas SQL injection similares"

```python
# Usuario: comby-skill memory similar --pattern-id 5

pattern = memory.get_pattern(5)  # SQL_INJECTION en línea 42
similar = memory.find_similar_patterns(5, threshold=0.7)

# Resultado: muestra 8 patrones SQL injection con código similar
# Útil para entender si es patrón repetido → refactor
```

### 2. "¿Qué patrones están relacionados?"

```python
# Usuario: comby-skill memory context --pattern-id 42

result = memory.get_pattern_context(42, depth=2)

# Resultado:
# {
#   "pattern": {id: 42, type: "SQL_INJECTION", ...},
#   "related": [
#     {pattern: {id: 10, type: "INPUT_VALIDATION"}, relation: "depends_on"},
#     {pattern: {id: 55, type: "SQL_INJECTION"}, relation: "same_file"}
#   ],
#   "dependents": [...]
# }
```

### 3. "Mostrame la evolución en este archivo"

```python
# Usuario: comby-skill memory history --file src/auth.py

history = memory.get_evolution("src/auth.py")

# Resultado: Timeline de patrones detectados en ese archivo
# - 2026-01-15: SQL_INJECTION detectado
# - 2026-01-20: Arreglado (removed from latest snapshot)
# - 2026-01-25: Nuevo MISSING_TYPE_HINTS detectado
```

### 4. "¿Cuáles son los problemas críticos que debo arreglar primero?"

```python
# Usuario: comby-skill memory analyze

analysis = memory.analyze_dependencies()

# Resultado:
# - Critical path: [pattern_5 → pattern_12 → pattern_8]
#   (arreglar en este orden)
# - Clusters: 3 clusters de problemas relacionados
# - Orphaned: 2 patrones aislados (bajo prioridad)
```

---

## Integración con PatternMatcher

### 1. Flujo de Datos

```
┌─────────────────────┐
│  analyze_file()     │
│  (CLI command)      │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────────┐
│ PatternMatcher.detect_*()       │
│ - SQL injection                 │
│ - Type hints                    │
│ - [Future patterns]             │
└──────────┬──────────────────────┘
           │
           ↓
┌─────────────────────────────────┐
│ MemoryManager.save_analysis()   │
│ - Guardar patrones              │
│ - Generar embeddings            │
│ - Construir relaciones          │
│ - Actualizar índices            │
└──────────┬──────────────────────┘
           │
           ↓
┌──────────────────────┐
│ Display results      │
└──────────────────────┘
```

### 2. Modificación Mínima de PatternMatcher

```python
class PatternMatcher:
    def __init__(self, memory_manager: MemoryManager = None):
        self.memory = memory_manager

    def detect_sql_injection(self, code: str) -> List[Dict[str, Any]]:
        matches = [...]  # Detección actual

        if self.memory:
            # Generar embeddings
            for match in matches:
                match['embedding'] = self.memory.embed_code(
                    match['code'],
                    'SQL_INJECTION'
                )

        return matches
```

---

## Configuración del Proyecto

### 1. `.comby/config.json` (Opcional)

```json
{
  "memory": {
    "enabled": true,
    "vector_embeddings": "lightweight",
    "auto_build_relations": true,
    "retention_days": null,
    "export_on_analysis": false
  },
  "patterns": {
    "track_evolution": true,
    "deduplicate": true
  }
}
```

### 2. `.gitignore` Updates

```
# Comby Skill memory (local only)
.comby/memory.db
.comby/memory.db-*
.comby/*.tmp
```

---

## Roadmap de Implementación

**Phase 1 (MVP)**: Core memory layer
- ✓ SQLite schema básico
- ✓ MemoryManager clase principal
- ✓ Guardar/recuperar patrones
- ✓ Embeddings determinísticos simples
- ✓ Búsqueda por similitud básica

**Phase 2**: Grafo y relaciones
- ✓ Tabla de relaciones
- ✓ GraphBuilder automático
- ✓ Queries de grafo básicas
- ✓ Análisis de dependencias

**Phase 3**: Anotaciones e histórico
- ✓ Tabla de anotaciones
- ✓ Snapshots y comparación
- ✓ Evolución temporal

**Phase 4 (Future)**: Integración avanzada
- ✓ Embeddings de Claude
- ✓ Búsqueda semántica mejorada
- ✓ Reportes visuales
- ✓ Sincronización multi-repo (descartado: enfoque single-repo)

---

## Conclusiones

Esta arquitectura proporciona:

1. **Persistencia ligera**: SQLite, un archivo, sin dependencias externas
2. **Semántica**: Embeddings + búsqueda por similitud
3. **Relaciones**: Grafo de dependencias entre patrones
4. **Escalabilidad**: Rendimiento mantenido hasta 10K+ patrones
5. **Simplicidad**: Integración mínima con código existente
6. **Extensibilidad**: Fácil agregar nuevas tablas/queries

El diseño **prioriza un único repositorio a la vez**, evitando complejidades de multi-repo. Cada repositorio obtiene su propia `.comby/memory.db` independiente.

**Listo para pasar a implementación cuando lo autorice el usuario.**
