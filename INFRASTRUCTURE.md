# 🚀 Techtrackr: Infrastructure Setup Log

A clean, end-to-end record of the infrastructure setup, CI/CD wiring, and cost-control decisions for **Techtrackr**.

---

## 1. ☁️ Cloud Provisioning (Azure)

### Virtual Machine

* **Instance Type:** `Standard_B2ats_v2`
* **OS:** Ubuntu

### Networking & Security

* **Issue:** Jenkins was not accessible on its default port **8080**.
* **Root Cause:** Inbound traffic on port 8080 was blocked.
* **Fix:** Updated **Inbound Security Rules** in the Azure Portal to allow traffic on port **8080**.

  * *(Alternative: Ensure port 80 is correctly mapped when using a reverse proxy.)*

### Cost Management

* **Auto-Shutdown Enabled:** 🕦 **11:30 PM IST**
* **Goal:** Prevent accidental overnight billing and keep cloud costs in check.

---

## 2. ⚙️ Server Configuration

### Jenkins Installation

* **Prerequisite:** Installed **OpenJDK (Java)**
* **Service:** Installed Jenkins (stable) and enabled it as a system service

#### Admin Unlock

Retrieved the initial admin password using:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

---

### Python Environment

* Verified **python3** and **pip** installation
* Required for running the **FastAPI backend**

---

### Docker Setup & Permissions

#### Installation

* Installed Docker:

```bash
sudo apt install docker.io
```

#### Permissions Fix

* **Issue:** `group does not exist` error when Jenkins tried to access Docker
* **Fix:** Manually created the Docker group and linked it to Jenkins

```bash
sudo groupadd docker
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

---

## 3. 📦 Azure Container Registry (ACR) Integration

### Registry

* **Tier:** Basic
* **Purpose:** Store Techtrackr Docker images

### Security – Service Principal (Robot Account)

* Created a dedicated **Service Principal (SP)** to give Jenkins scoped push access

```bash
# Get Registry ID
ACR_ID=$(az acr show --name <acr-name> --query id --output tsv)

# Create Service Principal
az ad sp create-for-rbac --name "Techtrackr-Jenkins-Push-SP" \
  --role AcrPush \
  --scopes $ACR_ID
```

### Jenkins Credentials

* Stored **appId** and **password** in **Jenkins Credentials Manager**
* **Credential ID:** `techtrackr-acr-push`

---

## 4. 🔁 CI/CD Pipeline Logic

### Jenkinsfile (Declarative Pipeline)

The pipeline automates the full container lifecycle:

1. **Build** – Create a Docker image from the Git repository
2. **Auth** – Log in to Azure using the Service Principal via `withCredentials`
3. **Push** – Upload the image to Azure Container Registry
4. **Cleanup** – Remove the local Docker image from the VM to save disk space

---

## ⚠️ Essential Commands Cheat Sheet

| Task                          | Command                                              |
| ----------------------------- | ---------------------------------------------------- |
| Check Jenkins Status          | `sudo systemctl status jenkins`                      |
| Check Docker Access (Jenkins) | `sudo su - jenkins -s /bin/bash -c "docker ps"`      |
| Stop VM (Save Money 💸)       | `az vm deallocate --resource-group <RG> --name <VM>` |
| Check Open Ports              | `sudo netstat -tunlp`                                |

---

✨ **Outcome:** A cost-aware, secure, and production-ready CI/CD infrastructure for Techtrackr — built with clarity, automation, and scalability in mind.
