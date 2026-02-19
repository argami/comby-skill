/**
 * Post-Tool Use Hook for Comby Skill Plugin
 *
 * Executes AFTER a tool or command completes.
 * Analyzes results and suggests follow-up actions.
 *
 * This hook is AUTO-INSTALLED and ENABLED by default.
 * It does NOT require user configuration.
 */

module.exports = {
  id: "comby-post-tool-use",
  name: "Post-Tool Use Analysis",

  /**
   * Main execution function
   * Called after any tool completes
   *
   * @param {Object} context - Execution context
   * @param {string} context.toolName - Name of the tool that executed
   * @param {Object} context.result - Result/output from the tool
   * @param {number} context.duration - Execution time in milliseconds
   * @param {boolean} context.success - Whether tool succeeded
   * @returns {Object} { continueExecution: boolean }
   */
  async execute(context) {
    const { toolName, result, duration, success } = context;

    try {
      // Skip if tool failed
      if (!success) {
        return { continueExecution: true };
      }

      // Pattern 1: Search results analysis
      if (isSearchResult(toolName, result)) {
        analyzeSearchResults(result);
      }

      // Pattern 2: Performance monitoring
      if (duration > 5000) {
        console.log(`⏱️  Performance: Tool '${toolName}' took ${(duration / 1000).toFixed(2)}s`);
        console.log("   Consider: Breaking down operation or using /comby-search for patterns");
      }

      // Pattern 3: Large output analysis
      if (hasLargeOutput(result)) {
        console.log(`📊 Large result set detected (${countResults(result)} items)`);
        console.log("   Consider: Using /comby-search with JSON output for structured data");
      }

      // Pattern 4: Error detection in output
      if (hasErrorPatterns(result)) {
        console.log("⚠️  Potential errors detected in output");
        logErrorPatterns(result);
      }

      return { continueExecution: true };

    } catch (error) {
      console.error("Error in post-tool-use hook:", error.message);
      // Don't block execution on hook error
      return { continueExecution: true };
    }
  }
};

/**
 * Helper Functions
 */

/**
 * Check if result is from a search operation
 */
function isSearchResult(toolName, result) {
  return toolName === "Bash" || toolName === "Grep";
}

/**
 * Analyze search results and provide insights
 */
function analyzeSearchResults(result) {
  const resultCount = countResults(result);

  if (resultCount === 0) {
    console.log("ℹ️  No results found");
    return;
  }

  if (resultCount === 1) {
    console.log("✅ Found 1 result");
    return;
  }

  if (resultCount > 10 && resultCount < 100) {
    console.log(`✅ Found ${resultCount} results`);
    console.log("   Tip: Use /comby-inventory to export structured data");
    return;
  }

  if (resultCount >= 100) {
    console.log(`⚠️  Found ${resultCount} results (large dataset)`);
    console.log("   Recommend: Export to JSON for analysis");
    console.log("   Command: /comby-search <pattern> <path> -f json");
    return;
  }
}

/**
 * Count results in output
 */
function countResults(result) {
  if (typeof result === 'number') {
    return result;
  }

  if (typeof result === 'string') {
    // Count lines that look like matches
    const lines = result.split('\n').filter(line => line.trim());
    return lines.length;
  }

  if (Array.isArray(result)) {
    return result.length;
  }

  if (typeof result === 'object' && result.matches) {
    return result.matches.length;
  }

  return 0;
}

/**
 * Check if output is large
 */
function hasLargeOutput(result) {
  const resultCount = countResults(result);
  return resultCount > 50;
}

/**
 * Check for error patterns in output
 */
function hasErrorPatterns(result) {
  if (typeof result !== 'string') return false;

  const errorPatterns = [
    /error/i,
    /exception/i,
    /failed/i,
    /ERROR|ERROR:/,
    /Traceback/,
    /undefined/i
  ];

  return errorPatterns.some(pattern => pattern.test(result));
}

/**
 * Log detected error patterns
 */
function logErrorPatterns(result) {
  const resultStr = String(result);

  if (/ERROR|Exception|Traceback/.test(resultStr)) {
    console.log("   This might be a tool error or application error");
  }

  if (/undefined/i.test(resultStr)) {
    console.log("   Undefined references detected - may indicate missing code");
  }
}
