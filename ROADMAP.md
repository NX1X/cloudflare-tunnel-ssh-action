# Roadmap

Planned features for `cloudflare-tunnel-ssh-action`.

Community votes and contributions are welcome - [open an issue](https://github.com/NX1X/cloudflare-tunnel-ssh-action/issues/new) or PR!

---

## Planned

- [ ] **macOS runner support** - install via Homebrew
- [ ] **ARM64 runner support** - use `cloudflared-linux-arm64.deb` on ARM runners
- [ ] **Windows runner support** - install via `winget` or direct `.msi`
- [ ] **Known hosts verification** - optional `ssh-keyscan` + `known-hosts` input for strict host key checking
- [ ] **Multiple SSH hosts** - configure more than one tunnel hostname in a single action call
- [ ] **SSH agent support** - add the key to `ssh-agent` for agent forwarding and nested git operations
- [ ] **Port forwarding mode** - `port-forward` input to open a background tunnel for database access, HTTP tunnels, etc.
- [ ] **Outputs** - expose cloudflared version, key fingerprint, and connection status for downstream steps
- [ ] **Proxy-only mode** - configure ProxyCommand without installing an SSH key, for use with other key management actions
- [ ] **Mutual TLS (mTLS) support** - for organizations using mTLS in addition to service tokens
- [ ] **Audit log step** - optional post-step that logs the connection event to a webhook or SIEM

---

## Completed

- [x] Install `cloudflared` (latest or pinned version)
- [x] Write SSH private key with correct permissions (`600`)
- [x] Wrapper script with embedded service token credentials (`chmod 700`)
- [x] SSH config with ProxyCommand, timeouts, keep-alive
- [x] Verify step with redacted output
- [x] Optional connection test
- [x] CI workflow with `actionlint` + `shellcheck`
- [x] Manual release workflow with floating major version tag
