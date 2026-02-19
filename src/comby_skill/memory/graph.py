"""
Graph Relations Module

Manages code relationships and dependencies for call graph analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from collections import defaultdict, deque
import re


@dataclass
class Node:
    """Represents a code element (file, function, class)."""
    id: str
    name: str
    node_type: str  # file, function, class, module
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Represents a relationship between code elements."""
    source: str
    target: str
    edge_type: str  # imports, calls, inherits, contains, uses
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodeGraph:
    """Graph of code relationships."""

    def __init__(self):
        """Initialize code graph."""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)

    def add_node(self, node: Node):
        """Add node to graph.

        Args:
            node: Node to add
        """
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        """Add edge to graph.

        Args:
            edge: Edge to add
        """
        self.edges.append(edge)
        self.adjacency[edge.source].add(edge.target)
        self.reverse_adjacency[edge.target].add(edge.source)

    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get direct dependencies of a node.

        Args:
            node_id: Node ID

        Returns:
            Set of dependency node IDs
        """
        return self.adjacency.get(node_id, set())

    def get_dependents(self, node_id: str) -> Set[str]:
        """Get direct dependents of a node.

        Args:
            node_id: Node ID

        Returns:
            Set of dependent node IDs
        """
        return self.reverse_adjacency.get(node_id, set())

    def find_all_dependencies(self, node_id: str) -> Set[str]:
        """Find all transitive dependencies.

        Args:
            node_id: Node ID

        Returns:
            Set of all dependency node IDs
        """
        visited = set()
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for dep in self.adjacency.get(current, []):
                if dep not in visited:
                    queue.append(dep)

        visited.discard(node_id)
        return visited

    def find_all_dependents(self, node_id: str) -> Set[str]:
        """Find all transitive dependents.

        Args:
            node_id: Node ID

        Returns:
            Set of all dependent node IDs
        """
        visited = set()
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for dep in self.reverse_adjacency.get(current, []):
                if dep not in visited:
                    queue.append(dep)

        visited.discard(node_id)
        return visited

    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between two nodes.

        Args:
            start: Start node ID
            end: End node ID

        Returns:
            List of node IDs forming the path, or None
        """
        if start not in self.nodes or end not in self.nodes:
            return None

        if start == end:
            return [start]

        visited = {start}
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            for neighbor in self.adjacency.get(current, []):
                if neighbor == end:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics.

        Returns:
            Statistics dictionary
        """
        edge_types = defaultdict(int)
        for edge in self.edges:
            edge_types[edge.edge_type] += 1

        # Find nodes with most dependencies
        most_dependents = sorted(
            [(nid, len(deps)) for nid, deps in self.adjacency.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "edge_types": dict(edge_types),
            "most_dependent_nodes": [
                {"id": nid, "count": count}
                for nid, count in most_dependents
            ],
        }


class GraphBuilder:
    """Build code graphs from source files."""

    # Import patterns by language
    IMPORT_PATTERNS = {
        "python": [
            r'^(?:from\s+(\S+)\s+import|import\s+(\S+))',
            r'import\s+([\w.]+)',
            r'from\s+([\w.]+)\s+import',
        ],
        "javascript": [
            r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]",
            r"require\s*\(\s*['\"]([^'\"]+)['\"]",
        ],
        "go": [
            r'import\s+"([^"]+)"',
            r"import\s+\(\s*\"([^\"]+)\"",
        ],
    }

    # Function call patterns
    CALL_PATTERNS = {
        "python": [
            r'def\s+(\w+)\s*\(',
            r'(\w+)\s*\(',
        ],
        "javascript": [
            r'function\s+(\w+)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
            r'(\w+)\s*\(',
        ],
    }

    def __init__(self, language: str = "python"):
        """Initialize graph builder.

        Args:
            language: Programming language
        """
        self.language = language
        self.graph = CodeGraph()

    def build_from_file(
        self,
        file_path: str,
        code_content: str,
    ) -> CodeGraph:
        """Build graph from a single file.

        Args:
            file_path: Path to file
            code_content: Source code

        Returns:
            Built graph
        """
        # Add file node
        file_node = Node(
            id=file_path,
            name=file_path.split('/')[-1],
            node_type="file",
            file_path=file_path,
        )
        self.graph.add_node(file_node)

        # Find imports
        imports = self._find_imports(code_content)
        for imp in imports:
            imp_node_id = f"import:{imp}"
            imp_node = Node(
                id=imp_node_id,
                name=imp,
                node_type="import",
            )
            self.graph.add_node(imp_node)

            self.graph.add_edge(Edge(
                source=file_path,
                target=imp_node_id,
                edge_type="imports",
            ))

        # Find functions/classes
        functions = self._find_functions(code_content)

        for func_name, func_line in functions:
            func_node_id = f"{file_path}:{func_name}"
            func_node = Node(
                id=func_node_id,
                name=func_name,
                node_type="function",
                file_path=file_path,
                line_number=func_line,
            )
            self.graph.add_node(func_node)

            self.graph.add_edge(Edge(
                source=file_path,
                target=func_node_id,
                edge_type="contains",
            ))

            # Find function calls
            calls = self._find_function_calls(code_content, func_name)
            for call in calls:
                call_node_id = f"{file_path}:{call}"
                if call_node_id in self.graph.nodes:
                    self.graph.add_edge(Edge(
                        source=func_node_id,
                        target=call_node_id,
                        edge_type="calls",
                    ))

        return self.graph

    def build_from_files(
        self,
        files: Dict[str, str],
    ) -> CodeGraph:
        """Build graph from multiple files.

        Args:
            files: Dictionary of file_path -> code_content

        Returns:
            Built graph
        """
        for file_path, code_content in files.items():
            self.build_from_file(file_path, code_content)

        # Link imports to actual files
        self._resolve_import_links()

        return self.graph

    def _find_imports(self, code_content: str) -> List[str]:
        """Find imports in code.

        Args:
            code_content: Source code

        Returns:
            List of import paths
        """
        imports = []
        patterns = self.IMPORT_PATTERNS.get(self.language, [])

        for pattern in patterns:
            for match in re.finditer(pattern, code_content, re.MULTILINE):
                groups = match.groups()
                for group in groups:
                    if group:
                        # Clean up the import path
                        imp = group.strip()
                        if not imp.startswith('.'):
                            imports.append(imp)

        return imports

    def _find_functions(self, code_content: str) -> List[tuple]:
        """Find function definitions.

        Args:
            code_content: Source code

        Returns:
            List of (function_name, line_number)
        """
        functions = []
        patterns = self.CALL_PATTERNS.get(self.language, [])

        for pattern in patterns:
            for match in re.finditer(pattern, code_content):
                name = match.group(1)
                line_num = code_content[:match.start()].count('\n') + 1
                functions.append((name, line_num))

        return functions

    def _find_function_calls(
        self,
        code_content: str,
        function_name: str,
    ) -> List[str]:
        """Find calls within a function.

        Args:
            code_content: Source code
            function_name: Function to find calls in

        Returns:
            List of called function names
        """
        calls = []

        # Find function body
        pattern = rf'def\s+{function_name}\s*\([^)]*\):(.*?)(?=\ndef\s|\Z)'
        match = re.search(pattern, code_content, re.DOTALL)

        if match:
            func_body = match.group(1)

            # Find calls in body
            call_pattern = r'(\w+)\s*\('
            for call_match in re.finditer(call_pattern, func_body):
                calls.append(call_match.group(1))

        return calls

    def _resolve_import_links(self):
        """Resolve import references to actual file nodes."""
        # This would require knowing the project structure
        # Simplified version just marks external imports
        pass


def build_call_graph(
    files: Dict[str, str],
    language: str = "python",
) -> CodeGraph:
    """Build call graph from source files.

    Args:
        files: Dictionary of file_path -> code_content
        language: Programming language

    Returns:
        Code graph
    """
    builder = GraphBuilder(language)
    return builder.build_from_files(files)
