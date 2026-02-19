/**
 * Pre-Commit Analysis Hook for Comby Skill Plugin
 *
 * Executes before git commits are created.
 * OPTIONAL: Only runs if enabled by user in configuration.
 *
 * This hook is INSTALLED but DISABLED by default.
 * User can enable it in ~/.claude/CLAUDE.md:
 *
 *   plugins:
 *     comby-skill:
 *       config:
 *         comby.hooks.preCommitAnalysis: true
 */

module.exports = {
  id: "comby-pre-commit-analysis",
  name: "Pre-Commit Analysis",
  configKey: "comby.hooks.preCommitAnalysis",

  /**
   * Main execution function
   * Called before git commit
   *
   * @param {Object} context - Execution context
   * @param {Array<string>} context.stagedFiles - Files staged for commit
   * @param {string} context.commitMessage - Commit message (if available)
   * @param {Object} context.config - Plugin configuration
   * @returns {Object} { continueExecution: boolean }
   */
  async execute(context) {
    const { stagedFiles, commitMessage, config } = context;

    try {
      // Check if this hook is enabled
      if (!isEnabled(config)) {
        return { continueExecution: true };
      }

      console.log(`📦 Pre-commit analysis: ${stagedFiles.length} file(s) staged`);

      // Pattern 1: Check for security issues in staged files
      const securityIssues = checkSecurityIssues(stagedFiles, config);
      if (securityIssues && securityIssues.length > 0) {
        console.log(`🔒 Potential security issues in ${securityIssues.length} file(s):`);
        securityIssues.forEach(file => {
          console.log(`   - ${file}`);
        });
        console.log("   Recommend: Run /comby-analyze --focus security");
      }

      // Pattern 2: Check for incomplete code (TODO/FIXME)
      const incompleteFiles = checkIncompleteCode(stagedFiles);
      if (incompleteFiles && incompleteFiles.length > 0) {
        console.log(`⚠️  TODO/FIXME markers found in ${incompleteFiles.length} file(s)`);
        incompleteFiles.forEach(file => {
          console.log(`   - ${file}`);
        });
      }

      // Pattern 3: Analyze commit message quality
      if (commitMessage) {
        analyzeCommitMessage(commitMessage);
      }

      // Pattern 4: Large commit detection
      if (stagedFiles.length > 20) {
        console.log(`📊 Large commit detected (${stagedFiles.length} files)`);
        console.log("   Consider: Breaking into smaller, focused commits");
      }

      return { continueExecution: true };

    } catch (error) {
      console.error("Error in pre-commit-analysis hook:", error.message);
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
  return config.get && config.get("comby.hooks.preCommitAnalysis") === true;
}

/**
 * Check staged files for security issues
 */
function checkSecurityIssues(stagedFiles, config) {
  const securityFocus = config && config.get("comby.analysis.securityFocus") !== false;
  if (!securityFocus) return [];

  const issues = [];

  stagedFiles.forEach(file => {
    // Check for sensitive files
    if (isSensitiveFile(file)) {
      issues.push(file);
    }
  });

  return issues;
}

/**
 * Check for incomplete code markers
 */
function checkIncompleteCode(stagedFiles) {
  // In production, would actually read files
  const todoMarkers = [];

  stagedFiles.forEach(file => {
    // Check for common markers in filenames/paths
    if (file.includes("TODO") || file.includes("WIP")) {
      todoMarkers.push(file);
    }
  });

  return todoMarkers;
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
    /api.*key/i,
    /key\.json/,
    /private/i
  ];

  return sensitivePatterns.some(pattern => pattern.test(filePath));
}

/**
 * Analyze commit message quality
 */
function analyzeCommitMessage(message) {
  // Check for conventional commit format
  const conventionalPattern = /^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?:/;

  if (!conventionalPattern.test(message)) {
    console.log("💡 Commit message tip: Consider using Conventional Commits format");
    console.log("   Format: <type>(<scope>): <description>");
    console.log("   Example: feat(auth): add JWT authentication");
  }

  // Check for meaningful message
  const words = message.split(" ");
  if (words.length < 3) {
    console.log("💡 Commit message too short - consider being more descriptive");
  }
}
