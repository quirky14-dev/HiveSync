# CI/CD Pipeline Security  
_HiveSync – Phase 7_

## 1. Overview
HiveSync’s CI/CD pipeline handles source code, build artifacts, and deployment steps that directly affect:

- backend  
- workers  
- desktop app  
- mobile app  
- plugins  
- documentation  

This document defines the **security controls** required to operate the pipeline safely in real-world environments.

CI/CD is one of the most critical attack surfaces because a compromised pipeline can:

- inject malicious code  
- leak secrets  
- deploy backdoored images  
- expose user repositories  
- grant attackers lateral movement into infrastructure  

This file provides a hardened blueprint for secure automation.

---

# 2. Pipeline Threat Model

### 2.1 Assets at Risk

- Source code (backend, desktop, mobile, plugins)  
- Build artifacts (Docker images, installers, preview tooling)  
- Secrets (JWT secret, API keys, DB/Redis login, object storage creds)  
- Signing keys (optional future)  
- Deployment targets

### 2.2 Attackers

- External attackers exploiting misconfigured CI  
- Compromised contributor accounts  
- Malicious PRs  
- Pipeline supply-chain attacks  
- Credential leaks within logs or artifacts  

---

# 3. CI/CD Hardening Principles

1. **Least privilege**  
   Pipelines only have access to what each stage requires.

2. **Separation of duties**  
   Builds, tests, and deploys run in different contexts.

3. **No secrets in source code**  
   All secrets provided at runtime through secret manager.

4. **Immutable build artifacts**  
   Build once, run everywhere.

5. **Restricted branch-based deployments**  
   Production deployment requires protected branches + reviews.

6. **Transparent audits**  
   Every pipeline action must be logged.

---

# 4. Secrets Management in CI/CD

## 4.1 No Plaintext Secrets  
Secrets must not appear in:

- `.env` files committed to Git  
- Build logs  
- Test output  
- Repository history  

---

## 4.2 Use Secret Manager  
Supported:

- GitHub Actions Secrets  
- GitLab CI variables  
- Bitbucket secure variables  
- AWS/GCP/Kubernetes secret managers  

---

## 4.3 Secret Access Rules

- Build jobs may access only build-specific secrets  
- Deploy jobs may access deployment secrets  
- No job may access:
  - DB admin credentials  
  - full object storage admin keys  
  - worker-only or backend-only secrets  

---

## 4.4 Rotation  
Rotate:

- JWT secret  
- DB/Redis credentials  
- AI provider keys  
- preview token salt/secret  
- object storage credentials  

Recommended rotation: every **90 days** or after any incident.

---

# 5. Build Pipeline Hardening

## 5.1 Build Isolation  
Each pipeline step runs in:

- fresh VM  
- fresh container  
- ephemeral environment  

No cached secrets.

---

## 5.2 Dependency Pinning  
All dependencies must be pinned:

- Python → `poetry.lock`  
- Node → `package-lock.json`  
- Desktop/mobile packaging → locked versions  
- Plugins → locked dependencies  

---

## 5.3 Supply Chain Security  
Use:

- vulnerability scanning (Snyk, Trivy, Grype, etc.)  
- dependency auditing  
- container base image scanning  
- disallow unpinned dependencies  

---

## 5.4 Build Artifacts  
Artifacts must:

- be immutable  
- contain no secrets  
- exclude test data  
- exclude developer-specific files  
- include checksum/hash  

---

# 6. Testing Pipeline Hardening

## 6.1 Untrusted PR Handling  
PRs from forks must run in a **sandboxed** environment with:

- no secrets  
- no ability to publish images  
- no access to deployment systems  

---

## 6.2 Test Logs Redaction  
Logs may not include:

- preview tokens  
- JWTs  
- object storage paths  
- repo mirror paths  
- user-specific environment variables  

---

## 6.3 Strict Test Isolation  
Tests must not:

- perform real preview uploads  
- access production DB/Redis  
- hit object storage with real keys  
- clone real user repos  

Mock everything.

---

# 7. Deployment Pipeline Security

## 7.1 Protected Branches  
Production deploys require:

- merge into `main` or `release`  
- code review by authorized team members  
- passing tests  
- no failing security scans  

---

## 7.2 Artifact Promotion  
CI should use:

- build → test → promotion  
- NOT rebuild from source during deploy  
- checksum verification of promoted artifacts  
- no manual artifact modification  

---

## 7.3 Deployment Secrets  
Deployment job must access:

- DB credentials  
- object storage keys  
- AI provider keys  
- JWT_SECRET  
- Redis credentials  

But only for the **target environment**.

---

## 7.4 Rollback Strategy  
Requirements:

- safe rollback of Docker images  
- rollback of DB migrations (where possible)  
- cleanup of partially-applied deploys  
- fast path to restore preview worker nodes  

Documentation of rollback included in deployment bible.

---

# 8. Desktop & Mobile Build Security

## 8.1 Desktop Build Hardening  
Desktop installers must:

- be code-signed  
- not include embedded secrets  
- use reproducible packaging when possible  
- not allow downgrade attacks (optional future requirement)  

---

## 8.2 Mobile Build Hardening  
Mobile preview app:

- shipped through App Store / Play Store  
- no debug flags in production builds  
- code obfuscation for Android  
- secure entitlements for iOS  
- certificate pinning optional  

---

# 9. Plugin Build Security

- Plugins must not bundle secrets  
- Plugin ZIPs must be reproducible  
- SHA256 or similar should verify plugin artifact consistency  
- Only approved build system may publish plugins  

---

# 10. Pipeline Monitoring & Alerts

Monitor:

- unusual pipeline job patterns  
- repeated pipeline failures  
- unsigned artifacts  
- failed attempts to access protected secrets  
- abnormal deploy volume  

Alert on:

- unauthorized environment variable access  
- unusual preview bundle build times  
- pipeline container outbound network anomalies  
- attempts to modify pipeline configuration  

---

# 11. Audit Logging of CI/CD

CI/CD pipeline actions must log:

- who triggered the run  
- branch, commit hash  
- job start/end times  
- secrets accessed (names ONLY, not values)  
- artifact hashes  
- promotion steps  
- deploy outcomes  
- rollback events  

Logs must be forwarded to centralized log system.

---

# 12. Recommended CI/CD Stack

Examples of secure CI/CD stacks:

- **GitHub Actions + OIDC + AWS/GCP/K8s**  
- **GitLab CI + built-in Vault + Runner groups**  
- **Bitbucket Pipelines + KMS + Container Registry**

Optional enhancements:

- Cosign / Sigstore  
- Trivy vulnerability checks  
- OPA/Gatekeeper policy enforcement  
- Canary deployments  

---

# 13. Cross-References

- backend_security_hardening.md  
- client_security_hardening.md  
- storage_and_repository_security.md  
- monitoring_and_alerts.md  
- audit_logging.md  
- deployment bible (Phase 7 cross-link)
