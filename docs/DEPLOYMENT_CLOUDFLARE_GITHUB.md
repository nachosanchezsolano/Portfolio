# Production deployment with GitHub and Cloudflare (legacy alternative)

> La API actual está preparada para Cloudflare Workers + Workers AI + Vectorize.
> Para el flujo recomendado, usar [DEPLOYMENT_CLOUDFLARE_WORKERS.md](DEPLOYMENT_CLOUDFLARE_WORKERS.md).
> Este documento conserva una alternativa de frontend en Pages y API Dockerizada.

This guide covers the current repository state:

- Frontend: Astro under `apps/web`.
- API: Dockerized FastAPI under `api`.
- Source control: GitHub.
- Edge, DNS, TLS, and protection: Cloudflare.

## Recommended topology

For the first production release:

```text
GitHub repository
       │
       ├── Cloudflare Pages → portfolio.example.com
       │
       └── Railway API       → api.example.com
                         ▲
                         │
                    Cloudflare DNS
```

This keeps the current FastAPI Docker deployment intact while Cloudflare handles the public web experience, DNS, TLS, caching, and edge protection.

Cloudflare Pages supports GitHub integration, automatic deployments, preview deployments, and build status checks. ([Cloudflare Pages Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/))

## 1. Prepare the repository

Run commands from the project directory:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform"
git status
rg --files -g '!node_modules' -g '!dist' -g '!.astro'
```

Before publishing, confirm that the repository has no:

- `.env` files with real values.
- API keys.
- Private vault content.
- Personal documents.
- Database dumps.
- Build artifacts.

Review `knowledge-base/` manually. The current `.gitignore` excludes environment files, secrets, private data, dependencies, and build artifacts, but it does not replace a manual review.

Build locally:

```powershell
cd apps\web
npm ci
npm run build

cd ..\..\api
python -m pytest

cd ..
docker compose -f docker-compose.dev.yml up --build
```

## 2. Create and push the GitHub repository

Create an empty GitHub repository. Do not add a README, `.gitignore`, or license if those files already exist locally.

Then, from `portfolio-platform`:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "chore: establish portfolio engine foundation"
git remote add origin https://github.com/YOUR_USERNAME/ai-portfolio-engine.git
git push -u origin main
```

Replace the username and repository name.

After the first push, configure protection for `main`:

- Require pull requests.
- Require a successful build check.
- Block force pushes.
- Block branch deletion.

## 3. Deploy the frontend to Cloudflare Pages

In Cloudflare Dashboard:

1. Open **Workers & Pages**.
2. Select **Create application**.
3. Select **Pages**.
4. Select **Import an existing Git repository**.
5. Authorize GitHub and choose `ai-portfolio-engine`.
6. Configure the build:

```text
Production branch: main
Root directory: apps/web
Build command: npm run build
Build output directory: dist
Node version: 22
```

Cloudflare Pages automatically deploys new commits and creates preview deployments for branches and pull requests. ([Astro on Cloudflare Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-an-astro-site/), [Pages build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/))

Configure these variables in the Pages project:

```text
PUBLIC_API_URL=https://api.example.com
PUBLIC_LINKEDIN_URL=https://www.linkedin.com/in/your-profile
PUBLIC_GITHUB_URL=https://github.com/your-username
```

Configure Preview and Production separately. Preview should point to a staging API, not the production API.

Add the custom domain from **Custom domains**:

```text
portfolio.example.com
```

## 4. Deploy the FastAPI API

The current API already has a Dockerfile that listens on the injected `PORT` and exposes `/health`. Deploy it as a separate service connected to the same GitHub repository.

Configure the backend service:

```text
Dockerfile path: api/Dockerfile
Build context: api
Healthcheck path: /health
```

Production variables:

```text
APP_ENV=production
ALLOWED_ORIGINS=https://portfolio.example.com
API_KEY=<generated-value-if-enabled>
OPENROUTER_API_KEY=<secret>
```

Keep runtime secrets in the hosting provider's secret manager. Do not put them in GitHub files or commit them. ([GitHub Actions secrets](https://docs.github.com/en/actions/concepts/security/secrets))

Verify the backend:

```powershell
curl https://api.example.com/health
```

Expected response:

```json
{"status":"ok"}
```

## 5. Put the API behind Cloudflare

Add a proxied DNS record:

```text
Type: CNAME
Name: api
Target: YOUR-API-HOST.example-host.com
Proxy: Proxied
TTL: Auto
```

Cloudflare supports proxied CNAME records and recommends proxying web traffic so requests pass through its network. ([Cloudflare DNS records](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/), [Cloudflare proxy status](https://developers.cloudflare.com/dns/proxy-status/))

Configure:

```text
SSL/TLS mode: Full (strict), when the origin has a valid certificate
Always Use HTTPS: On
```

Use `https://api.example.com` in the frontend, never the provider's origin hostname.

## 6. Production security checklist

Before opening the site publicly:

- Restrict CORS to the production frontend origin.
- Keep `/docs` and `/redoc` private or disabled until authentication exists.
- Use distributed rate limiting before horizontal scaling.
- Add request IDs and structured logs.
- Set request and message size limits.
- Configure provider timeouts and bounded retries.
- Never expose private documents through public retrieval.
- Verify webhook signatures before processing events.
- Return generic errors for unexpected exceptions.
- Rotate provider keys if they are exposed.

## 7. Deployment flow

```text
Feature branch
      ↓
Pull request
      ↓
Cloudflare preview deployment
      ↓
Tests and review
      ↓
Merge into main
      ↓
Production frontend deployment
      ↓
Production API deployment
```

Cloudflare's Git integration is enough for the first frontend release. GitHub Actions should initially run validation:

```text
pull_request:
  frontend build
  API tests
  secret scan
```

Do not add deployment secrets to GitHub Actions until a workflow needs them.

## 8. All-Cloudflare alternative

Cloudflare now documents FastAPI support in Python Workers through an ASGI adapter. This is a different runtime from the current Docker/Uvicorn deployment: it requires a Python Worker entrypoint, `pyproject.toml`, `pywrangler`, and Worker configuration. ([FastAPI on Cloudflare Workers](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/), [Python Workers](https://developers.cloudflare.com/workers/languages/python/))

Treat this as a second milestone:

1. Keep domain and application layers free of Uvicorn and filesystem assumptions.
2. Add a Worker entrypoint adapting FastAPI to ASGI.
3. Replace the container deployment configuration with `pyproject.toml` and `pywrangler`.
4. Test database connectivity and provider HTTP calls in the Worker runtime.
5. Deploy a staging Worker.
6. Run contract and end-to-end tests.
7. Switch `api.example.com` only after staging passes.

Do not combine this runtime migration with the first GitHub and Cloudflare release.

## 9. Smoke tests

Verify:

```text
GET  https://portfolio.example.com
GET  https://api.example.com/health
POST https://api.example.com/v1/chat
```

Also check:

- No `localhost` appears in the production bundle.
- The frontend contains no secrets.
- HTTPS works on both domains.
- Browser requests do not fail due to CORS.
- Invalid API keys are rejected when enabled.
- Rate limiting returns `429` after the threshold.
- Preview deployments do not modify production data.
- Logs do not expose prompts, keys, or private content.

## 10. Rollback

Keep the previous deployments available. If a release fails:

1. Roll back the frontend to the previous Pages deployment.
2. Roll back or redeploy the previous API image.
3. Check database migration compatibility.
4. Restore traffic.
5. Record the incident and corrective action.
