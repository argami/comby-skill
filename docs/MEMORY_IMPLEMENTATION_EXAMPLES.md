# Memory Layer - Ejemplos Concretos de Implementación

## 1. Ejemplos de API Usage

### Ejemplo 1: Análisis Inicial de Repositorio

```python
from comby_skill.memory import MemoryManager
from comby_skill.pattern_matcher import PatternMatcher
from pathlib import Path

# Inicializar gestor de memoria
repo_path = Path("/Users/argami/my-project")
memory = MemoryManager(repo_path)

# Inicializar pattern matcher con memory
matcher = PatternMatcher(memory)

# Analizar un archivo
with open(repo_path / "src" / "auth.py") as f:
    code = f.read()

patterns = matcher.detect_sql_injection(code)
patterns.extend(matcher.detect_missing_type_hints(code))

# Guardar en memoria
memory.save_analysis_results("src/auth.py", patterns)

# Ver estadísticas
stats = memory.get_stats()
print(f"Found {stats['total_patterns']} patterns")
print(f"Critical: {stats['by_severity']['CRITICAL']}")
```

### Ejemplo 2: Encontrar Patrones Similares

```python
# Usuario ejecuta: comby-skill memory similar --pattern-id 5

# Recuperar el patrón original
pattern = memory.get_pattern(5)
print(f"Original pattern: {pattern['code']}")
print(f"  File: {pattern['file_path']}, Line: {pattern['line_number']}")

# Buscar similares
similar = memory.find_similar_patterns(
    pattern_id=5,
    threshold=0.75,  # 75% de similitud
    limit=10
)

print(f"\nFound {len(similar)} similar patterns:")
for p in similar:
    print(f"  - {p['file_path']}:{p['line_number']} (similarity: {p['similarity']:.2%})")
    print(f"    {p['code']}")

# Usar caso: refactoring
# Si hay 8 patrones muy similares, probablemente podemos extraer una función
```

### Ejemplo 3: Entender Relaciones entre Patrones

```python
# Usuario ejecuta: comby-skill memory context --pattern-id 15

context = memory.get_pattern_context(pattern_id=15, depth=2)

print("=== PATTERN CONTEXT ===")
print(f"Pattern: {context['pattern']['pattern_type']}")
print(f"  File: {context['pattern']['file_path']}:{context['pattern']['line_number']}")
print(f"  Code: {context['pattern']['code']}")

print(f"\n=== RELATED PATTERNS ({len(context['related'])}) ===")
for rel in context['related']:
    print(f"  - {rel['relation_type']}: Pattern {rel['pattern']['id']}")
    print(f"    {rel['pattern']['file_path']}:{rel['pattern']['line_number']}")
    print(f"    {rel['pattern']['code']}")
    print(f"    Confidence: {rel['confidence']:.0%}")

print(f"\n=== PATTERNS THAT DEPEND ON THIS ({len(context['dependents'])}) ===")
for dep in context['dependents']:
    print(f"  - Pattern {dep['id']}: {dep['pattern_type']}")

# Usar caso: entender riesgos
# Veo que SQL_INJECTION (pattern 15) no tiene INPUT_VALIDATION relacionado
# → esto es un riesgo adicional
```

### Ejemplo 4: Analizar Dependencias del Repositorio

```python
# Usuario ejecuta: comby-skill memory analyze

analysis = memory.analyze_dependencies()

print("=== DEPENDENCY ANALYSIS ===")

print(f"\nCritical Path (debe arreglarse en orden):")
for i, pattern_id in enumerate(analysis['critical_path'], 1):
    pattern = memory.get_pattern(pattern_id)
    print(f"  {i}. Pattern {pattern_id}: {pattern['pattern_type']}")
    print(f"     {pattern['file_path']}:{pattern['line_number']}")

print(f"\nClusters encontrados: {len(analysis['clusters'])}")
for cluster_num, cluster in enumerate(analysis['clusters'], 1):
    print(f"  Cluster {cluster_num}: {len(cluster)} patrones")
    severity_count = {}
    for p_id in cluster:
        p = memory.get_pattern(p_id)
        severity_count[p['severity']] = severity_count.get(p['severity'], 0) + 1
    print(f"    Severities: {severity_count}")

print(f"\nCycles encontrados: {len(analysis['cycles'])}")
for cycle in analysis['cycles']:
    print(f"  Cycle: {' → '.join(map(str, cycle))}")

print(f"\nOrphaned patterns (sin relaciones): {len(analysis['orphaned'])}")
for pattern_id in analysis['orphaned'][:5]:
    pattern = memory.get_pattern(pattern_id)
    print(f"  - Pattern {pattern_id}: {pattern['pattern_type']}")

# Usar caso: priorizar refactoring
# Veo que existen 3 clusters independientes
# Puedo trabajar en ellos en paralelo con diferentes devs
```

### Ejemplo 5: Evolución de un Archivo

```python
# Usuario ejecuta: comby-skill memory history --file src/database.py

evolution = memory.get_evolution("src/database.py")

print("=== FILE EVOLUTION: src/database.py ===\n")

for snapshot in evolution:
    print(f"Analysis at {snapshot['analyzed_at']}")
    print(f"  Total patterns: {snapshot['total_patterns']}")
    print(f"  Critical: {snapshot['critical_count']}")
    print(f"  Medium: {snapshot['medium_count']}")

    if snapshot.get('patterns'):
        for pattern in snapshot['patterns']:
            status = "NEW" if pattern.get('is_new') else "PERSISTENT"
            print(f"    [{status}] {pattern['pattern_type']} @ line {pattern['line_number']}")

    print()

# Visualización de tendencia
import json
timestamps = [s['analyzed_at'] for s in evolution]
critical_counts = [s['critical_count'] for s in evolution]

print("Critical issues trend:")
for ts, count in zip(timestamps, critical_counts):
    bar = "█" * count
    print(f"  {ts}: {bar} ({count})")

# Usar caso: tracking de mejoras
# Veo que hace 3 análisis pasados había 8 CRITICAL
# Ahora quedan 2
# → buen progreso!
```

### Ejemplo 6: Comparar Dos Snapshots

```python
# Usuario ejecuta: comby-skill memory compare --snapshot-1 5 --snapshot-2 8

comparison = memory.compare_snapshots(5, 8)

print("=== COMPARING SNAPSHOTS ===")
print(f"From: Snapshot 5 ({comparison['snapshot1_date']})")
print(f"To:   Snapshot 8 ({comparison['snapshot2_date']})")

print(f"\nNew patterns: {len(comparison['new_patterns'])}")
for p in comparison['new_patterns']:
    print(f"  + {p['pattern_type']} in {p['file_path']}:{p['line_number']}")

print(f"\nFixed patterns: {len(comparison['fixed_patterns'])}")
for p in comparison['fixed_patterns']:
    print(f"  - {p['pattern_type']} in {p['file_path']}:{p['line_number']}")

print(f"\nChanged severity:")
for p in comparison['changed_severity']:
    print(f"  {p['pattern_type']}: {p['old_severity']} → {p['new_severity']}")

# Usar caso: validar cambios en PR
# Dev hizo commit
# Comparo snapshot before y after
# ¿Cuántos nuevos problemas introdujo? ¿Cuántos arregló?
```

### Ejemplo 7: Anotar Patrones

```python
# Usuario ejecuta múltiples comandos

# Marcar como falso positivo
memory.annotate_pattern(
    pattern_id=42,
    tag="false_positive",
    note="This is using parameterized queries, not vulnerable"
)

# Marcar como urgente
memory.annotate_pattern(
    pattern_id=15,
    tag="urgent",
    note="Production issue, user_id leaked in logs"
)

# Marcar como candidato de refactor
memory.annotate_pattern(
    pattern_id=8,
    tag="refactor_candidate",
    note="Can extract validation function with patterns 10 and 12"
)

# Recuperar anotaciones
annotations = memory.get_annotations(pattern_id=42)
for ann in annotations:
    print(f"[{ann['tag']}] {ann['note']} (created: {ann['created_at']})")

# Usar caso: colaboración
# Anotaciones quedan en memoria (persistentes)
# Otro dev ve las notas sobre patrones
# Entendimiento compartido
```

### Ejemplo 8: Búsqueda Semántica

```python
# Usuario ejecuta: comby-skill memory search "user input in SQL"

results = memory.semantic_search(
    query="user input in SQL query without validation",
    pattern_type=None,  # No filtrar por tipo
    limit=5
)

print("=== SEMANTIC SEARCH RESULTS ===")
print(f"Query: 'user input in SQL query without validation'\n")

for i, result in enumerate(results, 1):
    print(f"{i}. {result['file_path']}:{result['line_number']}")
    print(f"   Pattern: {result['pattern_type']} ({result['severity']})")
    print(f"   Relevance: {result['relevance_score']:.0%}")
    print(f"   {result['code'][:70]}...")
    print()

# Usar caso: exploración
# Dev está investigando "¿qué patrones hay relacionados con user input?"
# Sin saber exactamente qué buscar
# La búsqueda semántica lo ayuda a explorar
```

---

## 2. Ejemplos de Schema SQL

### Inserción de Patrones

```sql
-- Cuando se ejecuta: comby-skill analyze src/auth.py

INSERT INTO patterns (
    repo_hash,
    file_path,
    pattern_type,
    line_number,
    code_snippet,
    severity,
    embedding
) VALUES
    (
        'abc123def456',
        'src/auth.py',
        'SQL_INJECTION',
        42,
        'query = "SELECT * FROM users WHERE id = ' + user_id + '\"',
        'CRITICAL',
        X'f1f2f3...'  -- 768-dim float32 array encoded as BLOB
    ),
    (
        'abc123def456',
        'src/auth.py',
        'MISSING_TYPE_HINTS',
        10,
        'def authenticate(username):',
        'MEDIUM',
        X'a1a2a3...'
    );

-- Crear snapshot del archivo
INSERT INTO file_snapshots (file_path, file_hash, total_patterns, critical_count, medium_count)
VALUES ('src/auth.py', 'hash_of_file_content', 2, 1, 1);

-- Registrar análisis completo
INSERT INTO analysis_history (repo_state_hash, total_files_analyzed, total_patterns_found, critical_patterns)
VALUES ('repo_hash_123', 45, 128, 15);
```

### Búsqueda de Similares (Vectorial)

```sql
-- Encontrar patrones similares a pattern_id=5 (SQL_INJECTION)

SELECT
    p.id,
    p.file_path,
    p.line_number,
    p.code_snippet,
    p.severity,
    vec_distance_cosine(p.embedding, (SELECT embedding FROM patterns WHERE id = 5)) as distance,
    1 - vec_distance_cosine(p.embedding, (SELECT embedding FROM patterns WHERE id = 5)) as similarity
FROM patterns p
WHERE
    p.pattern_type = 'SQL_INJECTION'
    AND p.id != 5
ORDER BY similarity DESC
LIMIT 10;

-- Resultado:
-- | id  | file_path      | line_number | similarity | code_snippet              |
-- |-----|----------------|-------------|------------|---------------------------|
-- | 12  | src/user.py    | 85          | 0.89       | query = "SELECT..." + val  |
-- | 18  | src/admin.py   | 42          | 0.85       | "UPDATE users..." + role   |
-- | 23  | src/api.py     | 156         | 0.79       | "DELETE FROM..." + id      |
-- ...
```

### Traversal de Grafo

```sql
-- Obtener un patrón con su contexto de relaciones (depth=1)

WITH RECURSIVE pattern_graph AS (
    -- Base: el patrón inicial
    SELECT
        p.id, p.pattern_type, p.file_path, p.line_number,
        pr.relation_type, pr.confidence, 0 as depth
    FROM patterns p
    WHERE p.id = 15

    UNION ALL

    -- Recursivo: todas las relaciones conectadas
    SELECT
        pr_next.target_pattern_id,
        p_next.pattern_type, p_next.file_path, p_next.line_number,
        pr_next.relation_type, pr_next.confidence,
        pg.depth + 1
    FROM pattern_graph pg
    JOIN pattern_relations pr_next ON pg.id = pr_next.source_pattern_id
    JOIN patterns p_next ON pr_next.target_pattern_id = p_next.id
    WHERE pg.depth < 2  -- Limitar profundidad
)
SELECT * FROM pattern_graph
ORDER BY depth, relation_type;
```

### Análisis de Clusters

```sql
-- Encontrar componentes conexas (clusters) en el grafo

WITH RECURSIVE clusters AS (
    -- Seleccionar patrón inicial para cada cluster
    SELECT
        id, id as cluster_id
    FROM patterns
    WHERE id NOT IN (
        SELECT DISTINCT source_pattern_id FROM pattern_relations
        UNION
        SELECT DISTINCT target_pattern_id FROM pattern_relations
    )

    UNION ALL

    -- Expandir cluster siguiendo relaciones
    SELECT
        pr.target_pattern_id,
        c.cluster_id
    FROM pattern_relations pr
    JOIN clusters c ON pr.source_pattern_id = c.id
    WHERE pr.target_pattern_id NOT IN (
        SELECT id FROM clusters WHERE cluster_id = c.cluster_id
    )
)
SELECT
    cluster_id,
    COUNT(*) as size,
    GROUP_CONCAT(id) as pattern_ids,
    (SELECT COUNT(DISTINCT relation_type) FROM pattern_relations
     WHERE source_pattern_id IN (SELECT id FROM clusters WHERE cluster_id = c.cluster_id)
    ) as relation_types
FROM clusters c
GROUP BY cluster_id
ORDER BY size DESC;

-- Resultado:
-- | cluster_id | size | pattern_ids    | relation_types |
-- |------------|------|----------------|----------------|
-- | 5          | 8    | 5,10,12,15,... | 3              |
-- | 8          | 3    | 8,9,11         | 2              |
-- | 42         | 1    | 42             | 0              |
```

---

## 3. Integración Paso a Paso

### Step 1: Modificar `pattern_matcher.py`

```python
from comby_skill.memory import MemoryManager
from typing import Optional

class PatternMatcher:
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory = memory_manager

    def detect_sql_injection(self, code: str) -> List[Dict[str, Any]]:
        matches = []
        # ... detección existente ...

        # NUEVO: Generar embeddings si memory está disponible
        if self.memory:
            for match in matches:
                match['embedding'] = self.memory.embed_code_snippet(
                    match['code'],
                    'SQL_INJECTION'
                )

        return matches
```

### Step 2: Modificar CLI `analyze` command

```python
# En cli.py

def analyze(filepath: str, save_to_memory: bool = True) -> int:
    """Analyze file and optionally save results to memory."""
    file_path = Path(filepath)

    if not file_path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    code = file_path.read_text()

    # NUEVO: Inicializar memory si está disponible
    memory = None
    if save_to_memory:
        from comby_skill.memory import MemoryManager
        repo_root = find_repo_root(file_path)
        if repo_root:
            memory = MemoryManager(repo_root)

    # Detectar patrones con memory integrado
    matcher = PatternMatcher(memory)
    sql_matches = matcher.detect_sql_injection(code)
    type_hints_matches = matcher.detect_missing_type_hints(code)

    all_matches = sql_matches + type_hints_matches

    # NUEVO: Guardar en memory
    if memory and all_matches:
        relative_path = file_path.relative_to(repo_root)
        memory.save_analysis_results(str(relative_path), all_matches)

    # Output existente...
    if not all_matches:
        print(f"No vulnerabilities detected in {filepath}")
        return 0

    print(f"Found {len(all_matches)} issue(s) in {filepath}:\n")
    # ... mostrar resultados ...

    return 0
```

### Step 3: Agregar comandos de Memory al CLI

```python
# En cli.py - extender el parser

def main(args: List[str] = None) -> int:
    parser = argparse.ArgumentParser(prog='comby-skill')
    subparsers = parser.add_subparsers(dest='command')

    # Comando analyze existente
    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.add_argument('filepath')

    # NUEVO: Comando memory
    memory_parser = subparsers.add_parser('memory')
    memory_subparsers = memory_parser.add_subparsers(dest='memory_command')

    # memory patterns
    patterns_cmd = memory_subparsers.add_parser('patterns')
    patterns_cmd.add_argument('--type', help='Filter by pattern type')
    patterns_cmd.add_argument('--severity', help='Filter by severity')

    # memory similar
    similar_cmd = memory_subparsers.add_parser('similar')
    similar_cmd.add_argument('--pattern-id', type=int, required=True)

    # memory context
    context_cmd = memory_subparsers.add_parser('context')
    context_cmd.add_argument('--pattern-id', type=int, required=True)

    # memory analyze
    analyze_cmd = memory_subparsers.add_parser('analyze')

    # memory history
    history_cmd = memory_subparsers.add_parser('history')
    history_cmd.add_argument('--file', required=True)

    # ... más comandos ...

    parsed_args = parser.parse_args(args)

    if parsed_args.command == 'memory':
        return handle_memory_command(parsed_args)
    # ... resto ...
```

---

## 4. Testing de la Memory Layer

### Unit Tests para MemoryManager

```python
# spec/memory_spec.py

from ivoire import describe
import tempfile
from pathlib import Path

with describe("MemoryManager") as it:
    with it("should initialize database on first use") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            memory = MemoryManager(repo)

            db_path = repo / ".comby" / "memory.db"
            test.assertTrue(db_path.exists())
            test.assertTrue(db_path.stat().st_size > 1000)  # No empty file

    with it("should save and retrieve patterns") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            memory = MemoryManager(repo)

            patterns = [
                {
                    'code': 'query = "SELECT * FROM users" + id',
                    'line_number': 42,
                    'pattern': 'SQL_INJECTION',
                    'severity': 'CRITICAL'
                }
            ]

            memory.save_analysis_results('src/auth.py', patterns)

            retrieved = memory.get_patterns(file_path='src/auth.py')
            test.assertEqual(len(retrieved), 1)
            test.assertEqual(retrieved[0]['pattern'], 'SQL_INJECTION')

    with it("should find similar patterns") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            memory = MemoryManager(repo)

            # Guardar dos patrones similares
            patterns1 = [
                {
                    'code': 'query = "SELECT * FROM users WHERE id = ' + user_id + '"',
                    'line_number': 10,
                    'pattern': 'SQL_INJECTION',
                    'severity': 'CRITICAL'
                }
            ]
            patterns2 = [
                {
                    'code': 'query = "UPDATE users SET name = ' + name + '" WHERE id = ' + id + '"',
                    'line_number': 20,
                    'pattern': 'SQL_INJECTION',
                    'severity': 'CRITICAL'
                }
            ]

            memory.save_analysis_results('src/file1.py', patterns1)
            memory.save_analysis_results('src/file2.py', patterns2)

            p1 = memory.get_pattern(1)
            similar = memory.find_similar_patterns(p1['id'], threshold=0.7)

            test.assertGreater(len(similar), 0)
            test.assertEqual(similar[0]['file_path'], 'src/file2.py')
```

---

## Conclusión

Esta propuesta proporciona ejemplos concretos de cómo la memoria layer sería usada:

1. **Usuarios finales**: CLI commands simples (`comby-skill memory similar`, `comby-skill memory context`)
2. **Desarrolladores**: API Python elegante para integración
3. **Analysts**: Histórico y evolución para tracking de mejoras
4. **Teams**: Anotaciones para colaboración

**Listo para pasar a implementación cuando se autorice.**
