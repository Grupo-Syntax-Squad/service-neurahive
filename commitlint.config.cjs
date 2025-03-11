module.exports = {
    extends: ["@commitlint/config-conventional"],
    rules: {
        "type-enum": [2, "always", [
            "feat", "fix", "docs", "style", "refactor",
            "perf", "test", "build", "ci", "chore", "revert"
        ]],
        "subject-case": [2, "always", "sentence-case"],
        "header-max-length": [2, "always", 100],
        "references-empty": [2, "never"],
        "header-pattern": [2, "always", /^(\w+):\s#\d+\s.+$/],
        "header-correspondence": ["type", "subject"]
    }
};
