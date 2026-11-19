# BazarBariOnline documentation

| File | What it is |
| --- | --- |
| [claude.md](claude.md) | Main specification v2 (sections 0–21): decisions, architecture, domains, roadmap |
| [audit/phase-0.md](audit/phase-0.md) | Phase 0 audit of the current code (19 Nov 2026): findings H1–H5, gaps, revised module register; §7 re-check of what is fixed, §7.1 after the Steadfast merge |
| [adr/](adr/README.md) | Architecture Decision Records 01–10 |
| [modules/](modules/README.md) | One-page spec for each of the 16 MVP modules |
| [permissions.md](permissions.md) | Permission catalogue (spec §6.4): 45 `module.action` permissions, platform and vendor role matrices, mapping from today's seeded permissions |
| [openapi.yaml](openapi.yaml) | OpenAPI 3.1 (spec §10.3): every implemented route (105, incl. the Steadfast admin endpoints and webhook) plus the planned `/api/v1/...` MVP endpoints, with permission, tenant scope, rate limit, audit event and known issues |
| [security/steadfast.md](security/steadfast.md) | Steadfast courier security plan (Bangla): 13-item checklist, all built and merged; webhook auth answer; package decision |
| [runbooks/](runbooks/README.md) | Runbooks (spec §15.3): database restore, file restore, full redeploy, credential rotation, failed migration, hosting outage |
| [tools/gen_openapi.py](tools/gen_openapi.py) | Script that regenerates `openapi.yaml` from the route list |

## Regenerating openapi.yaml

Run after any route change (needs Python 3 with PyYAML):

```bash
cd laravel-ecommerce
php artisan route:list --path=api --json > ../documentation/tools/routes.json
cd ../documentation
python tools/gen_openapi.py tools/routes.json openapi.yaml
```

Endpoint descriptions, known issues and the planned v1 list live in the script; update them there, not in the YAML.

## Still to be written

- `config/permissions.php` and `config/roles.php` in the backend, generated from [permissions.md](permissions.md) — Phase 1 code, not documentation.
- `runbooks/incident-log.md` — created on the first incident or restore test.
