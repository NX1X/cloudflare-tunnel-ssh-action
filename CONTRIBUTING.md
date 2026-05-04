# Contributing to cloudflare-tunnel-ssh-action

Thanks for your interest in contributing! Here's how to get started.

## How to Contribute

1. **Found a bug?** [Open an issue](https://github.com/NX1X/cloudflare-tunnel-ssh-action/issues/new?template=bug_report.yml)
2. **Have an idea?** [Request a feature](https://github.com/NX1X/cloudflare-tunnel-ssh-action/issues/new?template=feature_request.yml) or check the [Roadmap](ROADMAP.md)
3. **Want to contribute code?** Fork the repo, make your changes, open a pull request

## Development Setup

```bash
# Clone the repo
git clone https://github.com/NX1X/cloudflare-tunnel-ssh-action.git
cd cloudflare-tunnel-ssh-action

# Install linting tools (optional, CI runs these automatically)
# actionlint: https://github.com/rhysd/actionlint
# shellcheck: https://github.com/koalaman/shellcheck
```

## Development Workflow

1. Create a branch from `main`
2. Make your changes to `action.yml` or workflows
3. Run quality checks locally (if tools are installed):
   ```bash
   actionlint
   shellcheck -x <(yq '.runs.steps[].run' action.yml)
   ```
4. Update `CHANGELOG.md` under the `[Unreleased]` section
5. Open a pull request

## Code Standards

- **Shell**: All `run:` blocks use `bash`
- **Linting**: Must pass `actionlint` and `shellcheck`
- **Secrets**: Always use `env:` blocks - never inline secrets in `run:` commands
- **Permissions**: SSH keys `chmod 600`, wrapper scripts `chmod 700`
- **Credentials**: Use `TUNNEL_SERVICE_TOKEN_ID` / `TUNNEL_SERVICE_TOKEN_SECRET` (the correct env var names for `cloudflared`)

## Changelog

- Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
- Categorize: Added, Changed, Deprecated, Removed, Fixed, Security
- Add entries under `[Unreleased]`

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add macOS runner support
fix: correct SSH key permissions on older runners
docs: update troubleshooting table
ci: upgrade actions/checkout to v4
```

## Pull Requests

- Fill out the PR template completely
- Reference any related issues
- Keep PRs focused - one fix or feature per PR
- All CI checks must pass before merge
