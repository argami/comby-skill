/**
 * Pre-Tool Use Hook for Comby Skill Plugin
 *
 * Executes BEFORE Claude Code uses any tool or command.
 * Provides contextual analysis to guide tool selection and usage.
 *
 * This hook is AUTO-INSTALLED and ENABLED by default.
 * It does NOT require user configuration.
 */

module.exports = {
  id: "comby-pre-tool-use",
  name: "Pre-Tool Use Analysis",

  /**
   * Main execution function
   * Called before any tool executes
   *
   * @param {Object} context - Execution context
   * @param {string} context.toolName - Name of the tool about to execute
   * @param {Object} context.args - Arguments passed to the tool
   * @param {string} context.currentFile - Currently open file (if any)
   * @param {Object} context.codebase - Metadata about the codebase
   * @returns {Object} { continueExecution: boolean }
   */
  async execute(context) {
    const { toolName, args, currentFile, codebase } = context;

    try {
      // Pattern 1: Suggest Comby for grep/find operations
      if (toolName === "Bash" && (args.includes("grep") || args.includes("find"))) {
        const grepPattern = extractGrepPattern(args);
        if (grepPattern) {
          console.log(`💡 Tip: Consider using /comby-search "${grepPattern}" for better pattern matching`);
        }
      }

      // Pattern 2: Security context detection
      if (isSensitiveFile(currentFile)) {
        console.log("🔒 Security context detected: Analyzing sensitive file access");
        logSecurityContext(currentFile);
      }

      // Pattern 3: Large-scale search detection
      if (toolName === "Bash" && isLargeScaleSearch(args)) {
        console.log("📊 Large-scale search detected");
        console.log(`   Consider using /comby-search for better performance and output options`);
      }

      // Pattern 4: Refactoring operation detection
      if (isRefactoringOperation(toolName, args)) {
        console.log("🔄 Refactoring operation detected");
        console.log("   Tip: Pre-analysis with /comby-search helps identify all affected locations");
      }

      // Allow execution to continue
      return { continueExecution: true };

    } catch (error) {
      console.error("Error in pre-tool-use hook:", error.message);
      // Don't block execution on hook error
      return { continueExecution: true };
    }
  }
};

/**
 * Helper Functions
 */

/**
 * Extract grep pattern from bash arguments
 */
function extractGrepPattern(args) {
  try {
    // Simple extraction - in production, would be more sophisticated
    const match = args.match(/'([^']*)'|"([^"]*)"/);
    return match ? (match[1] || match[2]) : null;
  } catch {
    return null;
  }
}

/**
 * Check if file is sensitive (credentials, config, secrets)
 */
function isSensitiveFile(filePath) {
  if (!filePath) return false;

  const sensitivePatterns = [
    /config/i,
    /credentials/i,
    /secret/i,
    /\.env/,
    /password/i,
    /api.*key/i,
    /key\.json/,
    /private/i
  ];

  return sensitivePatterns.some(pattern => pattern.test(filePath));
}

/**
 * Log security context information
 */
function logSecurityContext(filePath) {
  console.log(`   File: ${filePath}`);
  console.log("   Consider: Use /comby-analyze for security checks");
}

/**
 * Detect large-scale search operations
 */
function isLargeScaleSearch(args) {
  // Patterns that suggest searching entire codebase
  const largeScalePatterns = [
    /grep.*-r/,          // recursive grep
    /find.*\./,          // find from root
    /-R\s+/,              // -R flag (recursive)
    /--include=\*/       // searching all files
  ];

  const argString = typeof args === 'string' ? args : args.join(' ');
  return largeScalePatterns.some(pattern => pattern.test(argString));
}

/**
 * Detect refactoring operations
 */
function isRefactoringOperation(toolName, args) {
  const refactoringKeywords = [
    "rename",
    "refactor",
    "replace",
    "sed",
    "find.*-replace"
  ];

  const argString = typeof args === 'string' ? args : args.join(' ');
  return refactoringKeywords.some(keyword => argString.toLowerCase().includes(keyword));
}
