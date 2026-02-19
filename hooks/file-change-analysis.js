/**
 * File Change Analysis Hook for Comby Skill Plugin
 *
 * Executes when files change in the project.
 * OPTIONAL: Only runs if enabled by user in configuration.
 *
 * This hook is INSTALLED but DISABLED by default.
 * User can enable it in ~/.claude/CLAUDE.md:
 *
 *   plugins:
 *     comby-skill:
 *       config:
 *         comby.hooks.fileChangeAnalysis: true
 */

module.exports = {
  id: "comby-file-change-analysis",
  name: "File Change Analysis",
  configKey: "comby.hooks.fileChangeAnalysis",

  /**
   * Main execution function
   * Called when files change (create, modify, delete)
   *
   * @param {Object} context - Execution context
   * @param {string} context.filePath - Path to the changed file
   * @param {string} context.changeType - Type of change: 'created', 'modified', 'deleted'
   * @param {boolean} context.isDirty - Whether file has unsaved changes
   * @param {Object} context.config - Plugin configuration
   * @returns {Object} { continueExecution: boolean }
   */
  async execute(context) {
    const { filePath, changeType, isDirty, config } = context;

    try {
      // Check if this hook is enabled
      if (!isEnabled(config)) {
        return { continueExecution: true };
      }

      console.log(`📝 File ${changeType}: ${filePath}`);

      // Pattern 1: Analyze modified files for issues
      if (changeType === "modified" && shouldAnalyzeFile(filePath, config)) {
        console.log("🔍 Running quick analysis on modified file...");
        // Would call comby-analyze
        suggestAnalysis(filePath);
      }

      // Pattern 2: Detect new vulnerable patterns
      if (changeType === "created" && isSensitiveFile(filePath)) {
        console.log("🔒 New sensitive file detected");
        console.log("   Recommend: Run /comby-analyze for security checks");
      }

      // Pattern 3: Track deleted files
      if (changeType === "deleted") {
        console.log("🗑️  File deleted");
        // Could track for cleanup operations
      }

      return { continueExecution: true };

    } catch (error) {
      console.error("Error in file-change-analysis hook:", error.message);
      return { continueExecution: true };
    }
  }
};

/**
 * Helper Functions
 */

/**
 * Check if this hook is enabled in user config
 */
function isEnabled(config) {
  if (!config) return false;
  return config.get && config.get("comby.hooks.fileChangeAnalysis") === true;
}

/**
 * Determine if file should be analyzed
 */
function shouldAnalyzeFile(filePath, config) {
  // Skip test files by default
  if (filePath.includes("test") || filePath.includes("spec")) {
    return false;
  }

  // Skip non-code files
  const codeExtensions = [
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".go", ".rb", ".php", ".cs",
    ".cpp", ".c", ".h", ".rs"
  ];

  return codeExtensions.some(ext => filePath.endsWith(ext));
}

/**
 * Check if file is sensitive
 */
function isSensitiveFile(filePath) {
  const sensitivePatterns = [
    /config/i,
    /credentials/i,
    /secret/i,
    /\.env/,
    /password/i,
    /key\.json/
  ];

  return sensitivePatterns.some(pattern => pattern.test(filePath));
}

/**
 * Suggest appropriate analysis
 */
function suggestAnalysis(filePath) {
  if (isSensitiveFile(filePath)) {
    console.log("   /comby-analyze --focus security");
  } else if (filePath.includes("test")) {
    console.log("   /comby-analyze --focus quality");
  } else {
    console.log("   /comby-analyze");
  }
}
