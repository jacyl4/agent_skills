---
name: python-app-deployment
description: Manages the deployment of Python applications, including research apps
  and web apps, using systemd services.
commands:
- python-research-app-deployment: Deploys Python research/demo apps from GitHub into
    a durable local app directory.
- python-webapp-systemd-deployment: Deploys Python web apps from source into a venv
    and manages them as systemd services.
maintainer_notes: 'This umbrella skill consolidates Python application deployment
  strategies, covering both research/demo applications and standard web applications.

  '
pinned: false
tags:
- python
- devops
- deployment
- webapp
- research
metadata:
  targets:
  - hermes
---

# Python Application Deployment

This skill provides strategies for deploying Python applications, covering research applications and web services.

## Research Application Deployment

### `python-research-app-deployment`

Deploys Python research/demo applications from GitHub into a durable local app directory. It ensures safe secret configuration, selection of minimal runnable benchmarks/demos, and verification of startup.

## Web Application Deployment

### `python-webapp-systemd-deployment`

Deploys Python web applications from source into a virtual environment (venv) and manages them as systemd services. This includes handling LAN binding and verification of the deployed service.
