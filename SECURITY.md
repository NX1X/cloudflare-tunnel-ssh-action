# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | :white_check_mark: |
| < latest| :x:                |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, please report vulnerabilities privately:

1. Go to the [Security Advisories](https://github.com/NX1X/cloudflare-tunnel-ssh-action/security/advisories) page
2. Click "Report a vulnerability"
3. Provide a clear description and reproduction steps

You will receive a response within 72 hours. If confirmed, a fix will be
released as a patch version and credited in the changelog.

## Security Practices

- CI runs `actionlint` and `shellcheck` on every push and PR
- All secrets are passed through `env:` blocks (masked by GitHub Actions) - never inlined in shell commands
- The wrapper script (`~/.cloudflared-ssh`) is created with `chmod 700` - readable only by the owner
- SSH private keys are written with `chmod 600`
- The "Verify setup" step redacts all credentials in output using `sed`
- No telemetry, no analytics, no external calls - all processing stays on your runner
- Dependencies are monitored via Dependabot for GitHub Actions version updates
- Releases include source verification via git tags
- The cleanup sub-action removes sensitive artifacts (SSH keys, wrapper script with embedded credentials) after job completion
- The state file (`~/.cloudflared-ssh-state`) contains only file paths and hostnames - no credentials
- Known hosts support enables `StrictHostKeyChecking yes` for strict host key verification

## Security Changelog

| Date | Change |
|------|--------|
| 2026-05-09 | v1.1.0 - Changed `StrictHostKeyChecking` default from `no` to `accept-new` (MITM prevention), added input validation for `connect-timeout` and `server-alive-interval`, disabled shell glob expansion in host list loops, switched to `grep -F` for fixed-string hostname matching, cleanup sub-action now selectively removes `known_hosts` only if action-created, credentials embedded with `printf '%q'` for safe shell quoting, SSH key created with `install -m 600` (no permission race), verify step redacts by position not value |
| 2026-03-05 | v1.0.0 - Initial release with `chmod 600` keys, `chmod 700` wrapper script, credential redaction in verify step, `env:` masking for all secrets |
