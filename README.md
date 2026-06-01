# futbol-report

## CI Security Scanning

Two automated security checks run on every push, pull request to `main`, and weekly on a schedule:

- **gitleaks** — scans the full commit history for accidentally committed secrets (API keys, tokens, etc.). The workflow fails immediately if any are detected.
- **osv-scanner** — checks `uv.lock` against Google's [OSV database](https://osv.dev) for known CVEs. HIGH/CRITICAL findings block the merge; MEDIUM/LOW findings surface as warnings in the Security tab.
- **Dependabot** — opens weekly pull requests for available dependency upgrades (Python packages and GitHub Actions). PRs require human review; auto-merge is not enabled.
