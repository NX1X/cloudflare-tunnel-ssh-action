# Changelog

All notable changes to this action are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

_No unreleased changes._

---

## [1.0.0] - 2026-05-04

### Added
- Initial release - part of the NXTools Collection by NX1X (https://nx1xlab.dev/nxtools)
- Install `cloudflared` from GitHub releases (latest or pinned version)
- Write SSH private key with correct permissions (`chmod 600`)
- Create wrapper script embedding `TUNNEL_SERVICE_TOKEN_ID` / `TUNNEL_SERVICE_TOKEN_SECRET` at write-time (bypasses ProxyCommand subprocess env var propagation issue)
- Configure `~/.ssh/config` with ProxyCommand, `IdentityFile`, timeouts, and keep-alive settings
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
