# Changelog

All notable changes to this action are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- SSH connection retry logic: `retry-count` (default: 3) and `retry-delay` (default: 5) inputs for resilient connection testing
- Known hosts support: `known-hosts` input enables `StrictHostKeyChecking yes` for strict host key verification
- Multiple hosts: `ssh-host` now accepts space/newline-separated list with optional `user@host` syntax for per-host user override
- Custom SSH config: `ssh-extra-config` input appends additional directives (e.g. `ForwardAgent yes`) to each Host block
- Cleanup sub-action: `NX1X/cloudflare-tunnel-ssh-action/cleanup@v1` removes SSH keys, wrapper script, config entries, and known_hosts after job completion
- Connection status outputs: `cloudflared-version` and `connection-test-result` for use in downstream steps
- `User` directive in SSH config Host blocks (set per-host via `user@host` or from `ssh-user` input)
- State file (`~/.cloudflared-ssh-state`) for cleanup action coordination
- Unit test workflow (`unit-tests.yml`) covering version validation, URL construction, file permissions, wrapper script injection safety, SSH config generation, credential redaction, and verify step diagnostics

### Changed
- License changed from MIT to Apache License 2.0 (applies retroactively to all versions)
- Replaced all em dashes with standard hyphens across docs, workflows, and action.yml (history rewritten)

### Security
- Changed `StrictHostKeyChecking` default from `no` to `accept-new` when no `known-hosts` are provided (prevents MITM on repeated connections)
- Added input validation for `connect-timeout` and `server-alive-interval` (must be non-negative integers)
- Disabled shell glob expansion (`set -f`) before unquoted word-splitting loops over host lists (prevents unexpected filename expansion)
- Changed `grep` to `grep -F` (fixed string) in verify step to prevent hostname regex interpretation
- Cleanup sub-action now only removes `~/.ssh/known_hosts` if the action created it (preserves pre-existing entries from other steps)
- All new inputs (`known-hosts`, `ssh-extra-config`, `retry-count`, `retry-delay`) routed through `env:` blocks -- no `${{ inputs.* }}` in `run:` blocks
- SSH private key created with `install -m 600` before writing content (no permission race window)
- Wrapper script credentials embedded with `printf '%q'` for safe shell quoting (handles special characters in tokens)
- Verify step redacts credentials by position (`sed 's/=.*/=<REDACTED>/'`) rather than by value (avoids regex/delimiter issues with secret content)

---

## [1.0.0] - 2026-05-04

### Added
- Initial release - part of the NXTools Collection by NX1X (https://nx1xlab.dev/nxtools)
- Install `cloudflared` from GitHub releases (latest or pinned version)
- Write SSH private key with correct permissions (`chmod 600`)
- Create wrapper script embedding `TUNNEL_SERVICE_TOKEN_ID` / `TUNNEL_SERVICE_TOKEN_SECRET` at write-time (bypasses ProxyCommand subprocess env var propagation issue)
- Configure `~/.ssh/config` with ProxyCommand, timeouts, and keep-alive settings
- Verify step: print cloudflared version, key fingerprint, redacted wrapper script, SSH config entry
- Optional connection test (`test-connection: true` by default)
- Inputs: `cf-access-client-id`, `cf-access-client-secret`, `ssh-private-key`, `ssh-host`, `ssh-user`, `cloudflared-version`, `ssh-key-path`, `connect-timeout`, `server-alive-interval`, `test-connection`
- Manual release workflow (`workflow_dispatch`) with version validation, duplicate tag check, and floating major version tag
- CI workflow with pinned `actionlint` (v1.7.7) and `shellcheck`
- Dependabot for GitHub Actions version updates

### Security
- All `${{ inputs.* }}` and `${{ steps.*.outputs.* }}` expressions in shell scripts routed through `env:` blocks to prevent script injection
- Input validation for `cloudflared-version` - rejects values that don't match `latest` or `X.Y.Z` format
- `softprops/action-gh-release` pinned to commit SHA to prevent supply chain attacks
- Explicit `permissions` blocks on all workflows (least-privilege `contents: read`)
- Credentials redacted in verify step output via `sed`
- Documentation examples use `env:` blocks instead of direct `${{ secrets.* }}` in `run:` blocks
