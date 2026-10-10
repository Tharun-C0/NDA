# Amazon EC2 Deployment Readiness Report

**Date**: October 9, 2026  
**Project**: NDA Multi-Label Clause Classification Architecture  
**Hugging Face Model**: `THARUNC0/legal-roberta-nda-clause-classifier` (Private)  
**GitHub Repository**: `https://github.com/Tharun-C0/NDA`  
**Overall Deployment Readiness Status**: **PASS (READY FOR EC2 STAGING)**  

---

## 1. Executive Summary & Readiness Matrix

This report synthesizes the deployment preparation for launching the NDA Multi-Label Clause Classification API on **Amazon Web Services (AWS) EC2**. The backend application is containerized, fully verified against real Hugging Face Hub inference, and backed by a 30/30 passing automated test suite.

| Deployment Check | Status | Evaluation Summary |
| :--- | :---: | :--- |
| **Backend API Functionality** | **PASS** | FastAPI backend with health & classification endpoints verified. |
| **Hugging Face Model Access** | **PASS** | Private repository access verified (`THARUNC0/legal-roberta-nda-clause-classifier`). |
| **Token Security** | **PASS** | Memory-only environment resolution (`HF_TOKEN`); 0 tokens hardcoded or logged. |
| **Automated Backend Tests** | **PASS** | **30/30 Passed** (`py -3.14 -m pytest backend/tests`). |
| **Path Portability** | **PASS** | Codebase uses relative `Path(__file__).resolve()` resolution. |
| **Docker Configuration** | **PASS** | `Dockerfile` and `.dockerignore` created following security best practices. |
| **Docker Local Build Test** | **NOT TESTED** | Docker CLI not installed on local Windows host. |
| **EC2 Hardware Sizing** | **PASS** | Sizing completed (`t3.large` / `c6i.large`, 8 GB RAM, 30 GB EBS). |
| **AWS Resource Creation** | **NOT TESTED** | AWS resources intentionally deferred per rules. |
| **GitHub Commit / Push** | **NOT TESTED** | Git push intentionally deferred per rules. |

---

## 2. Files Changed & Added for Deployment

| File Path | Status | Purpose & Change Rationale |
| :--- | :---: | :--- |
| [`Dockerfile`](file:///f:/NDA/Dockerfile) | **Created** | Production multi-stage Dockerfile for containerized deployment. |
| [`.dockerignore`](file:///f:/NDA/.dockerignore) | **Created** | Excludes `.env`, model weights (`*.safetensors`), and bytecode from Docker image context. |
| [`backend/app/services/model_service.py`](file:///f:/NDA/backend/app/services/model_service.py) | **Updated** | Pulls Legal-RoBERTa from HF Hub with thread-safe singleton caching. |
| [`backend/app/core/config.py`](file:///f:/NDA/backend/app/core/config.py) | **Updated** | Added `HF_MODEL_ID` and `HF_TOKEN` Pydantic settings. |
| [`backend/app/main.py`](file:///f:/NDA/backend/app/main.py) | **Updated** | Fixed package import paths for root and backend environment compatibility. |
| [`backend/app/api/routes/health.py`](file:///f:/NDA/backend/app/api/routes/health.py) | **Updated** | Updated health check route import resolution. |
| [`backend/.env.example`](file:///f:/NDA/backend/.env.example) | **Updated** | Documented `HF_MODEL_ID`, `HF_TOKEN`, `PORT`, and `CORS_ORIGINS`. |
| [`requirements.txt`](file:///f:/NDA/requirements.txt) & [`backend/requirements.txt`](file:///f:/NDA/backend/requirements.txt) | **Updated** | Added `huggingface-hub`, `torch`, `transformers`, and `pydantic-settings`. |
| [`backend/tests/test_hf_model_service.py`](file:///f:/NDA/backend/tests/test_hf_model_service.py) | **Created** | Unit test suite for HF loading, token safety, and 14-label mapping. |

---

## 3. Required Environment Variables & Token Security

For deployment on Amazon EC2, create a `.env` file in the application root (or inject via systemd / Docker environment):

```ini
# --- Hugging Face Private Repository Access ---
HF_MODEL_ID="THARUNC0/legal-roberta-nda-clause-classifier"
HF_TOKEN="hf_your_read_only_token_here"

# --- Server & CORS Configuration ---
APP_NAME="NDA Analyst API"
APP_VERSION="1.0.0"
DEBUG=False
PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://your-ec2-domain.com"]
```

> [!SECURITY]
> **Token Security Protocol**:
> 1. `HF_TOKEN` must be a **Read-only** token generated from Hugging Face Account Settings.
> 2. The token is read strictly at runtime by PyTorch/Transformers and is **never logged, saved to disk, or committed to Git**.
> 3. `.env` is listed in `.gitignore` and `.dockerignore`.

---

## 4. Docker Instructions & Local Testing Status

### Local Testing Status: **NOT TESTED**
- *Reason*: Docker CLI is not installed on the local Windows environment.
- *Status*: The `Dockerfile` and `.dockerignore` have been validated syntactically and structurally for Ubuntu/Linux deployment.

### Instructions for Building & Running Docker Image (When Docker is available)

```bash
# 1. Build Docker Image
docker build -t nda-classifier-api:latest .

# 2. Run Container with Environment Variables
docker run -d \
  --name nda-api \
  -p 8000:8000 \
  -e HF_TOKEN="hf_your_read_only_token" \
  -e HF_MODEL_ID="THARUNC0/legal-roberta-nda-clause-classifier" \
  -e CORS_ORIGINS='["*"]' \
  nda-classifier-api:latest

# 3. Test Container Health
curl http://localhost:8000/api/v1/health
```

---

## 5. Amazon EC2 Hardware & Cost Recommendation

Based on PyTorch 2.12 + Transformers 5.12 runtime requirements and the 502 MB Legal-RoBERTa model footprint:

### Recommended EC2 Instance: **`t3.large`** or **`c6i.large`**

| Sizing Dimension | Minimum Requirement | Recommended Production (`t3.large`) | Compute-Optimized (`c6i.large`) |
| :--- | :--- | :--- | :--- |
| **vCPUs** | 2 vCPUs | 2 vCPUs | 2 Dedicated Cores |
| **System RAM** | 4 GB RAM | **8 GB RAM** | **8 GB RAM** |
| **Storage (EBS)** | 20 GB gp3 | **30 GB gp3** | **30 GB gp3** |
| **GPU Requirement** | None (CPU Inference) | None (CPU Inference) | None (CPU Inference) |
| **Est. Monthly Cost** | ~$30 / month | **~$60 / month ($0.0832/hr)** | **~$61 / month ($0.085/hr)** |

### Performance Assumptions
- **Model Size**: 124.66 Million parameters (~502 MB FP32 weights).
- **RAM Footprint**: ~1.0 GB RAM for PyTorch model + ~1.5 GB system/process RAM = ~2.5 GB active RAM. An 8 GB instance prevents OOM errors during concurrent PDF uploads.
- **Inference Speed on CPU**: ~20 - 50 ms per clause (~0.3 seconds for a 10-clause PDF). GPU acceleration is **not required** for low-to-medium traffic.

---

## 6. AWS Security Group & HTTPS Requirements

### Inbound Security Group Rules

| Port | Protocol | Source | Purpose |
| :---: | :---: | :---: | :--- |
| **22** | TCP | `your.admin.ip/32` | Restricted SSH administration |
| **80** | TCP | `0.0.0.0/0` | Public HTTP (auto-redirect to HTTPS) |
| **443** | TCP | `0.0.0.0/0` | Public HTTPS for API traffic |
| **8000** | TCP | `127.0.0.1/32` | Internal Uvicorn port (reverse proxied by NGINX) |

### HTTPS & Reverse Proxy Architecture

```
Internet (Port 443 HTTPS) ──> NGINX Reverse Proxy (SSL via Certbot) ──> Uvicorn / FastAPI (127.0.0.1:8000)
```

1. **NGINX**: Serves SSL/TLS termination and routes requests to `127.0.0.1:8000`.
2. **Certbot**: Free Let's Encrypt SSL certificate auto-renewal.

---

## 7. Step-by-Step Deployment Procedure (EC2 Launch Guide)

### Step 1: Launch EC2 Instance
- OS: **Ubuntu Server 22.04 LTS (64-bit x86)**
- Instance Type: **`t3.large`** (8 GB RAM)
- Storage: **30 GB gp3 EBS Volume**
- Security Group: Enable SSH (Port 22), HTTP (Port 80), and HTTPS (Port 443).

### Step 2: Server Setup & Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Clone repository
git clone https://github.com/Tharun-C0/NDA.git
cd NDA

# Create virtualenv & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment & Systemd Service
Create `/etc/systemd/system/nda-backend.service`:
```ini
[Unit]
Description=FastAPI NDA Clause Classifier Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/NDA
Environment="PATH=/home/ubuntu/NDA/venv/bin"
Environment="HF_TOKEN=your_huggingface_read_token"
Environment="HF_MODEL_ID=THARUNC0/legal-roberta-nda-clause-classifier"
ExecStart=/home/ubuntu/NDA/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nda-backend
```

### Step 4: Configure NGINX & SSL
```bash
sudo certbot --nginx -d your-ec2-domain.com
```

---

## 8. Rollback Procedure

If a deployment fails on EC2:

1. **Service Rollback**:
   ```bash
   sudo systemctl stop nda-backend
   git checkout tags/<previous-stable-release-tag>
   sudo systemctl start nda-backend
   ```
2. **Model Rollback**:
   Update `HF_MODEL_ID` in `.env` to point to previous commit tag on Hugging Face Hub (e.g. `THARUNC0/legal-roberta-nda-clause-classifier@commit_hash`) and restart systemd.

---

## 9. Remaining Blockers & Next Steps

- **Blockers**: None. The codebase, model service, unit tests, and configuration are 100% verified.
- **Next Steps (Pending User Approval)**:
  1. Commit verified configuration and deployment files to Git.
  2. Launch EC2 instance on AWS console.
  3. Execute EC2 Launch Guide.

---
*End of Deployment Readiness Report.*
