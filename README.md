# cloudflare-tunnel-ssh-action

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Cloudflare%20Tunnel%20SSH-blue?logo=github)](https://github.com/marketplace/actions/cloudflare-tunnel-ssh-setup)
[![Latest Release](https://img.shields.io/github/v/release/NX1X/cloudflare-tunnel-ssh-action?label=version&color=brightgreen)](https://github.com/NX1X/cloudflare-tunnel-ssh-action/releases/latest)
[![CI](https://github.com/NX1X/cloudflare-tunnel-ssh-action/actions/workflows/ci.yml/badge.svg)](https://github.com/NX1X/cloudflare-tunnel-ssh-action/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![NXTools](https://img.shields.io/badge/NXTools-Collection-orange)](https://nx1xlab.dev/nxtools)
![Views](https://komarev.com/ghpvc/?username=NX1X-cloudflare-tunnel-ssh-action&label=views&color=f66a0a)

Install `cloudflared` and configure SSH to connect through a **Cloudflare Tunnel** using a service token - zero-trust CI/CD access without exposing port 22 to the internet.

Part of the [NXTools Collection](https://nx1xlab.dev/nxtools) by [NX1X](https://github.com/NX1X).

---

## Quick Start

```yaml
steps:
  - uses: NX1X/cloudflare-tunnel-ssh-action@v1
    with:
      cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
      cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
      ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-host:                ssh.example.com

  - name: Deploy
    run: ssh deploy@ssh.example.com "cd ~/app && docker compose up -d"
```

After the action runs, `ssh`, `rsync`, `scp`, and `sftp` all work in every subsequent step - no wrapper, no per-command setup.

New to this? See the **[Setup Guide](GUIDE.md)** for a complete walkthrough.

---

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `cf-access-client-id` | **yes** | - | Cloudflare Access service token ID |
| `cf-access-client-secret` | **yes** | - | Cloudflare Access service token secret |
| `ssh-private-key` | **yes** | - | SSH private key (Ed25519 or RSA) |
| `ssh-host` | **yes** | - | SSH hostname(s) through the tunnel. Space/newline-separated. Use `user@host` to override user per host. |
| `ssh-user` | no | `deploy` | SSH username (default for all hosts unless overridden with `user@host`) |
| `cloudflared-version` | no | `latest` | Pin a specific cloudflared release (e.g. `2025.4.0`) |
| `ssh-key-path` | no | `~/.ssh/id_ed25519` | Path to write the SSH private key |
| `connect-timeout` | no | `120` | SSH `ConnectTimeout` in seconds |
| `server-alive-interval` | no | `30` | SSH `ServerAliveInterval` in seconds |
| `test-connection` | no | `true` | Run a test SSH command after setup to verify the tunnel |
| `known-hosts` | no | `''` | Known hosts entries for strict host key checking |
| `ssh-extra-config` | no | `''` | Additional SSH config directives per host (one per line) |
| `retry-count` | no | `3` | Number of SSH connection test attempts |
| `retry-delay` | no | `5` | Seconds between retry attempts |

---

## Outputs

| Output | Description |
|--------|-------------|
| `cloudflared-version` | Installed cloudflared version (e.g. `2025.4.0`) |
| `connection-test-result` | `success`, `failed`, or `skipped` |

---

## Multiple Hosts

Connect to several servers in a single action step:

```yaml
- uses: NX1X/cloudflare-tunnel-ssh-action@v1
  with:
    cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
    cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
    ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
    ssh-host: 'web.example.com admin@db.example.com staging.example.com'
    ssh-user: deploy

# All hosts are now reachable
- run: ssh deploy@web.example.com "systemctl restart app"
- run: ssh admin@db.example.com "pg_dump mydb > /tmp/backup.sql"
```

---

## Cleanup

Remove SSH keys, config entries, and the wrapper script after your job completes:

```yaml
- uses: NX1X/cloudflare-tunnel-ssh-action/cleanup@v1
  if: always()
```

Optional: also uninstall cloudflared:

```yaml
- uses: NX1X/cloudflare-tunnel-ssh-action/cleanup@v1
  if: always()
  with:
    remove-cloudflared: 'true'
```

---

## Supported Runners

Ubuntu/Debian only (installs `cloudflared` via `.deb` package):

- `ubuntu-latest` (Ubuntu 24.04)
- `ubuntu-22.04`
- `ubuntu-20.04`

---

## Documentation

- **[Setup Guide & Examples](GUIDE.md)** - full walkthrough, real-world workflows, and troubleshooting
- **[Roadmap](ROADMAP.md)** - planned features
- **[Changelog](CHANGELOG.md)** - version history
- **[Security](SECURITY.md)** - vulnerability reporting and security practices
- **[Contributing](CONTRIBUTING.md)** - how to contribute

---

## Privacy

This action collects no data. No telemetry, no analytics, no external calls. All processing happens on your GitHub Actions runner. The source is fully open - read every line in [`action.yml`](action.yml).

---

## License

[Apache 2.0](LICENSE) - © 2026 [NX1X](https://github.com/NX1X)
