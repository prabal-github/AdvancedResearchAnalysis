# Deployment & Future Update Strategy

This document outlines how to deploy the application to AWS and evolve it safely with new features without risking existing client data.

## 1. Repository Preparation
- Remove secrets from code. Use environment variables (store locally in `.env`, not committed).
- Ensure `requirements.txt` is current.
- Add `Dockerfile` or Elastic Beanstalk config (Procfile) depending on chosen path.
- Add `.gitignore` (exclude virtualenv, `instance/`, `__pycache__/`, local SQLite files, `.env`).
- Provide `README.md` with setup, environment variables, and migration commands.

## 2. Migrations (Mandatory Before Production)
Use Alembic / Flask-Migrate:
1. `pip install flask-migrate alembic`
2. Integrate Flask-Migrate (init in `app.py` or a `wsgi.py`).
3. Baseline: `flask db init` → `flask db migrate -m "baseline"` → `flask db upgrade`.
4. Commit the `migrations/` directory.
Rule: All schema changes through migrations. Avoid ad‑hoc production DDL.

### Migration Best Practices
| Change Type | Safe Pattern |
|-------------|--------------|
| Add column  | Add nullable (or with default) → backfill → enforce NOT NULL later |
| Rename      | Add new column → copy data → switch code → drop old column later |
| Drop column | Only after code no longer references it & backups verified |
| Large index | PostgreSQL: create concurrently in separate migration |

## 3. AWS Architecture Options
| Option | Components | When to Use |
|--------|------------|------------|
| A: Elastic Beanstalk | EB (Python), RDS (Postgres), S3, (CloudFront optional) | Fast start without containers |
| B: ECS Fargate | ECS + ALB + RDS + S3 | Container workflow & scaling |
| C: EC2 + Nginx | EC2 autoscaling group, RDS, S3 | Full control / legacy style |

Recommendation: Start with Elastic Beanstalk or ECS Fargate for managed deployment + health checks.

## 4. Environments
- `dev`, `staging`, `prod` (separate RDS instances ideally; minimum separate DBs).
- Feature branches may deploy to ephemeral staging (optional nice‑to‑have).

## 5. Configuration & Secrets Management
Use either:
- AWS Systems Manager Parameter Store (simple) or
- AWS Secrets Manager (rotation, audit) for: `DATABASE_URL`, `SECRET_KEY`, API keys.
Never commit secrets. Map them to environment variables in task definitions or EB config.

## 6. User Uploads & Static Assets
- Store user uploads in S3 (bucket with versioning ON).
- Migrate existing local files (one‑time sync: `aws s3 sync`).
- Serve via CloudFront (optional) for performance + HTTPS.

## 7. Backups & Disaster Recovery
| Asset | Mechanism | Frequency |
|-------|-----------|-----------|
| RDS   | Automated backups + snapshots | Daily + pre‑deploy snapshot |
| Logical DB dump | `pg_dump` / `mysqldump` to S3 | Weekly |
| S3 uploads | Versioning + lifecycle rules | Continuous |
| Config (IaC) | Git (Terraform/CloudFormation) | Per change |

Test a restore quarterly: create staging from snapshot.

## 8. CI/CD Pipeline (GitHub Actions Example)
Workflow per push to `main`:
1. Lint & test.
2. Build Docker image (tag: `app:<semver>-<shortsha>`).
3. Push to ECR.
4. Deploy to staging (update service / EB env).
5. Run DB migrations (staging) + smoke tests (`/healthz`, sample API call, simple booking flow mock).
6. Manual approval gate.
7. Pre‑prod snapshot (RDS) then run migrations (prod) in a dedicated migration task.
8. Blue/Green or rolling production deploy.
9. Post‑deploy canary tests (latency, 5xx, critical flows).
10. Notify success/failure (Slack / email).

## 9. Zero / Low Downtime Strategies
- Blue/Green: maintain old environment until new passes health → swap CNAME (EB) or shift ALB target group (ECS).
- Backward-compatible migrations first; cleanup migrations later.
- Avoid long locks: break large updates into batches, use `CREATE INDEX CONCURRENTLY` (Postgres).

## 10. Data Safety Principles
1. All destructive operations require:
   - Recent snapshot.
   - Verified migration rehearsal in staging with snapshot copy.
2. Instrument integrity checks (counts, null anomalies) via nightly script.
3. Feature rollout uses flags—no immediate irreversible schema usage.

## 11. Monitoring & Observability
| Layer | Tool | Key Metrics |
|-------|------|-------------|
| Logs  | CloudWatch Logs | Error rate, stack traces |
| Infra | CloudWatch Metrics | CPU, memory, DB connections, latency |
| App   | Health endpoint `/healthz` | 200 + version, DB ping |
| Alerts| CloudWatch Alarms | 5xx spike, latency p95, low free storage |

Add structured logging (JSON) for easier search.

## 12. Versioning & Releases
- Semantic Versioning: `MAJOR.MINOR.PATCH`.
- Add `/meta` or `/healthz` returning `version` + `git_sha`.
- Deprecate API fields gradually: support old + new for a period, log usage of old.

## 13. Feature Flags
Simple schema:
```sql
feature_flags(id serial, name text unique, enabled boolean, rollout_percentage int null, metadata jsonb null);
```
Access pattern: cache in memory; refresh every N minutes or on admin toggle.
Remove stale flags once fully rolled out.

## 14. Rollback Playbook
| Scenario | Response |
|----------|----------|
| App bug (no schema change) | Redeploy previous image tag |
| Bad forward-compatible migration | Roll forward with fix migration |
| Destructive migration gone wrong | Restore snapshot → reapply good migrations → fix root cause |

Avoid down migrations in prod; forward fixes are safer.

## 15. Security
- HTTPS (ACM cert) fronted by ALB / CloudFront.
- IAM least privilege: app task role limited to S3 bucket + Parameter Store nodes.
- Regular secret rotation (quarterly or on incident).
- Enable DB encryption at rest and S3 encryption (SSE-S3 or SSE-KMS).
- WAF for basic shielding (optional early, recommended later).

## 16. Scalability & Performance
- Gunicorn workers: ~2–4 × vCPU (measure real load).
- Add Redis/ElastiCache if session state or caching becomes heavy.
- DB connection pooling (SQLAlchemy pool size + overflow limits). Possibly PgBouncer later.
- Profile slow queries (RDS Performance Insights) → add indexes carefully.

## 17. Operational Routines
| Cadence | Task |
|---------|------|
| Daily   | Check error dashboard, alarm status |
| Weekly  | Review slow queries; verify backups succeeded |
| Monthly | Restore drill (staging), rotate minor credentials |
| Quarterly | Load test baseline; security review |

## 18. Example Environment Variables
```
FLASK_ENV=production
SECRET_KEY=********
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
LOG_LEVEL=INFO
S3_BUCKET=your-bucket
AWS_REGION=ap-south-1
SESSION_COOKIE_SECURE=1
```

## 19. Introducing Migrations Now (If Absent)
1. Add Flask-Migrate initialization:
```python
from flask_migrate import Migrate
migrate = Migrate(app, db)
```
2. Provide manage script or use `flask` CLI with `FLASK_APP=app.py`.
3. Baseline migration then commit.

## 20. Documentation & Change Tracking
- Maintain `CHANGELOG.md` (date, version, highlights, migration notes).
- Keep this strategy file updated as architecture evolves.
- Add `DEPLOYMENT.md` with step-by-step provisioning (RDS creation, S3 bucket policies, EB/ECS config).

## 21. Future Enhancements
- Infrastructure as Code (Terraform / CloudFormation) for reproducible environments.
- Canary releases (weighted target groups) for progressive delivery.
- Automated data quality dashboard (row counts, anomaly detection).
- Chaos testing (resilience) once stable.

## Quick Start Summary
1. Add migrations + remove secrets.
2. Choose AWS path (EB quickest).
3. Provision RDS + S3 + environment.
4. Configure CI/CD (build → test → stage → migrate → prod deploy).
5. Enable backups & alarms.
6. Use flags for new features; follow safe migration patterns.

---
This document is the living guide for safely deploying and evolving the platform without compromising existing client data.
