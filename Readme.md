# K8s AI Support Platform

Production-oriented AI support platform built with:

- Next.js
- TypeScript
- Python
- FastAPI
- PostgreSQL
- Redis
- RabbitMQ
- Docker
- Kubernetes
- Helm
- Kustomize
- Argo CD
- Terraform
- Azure
- Azure OpenAI
- RAG

## Architecture

```text
Browser
   |
   v
Next.js
   |
   v
FastAPI API Gateway
   |
   +---- Auth Service
   |
   +---- Chat Service
   |
   +---- Ticket Service
   |
   +---- Worker
   |
   +---- PostgreSQL
   |
   +---- Redis


Project Goals
Build a complete web application.
Containerize all application components.
Deploy the platform on Kubernetes.
Implement Kubernetes security and reliability features.
Implement CI/CD and GitOps.
Add monitoring, logging and tracing.
Add LLM integration.
Add RAG capabilities.
Deploy the final platform on Azure AKS.
Environments
Development
Staging
Production   