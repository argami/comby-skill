# Comby Skill Plugin - Diseño Final

## Principios Fundamentales

1. **Autocontenido**: Todo lo necesario para funcionar está dentro del plugin
2. **Estándar Anthropic**: Sigue el modelo oficial de Claude Code plugins
3. **Hooks Auto-Instalados**: Se instalan y quedan activos sin tocar `~/.claude/`
4. **Portabilidad**: Funciona igual en cualquier máquina con Claude Code
5. **Usuario Control**: El usuario puede customizar via `~/.claude/CLAUDE.md` si quiere

## Estructura Final del Plugin

```
comby-skill-plugin/
│
├── .claude-plugin/
│   ├── plugin.json                ← Único manifiesto oficial
│   └── .mcp.json                  ← Configuración MCP (opcional)
│
├── skills/
│   └── comby-search/
│       └── SKILL.md               ← Agent Skill (formato Anthropic)
│
├── commands/
│   ├── comby-search.md            ← Comando /comby-search
│   ├── comby-analyze.md           ← Comando /comby-analyze
│   └── comby-inventory.md         ← Comando /comby-inventory
│
├── hooks/
│   ├── pre-tool-use.js            ← Auto-instalado (enabled: true)
│   ├── post-tool-use.js           ← Auto-instalado (enabled: true)
│   ├── file-change-analysis.js    ← User-optional (enabled: false)
│   ├── pre-commit-analysis.js     ← User-optional (enabled: false)
│   └── hook-manifest.json         ← Metadatos de hooks
│
├── scripts/
│   ├── search.py                  ← Lógica de búsqueda
│   ├── analyze.py                 ← Lógica de análisis
│   └── utils.py                   ← Utilidades compartidas
│
├── references/
│   ├── PATTERNS.md                ← Patrones de búsqueda comunes
│   ├── SECURITY-CHECKS.md         ← Análisis de seguridad
│   └── EXAMPLES.md                ← Ejemplos de uso
│
├── assets/
│   ├── example-project.claude.md  ← Template para usuarios
│   └── search-patterns.json       ← Patrones predefinidos
│
├── README.md                      ← Documentación principal
└── LICENSE                        ← Licencia MIT
```

## Plugin.json - Manifiesto Único

Archivo: `.claude-plugin/plugin.json`

Responsabilidades:
- Identidad del plugin (nombre, versión, autor)
- Declaración de skills (qué skills expone)
- Declaración de comandos (qué comandos registra)
- Declaración de hooks (qué hooks instala y cómo)
- Configuración de eventos
- Metadatos y metadata

```json
{
  "name": "comby-skill",
  "displayName": "Comby Pattern Search & Analysis",
  "description": "Pattern matching and code analysis skill for Claude Code. Search code patterns, analyze for vulnerabilities, and generate code inventories.",
  "version": "1.0.0",
  "author": {
    "name": "argami",
    "email": "your-email@example.com"
  },
  "license": "MIT",
  "homepage": "https://github.com/argami/comby-skill",
  "repository": {
    "type": "git",
    "url": "https://github.com/argami/comby-skill"
  },
  "engines": {
    "claude-code": ">=1.0.0"
  },
  "keywords": ["pattern-matching", "code-search", "security-analysis", "refactoring"],
  "categories": ["analysis", "code-quality", "security"],
  "activationEvents": ["*"],

  "contributes": {
    "skills": [
      {
        "path": "skills/comby-search/SKILL.md"
      }
    ],
    "commands": [
      {
        "path": "commands/comby-search.md"
      },
      {
        "path": "commands/comby-analyze.md"
      },
      {
        "path": "commands/comby-inventory.md"
      }
    ],
    "hooks": [
      {
        "id": "comby-pre-tool-use",
        "name": "Pre-Tool Use Analysis",
        "description": "Analyze context before tools are executed",
        "file": "hooks/pre-tool-use.js",
        "events": ["PreToolUse"],
        "enabled": true,
        "autoInstall": true,
        "userConfigurable": false
      },
      {
        "id": "comby-post-tool-use",
        "name": "Post-Tool Use Analysis",
        "description": "Analyze results after tools complete",
        "file": "hooks/post-tool-use.js",
        "events": ["PostToolUse"],
        "enabled": true,
        "autoInstall": true,
        "userConfigurable": false
      },
      {
        "id": "comby-file-change-analysis",
        "name": "File Change Analysis",
        "description": "Auto-analyze when files change in the project",
        "file": "hooks/file-change-analysis.js",
        "events": ["FileChange"],
        "enabled": false,
        "autoInstall": true,
        "userConfigurable": true,
        "configKey": "comby.hooks.fileChangeAnalysis"
      },
      {
        "id": "comby-pre-commit-analysis",
        "name": "Pre-Commit Analysis",
        "description": "Analyze code before git commits",
        "file": "hooks/pre-commit-analysis.js",
        "events": ["PreCommit"],
        "enabled": false,
        "autoInstall": true,
        "userConfigurable": true,
        "configKey": "comby.hooks.preCommitAnalysis"
      }
    ]
  },

  "configuration": {
    "comby.hooks.fileChangeAnalysis": {
      "type": "boolean",
      "default": false,
      "description": "Enable automatic analysis when files change"
    },
    "comby.hooks.preCommitAnalysis": {
      "type": "boolean",
      "default": false,
      "description": "Enable automatic analysis before git commits"
    },
    "comby.analysis.securityFocus": {
      "type": "boolean",
      "default": true,
      "description": "Focus analysis on security patterns"
    },
    "comby.analysis.excludePatterns": {
      "type": "array",
      "default": ["*test*", "*spec*", "node_modules", ".git"],
      "description": "Patterns to exclude from analysis"
    }
  }
}
```

## Cómo Funciona la Instalación

### Paso 1: Usuario instala el plugin
```bash
/plugin install comby-skill
```

### Paso 2: Claude Code procesa plugin.json

Claude Code automáticamente:

1. Lee `.claude-plugin/plugin.json`
2. Valida la estructura
3. Para cada skill en `contributes.skills`:
   - Registra la skill en Claude Code
   - La skill queda disponible para Claude automáticamente
4. Para cada comando en `contributes.commands`:
   - Registra el comando como disponible
   - Usuario puede usarlo: `/comby-search`, etc.
5. Para cada hook en `contributes.hooks`:
   - Si `enabled: true` → Lo instala y activa inmediatamente
   - Si `enabled: false` → Lo instala pero inactivo (user-optional)
   - Registra en Claude Code para que se ejecute en los eventos especificados

### Paso 3: Hooks activos sin configuración

Resultado inmediatamente después de instalar:

```
✅ comby-search skill → registrada
✅ /comby-search comando → disponible
✅ /comby-analyze comando → disponible
✅ /comby-inventory comando → disponible
✅ pre-tool-use hook → ACTIVO (se ejecuta antes de cualquier tool)
✅ post-tool-use hook → ACTIVO (se ejecuta después de cualquier tool)
⏸️  file-change-analysis hook → instalado pero INACTIVO
⏸️  pre-commit-analysis hook → instalado pero INACTIVO
```

**Punto clave**: Los hooks que están en `enabled: true` se ejecutan automáticamente en los eventos especificados. No requieren configuración del usuario.

### Paso 4: Usuario puede customizar (opcional)

En `~/.claude/CLAUDE.md`, el usuario PUEDE añadir:

```yaml
plugins:
  comby-skill:
    config:
      comby.hooks.fileChangeAnalysis: true
      comby.hooks.preCommitAnalysis: true
      comby.analysis.securityFocus: true
      comby.analysis.excludePatterns: ["*test*", "node_modules"]
```

Pero esto es **completamente opcional**. Sin esto, el plugin funciona con configuración por defecto.

## Hooks Auto-Instalados

### Hook 1: `pre-tool-use.js` (Auto-instalado, enabled: true)

Se ejecuta ANTES de que Claude Code use cualquier herramienta.

```javascript
// hooks/pre-tool-use.js

module.exports = {
  id: "comby-pre-tool-use",

  async onPreToolUse(context) {
    // context = { toolName, args, currentFile, codebase }

    // Análisis preventivo automático
    // Sin requerer que el usuario haga nada
  }
};
```

### Hook 2: `post-tool-use.js` (Auto-instalado, enabled: true)

Se ejecuta DESPUÉS de que una herramienta completa.

```javascript
// hooks/post-tool-use.js

module.exports = {
  id: "comby-post-tool-use",

  async onPostToolUse(context) {
    // context = { toolName, result, duration }

    // Análisis de resultados automático
    // Sin requerer que el usuario haga nada
  }
};
```

### Hook 3: `file-change-analysis.js` (User-optional, enabled: false)

Se ejecuta cuando archivos cambian, **solo si el usuario lo activa**.

```javascript
// hooks/file-change-analysis.js

module.exports = {
  id: "comby-file-change-analysis",

  async onFileChange(context) {
    // context = { filePath, changeType, isDirty }

    // Solo se ejecuta si:
    // comby.hooks.fileChangeAnalysis = true
    // en ~/.claude/CLAUDE.md
  }
};
```

### Hook 4: `pre-commit-analysis.js` (User-optional, enabled: false)

Se ejecuta antes de commits git, **solo si el usuario lo activa**.

```javascript
// hooks/pre-commit-analysis.js

module.exports = {
  id: "comby-pre-commit-analysis",

  async onPreCommit(context) {
    // context = { stagedFiles, commitMessage }

    // Solo se ejecuta si:
    // comby.hooks.preCommitAnalysis = true
    // en ~/.claude/CLAUDE.md
  }
};
```

## Punto Clave: Sin Tocar ~/.claude/

**CRÍTICO**: Los hooks no se instalan en `~/.claude/` del usuario.

Donde van los hooks:

```
~/.claude/plugins/comby-skill/          ← Aquí vive el plugin
├── .claude-plugin/plugin.json          ← Describe todo
├── hooks/
│   ├── pre-tool-use.js                 ← Aquí
│   ├── post-tool-use.js                ← Aquí
│   ├── file-change-analysis.js         ← Aquí
│   └── pre-commit-analysis.js          ← Aquí
└── ...
```

Dónde NO van:

```
~/.claude/                              ← Nunca aquí
  ├── hooks/                            ← No auto-instala
  ├── CLAUDE.md                         ← No modifica
  └── ...
```

El usuario PUEDE opcionalmente poner referencias en `~/.claude/CLAUDE.md`:

```yaml
# ~/.claude/CLAUDE.md
plugins:
  comby-skill:
    config:
      comby.hooks.fileChangeAnalysis: true
```

Pero esto es **configuración**, no **instalación de hooks**. Los hooks ya están instalados dentro del plugin.

## Estructura de Directorios - Resumen

| Directorio | Propósito | Auto-Instala |
|-----------|-----------|-------------|
| `.claude-plugin/` | Manifiesto oficial | N/A (es metadata) |
| `skills/` | Agent Skills (Anthropic format) | ✅ Sí |
| `commands/` | Comandos custom | ✅ Sí |
| `hooks/` | Scripts de extensión | ✅ Sí (si enabled: true) |
| `scripts/` | Lógica ejecutable | ✅ Sí (referenciada) |
| `references/` | Documentación | ❌ No (on-demand) |
| `assets/` | Templates y recursos | ❌ No (on-demand) |

## Flujo Completo para Usuario Nuevo

```
Usuario: /plugin install comby-skill
   ↓
Claude Code descarga el plugin de la registry
   ↓
Claude Code lee .claude-plugin/plugin.json
   ↓
Claude Code procesa cada sección:

   contributes.skills:
   ✅ Registra comby-search skill
      (queda disponible automáticamente)

   contributes.commands:
   ✅ Registra /comby-search
   ✅ Registra /comby-analyze
   ✅ Registra /comby-inventory
      (usuario puede usar inmediatamente)

   contributes.hooks:
   ✅ pre-tool-use (enabled: true)
      → Instala en hooks/pre-tool-use.js
      → Activa automáticamente
      → Se ejecuta en eventos PreToolUse

   ✅ post-tool-use (enabled: true)
      → Instala en hooks/post-tool-use.js
      → Activa automáticamente
      → Se ejecuta en eventos PostToolUse

   ✅ file-change-analysis (enabled: false, userConfigurable: true)
      → Instala en hooks/file-change-analysis.js
      → Inactivo por defecto
      → Usuario puede activar en ~/.claude/CLAUDE.md

   ✅ pre-commit-analysis (enabled: false, userConfigurable: true)
      → Instala en hooks/pre-commit-analysis.js
      → Inactivo por defecto
      → Usuario puede activar en ~/.claude/CLAUDE.md
   ↓
Listo para usar:
   ✅ /comby-search "pattern" src/
   ✅ /comby-analyze file.py
   ✅ /comby-inventory src/
   ✅ Hooks pre-tool-use y post-tool-use ejecutándose automáticamente

Configuración del usuario (~/.claude/CLAUDE.md):
   (completamente opcional)
   plugins:
     comby-skill:
       config:
         comby.hooks.fileChangeAnalysis: true
         comby.hooks.preCommitAnalysis: true
   ↓
   ✅ file-change-analysis se activa
   ✅ pre-commit-analysis se activa
```

## Archivos a Crear (Resumen)

✅ `.claude-plugin/plugin.json` - Único manifiesto oficial
✅ `skills/comby-search/SKILL.md` - Agent Skill
✅ `commands/comby-search.md` - Comando
✅ `commands/comby-analyze.md` - Comando
✅ `commands/comby-inventory.md` - Comando
✅ `hooks/pre-tool-use.js` - Hook auto-instalado
✅ `hooks/post-tool-use.js` - Hook auto-instalado
✅ `hooks/file-change-analysis.js` - Hook user-optional
✅ `hooks/pre-commit-analysis.js` - Hook user-optional
✅ `hooks/hook-manifest.json` - Metadatos de hooks
✅ `scripts/search.py` - Lógica
✅ `scripts/analyze.py` - Lógica
✅ `scripts/utils.py` - Lógica
✅ `references/PATTERNS.md` - Documentación
✅ `references/SECURITY-CHECKS.md` - Documentación
✅ `references/EXAMPLES.md` - Documentación
✅ `assets/example-project.claude.md` - Template
✅ `assets/search-patterns.json` - Datos
✅ `README.md` - Documentación principal
✅ `LICENSE` - Licencia MIT

## Características del Diseño

| Característica | Implementado |
|---|---|
| Plugin autocontenido | ✅ |
| Estándar Anthropic | ✅ |
| Hooks auto-instalados | ✅ |
| Sin tocar ~/.claude/ | ✅ |
| Manifiesto único (plugin.json) | ✅ |
| Skills registradas | ✅ |
| Comandos registrados | ✅ |
| Configuración user-optional | ✅ |
| Portable y reutilizable | ✅ |

---

**Estado**: Diseño final aprobado. Listo para implementación.
