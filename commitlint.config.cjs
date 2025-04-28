module.exports = {
    extends: ["@commitlint/config-conventional"],
    rules: {
        "type-enum": [2, "always", [
            "feat", "fix", "docs", "style", "refactor",
            "perf", "test", "build", "ci", "chore", "revert"
        ]],
        "header-max-length": [2, "always", 100],
        "references-empty": [2, "never"],
        "scope-empty": [1, 'always'],
    },
    parserPreset: {
        parserOpts: {
            headerPattern: /^(\w+):\s#(\d+)\s(.+)$/,
            headerCorrespondence: ["type", "issue", "subject"]
        }
    }
};
