# Setup Guide

Complete walkthrough for `cloudflare-tunnel-ssh-action` - from Cloudflare setup to real-world deploy workflows.

---

## How It Works

```
GitHub Actions ──SSH──► Cloudflare Access (service token check)
                              │
                    Cloudflare Tunnel (outbound from server)
                              │
                         server:22 (never exposed to the internet)
```

Your server connects **outbound** to Cloudflare - no open inbound ports, no exposed IP.

---

## Step 1 - Set Up a Cloudflare Tunnel

Install cloudflared on your server and create a tunnel:

```bash
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
  -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb
cloudflared tunnel login
cloudflared tunnel create my-tunnel
```

Create `/etc/cloudflared/config.yml`:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<your-tunnel-id>.json

ingress:
  - hostname: ssh.example.com
    service: ssh://localhost:22
  - service: http_status:404
```

Start the service:

```bash
cloudflared tunnel route dns my-tunnel ssh.example.com
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

---

## Step 2 - Create a Cloudflare Access Application

1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com) → **Access** → **Applications**
2. Click **Add an application** → **Self-hosted**
3. Set **Application domain** to `ssh.example.com`
4. Add a policy with **Action: Service Auth** (not "Allow") → select your service token

> **Important:** The policy action must be **Service Auth**. Using "Allow" causes a silent fallback to browser authentication, which fails in CI.

---

## Step 3 - Create a Service Token

1. Go to Zero Trust → **Access** → **Service Auth** → **Service Tokens**
2. Click **Create Service Token**
3. Copy the **Client ID** and **Client Secret** - you won't see the secret again

---

## Step 4 - Generate an SSH Key Pair

```bash
ssh-keygen -t ed25519 -C "github-actions@your-repo" -f ~/.ssh/github_actions_deploy -N ""
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub deploy-user@your-server
```

---

## Step 5 - Add GitHub Secrets

Go to your repository → **Settings** → **Secrets and variables** → **Actions**.

| Secret | Value |
|--------|-------|
| `CF_ACCESS_CLIENT_ID` | Service token Client ID |
| `CF_ACCESS_CLIENT_SECRET` | Service token Client Secret |
| `SSH_PRIVATE_KEY` | Full private key content (including `-----BEGIN/END-----` lines) |
| `SERVER_SSH_HOST` | Tunnel SSH hostname (e.g. `ssh.example.com`) |
| `DEPLOY_USER` | SSH username on the server |

> **Tip:** Use a GitHub **Environment** (e.g. `prod`) for secrets that need manual approval before deployment.

---

## Step 6 - Use the Action

```yaml
steps:
  - uses: NX1X/cloudflare-tunnel-ssh-action@v1
    with:
      cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
      cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
      ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-host:                ${{ secrets.SERVER_SSH_HOST }}

  - run: ssh deploy@${{ secrets.SERVER_SSH_HOST }} "echo connected"
```

To verify manually: go to **GitHub Actions** → **Test Action** → **Run workflow**.

---

## Input Variations

Pin a specific cloudflared version:
```yaml
cloudflared-version: '2025.4.0'
```

Use an RSA key:
```yaml
ssh-key-path: '~/.ssh/id_rsa'
```

Skip the built-in connection test:
```yaml
test-connection: 'false'
```

Pin the action for reproducibility:

| Style | Tag | Behavior |
|-------|-----|----------|
| Major | `@v1` | Auto-receives minor + patch updates (recommended) |
| Exact | `@v1.0.0` | Pinned, no automatic updates |
| SHA | `@abc1234` | Maximum reproducibility |

---

## Examples

### Basic Deploy

Sync files and restart a service.

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: NX1X/cloudflare-tunnel-ssh-action@v1
        with:
          cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
          cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
          ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
          ssh-host:                ${{ secrets.SERVER_SSH_HOST }}

      - name: Sync files
        env:
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: rsync -avz --delete --exclude='.git' ./ "deploy@${SERVER_HOST}:~/app/"

      - name: Restart
        env:
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: ssh "deploy@${SERVER_HOST}" "sudo systemctl restart myapp"
```

### Docker Compose Deploy

Sync, build, deploy containers, run migrations, health check.

```yaml
name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: actions/checkout@v4

      - uses: NX1X/cloudflare-tunnel-ssh-action@v1
        with:
          cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
          cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
          ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
          ssh-host:                ${{ secrets.SERVER_SSH_HOST }}
          ssh-user:                ${{ secrets.DEPLOY_USER }}

      - name: Copy files
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          rsync -avz --delete \
            --exclude='.git' --exclude='.env' --exclude='data' \
            ./ "${DEPLOY_USER}@${SERVER_HOST}:~/myapp/"

      - name: Deploy containers
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          ssh "${DEPLOY_USER}@${SERVER_HOST}" "cd ~/myapp && \
            docker compose pull && \
            docker compose up -d --force-recreate --remove-orphans && \
            docker image prune -f"

      - name: Health check
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          sleep 15
          ssh "${DEPLOY_USER}@${SERVER_HOST}" \
            "curl -sf http://localhost/health > /dev/null && echo 'OK'"
```

### Deploy with Rollback

Pre-deploy snapshot, deploy, verify, auto-rollback on failure.

```yaml
name: Deploy with Rollback
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: actions/checkout@v4

      - uses: NX1X/cloudflare-tunnel-ssh-action@v1
        with:
          cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
          cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
          ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
          ssh-host:                ${{ secrets.SERVER_SSH_HOST }}

      - name: Snapshot + Deploy
        id: deploy
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          ssh "${DEPLOY_USER}@${SERVER_HOST}" \
            "cd ~/app && cp docker-compose.yml docker-compose.yml.bak"
          rsync -avz --delete --exclude='.git' --exclude='data' \
            ./ "${DEPLOY_USER}@${SERVER_HOST}:~/app/"
          ssh "${DEPLOY_USER}@${SERVER_HOST}" \
            "cd ~/app && docker compose pull && docker compose up -d --force-recreate"

      - name: Verify
        timeout-minutes: 3
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          sleep 30
          ssh "${DEPLOY_USER}@${SERVER_HOST}" \
            "cd ~/app && docker compose ps | grep -q 'Up' && \
             curl -sf http://localhost/health > /dev/null && echo 'Verified'"

      - name: Rollback on failure
        if: failure() && steps.deploy.outcome == 'success'
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          ssh "${DEPLOY_USER}@${SERVER_HOST}" \
            "cd ~/app && mv docker-compose.yml.bak docker-compose.yml && \
             docker compose up -d --force-recreate && echo 'Rolled back'"
```

### Build, Test & Deploy Pipeline

Build in one job, deploy in another.

```yaml
name: Build, Test & Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci && npm test && npm run build
      - uses: actions/upload-artifact@v4
        with: { name: build, path: dist/ }

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: actions/download-artifact@v4
        with: { name: build, path: dist/ }

      - uses: NX1X/cloudflare-tunnel-ssh-action@v1
        with:
          cf-access-client-id:     ${{ secrets.CF_ACCESS_CLIENT_ID }}
          cf-access-client-secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
          ssh-private-key:         ${{ secrets.SSH_PRIVATE_KEY }}
          ssh-host:                ${{ secrets.SERVER_SSH_HOST }}

      - name: Deploy
        env:
          SERVER_HOST: ${{ secrets.SERVER_SSH_HOST }}
        run: |
          rsync -avz --delete dist/ "deploy@${SERVER_HOST}:~/app/public/"
          ssh "deploy@${SERVER_HOST}" "sudo nginx -s reload"
```

---

## Troubleshooting

### `A browser window should have opened at the following URL`

The service token was rejected:
1. Access policy action must be **Service Auth** (not "Allow")
2. Token must be attached to the policy and not expired
3. `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET` must be correct in GitHub Secrets

### `Permission denied (publickey)`

1. Public key must be in `~/.ssh/authorized_keys` on the server
2. `SSH_PRIVATE_KEY` must be the **private** key (starts with `-----BEGIN`)
3. No extra whitespace or newlines in the secret

### `Connection timed out`

1. Check `cloudflared` is running: `sudo systemctl status cloudflared`
2. Verify DNS for `ssh.example.com` points to the tunnel
3. Confirm `ssh-host` matches the hostname in `/etc/cloudflared/config.yml`

### `cloudflared: command not found`

This action only supports Ubuntu/Debian runners. Use `ubuntu-latest`, `ubuntu-22.04`, or `ubuntu-20.04`.

### SSH still fails after setup looks correct

Add verbose output: `ssh -v deploy@host "echo test"`
