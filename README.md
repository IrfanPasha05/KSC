# KSC Wholesale Chicken — Production Rebuild

A production-style rebuild of the existing KSC Wholesale Chicken Flask application.

## Architecture

Customer order → Flask → SQLite → Kafka event → notification worker → optional WhatsApp notification.

CI/CD: GitHub → GitHub Actions → tests/quality/security → Docker image → GHCR.

Runtime: Docker Compose locally or Kubernetes/Minikube.

## Stack

- Python + Flask
- SQLite with persistent storage
- Apache Kafka
- Docker / Docker Compose
- Kubernetes / Minikube
- GitHub Actions
- GitHub Container Registry
- Pytest, Ruff, Bandit, pip-audit
- Trivy filesystem and image scans
- Prometheus metrics
- Optional official Meta WhatsApp Cloud API

No AWS, PostgreSQL, Jenkins or Nexus.

## Local development

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python app.py
```

Or:

```bash
docker compose up --build
```

Open http://localhost:8000

## Kafka

Orders are stored in SQLite and published to:

`ksc.order.created`

The worker consumes that topic using consumer group:

`ksc-notification-worker`

## WhatsApp

WhatsApp is optional and disabled by default.

Set these only as environment variables or Kubernetes Secrets:

- WHATSAPP_ENABLED
- WHATSAPP_API_VERSION
- WHATSAPP_PHONE_NUMBER_ID
- WHATSAPP_ACCESS_TOKEN
- WHATSAPP_ADMIN_NUMBER

Never commit credentials.

## Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/ksc.yaml
kubectl apply -f k8s/worker.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl -n ksc get pods
kubectl -n ksc port-forward svc/ksc 8000:80
```

The application exposes:

- /healthz
- /readyz
- /metrics

SQLite is intentionally kept at one application replica because it is a single-file database. If the business later requires horizontal application scaling, move the state layer to a shared database.

## GitHub Actions

Pushes to `master` and `production-rebuild` run:

1. Ruff
2. Pytest
3. Bandit
4. pip-audit
5. Trivy filesystem scan
6. Docker build
7. Push to GHCR
8. Trivy image scan
