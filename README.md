# 🛡️ Hybrid Enterprise SOC & CyberSecurity Homelab (Proxmox VE + Microsoft Azure)

## Overview
This repository documents the architecture, engineering, and operational workflows of my **Hybrid Enterprise Security Operations Center (SOC) and Cyber Range**.

Moving beyond traditional isolated open-source homelabs, this environment bridges on-premises virtualization (**Proxmox VE**) with an enterprise cloud security stack (**Microsoft Sentinel, Microsoft Defender XDR, Microsoft Entra ID P2, and Microsoft Intune**). On-premises virtual machines act as realistic corporate endpoints, domain controllers, and attack targets, while Microsoft Cloud services handle centralized SIEM/SOAR analytics, XDR endpoint telemetry, hybrid identity protection, and automated Cyber Threat Intelligence (MISP) correlation.

## 🏗️ Architecture Evolution: Local Homelab to Hybrid Enterprise SOC

| Architecture Domain | Phase 1: Legacy Local Homelab | Phase 2: Hybrid Enterprise SOC (Current) |
| :--- | :--- | :--- |
| **SIEM / SOAR** | Local Wazuh (OpenSearch) on Ubuntu | **Microsoft Sentinel** (Log Analytics Workspace) |
| **Endpoint Security (EDR/XDR)** | Basic Host Antivirus | **Microsoft Defender for Endpoint (MDE P2)** |
| **Identity & Access (IAM)** | Isolated Active Directory (DC) | **Hybrid AD + Microsoft Entra ID P2** (Entra Connect) |
| **Threat Intelligence (CTI)** | Manual IP lists / local hosts | **MISP (Docker)** synced to Sentinel via Python STIX 2.1 API |
| **Endpoint Policy Management** | Classic AD Group Policy (GPO) | **MDE Management & Microsoft Intune** Policy Sync |
| **Web App Protection (WAF)** | None | **Azure Application Gateway with WAF v2** (OWASP Juice Shop) |

## 💻 Hardware Infrastructure
The on-premises segment utilizes a dedicated workstation for virtualization:

* **Hypervisor:** Proxmox VE 8 (Hosted on HP Z440 Workstation - Intel Xeon, 64GB RAM, 1TB SATA III SSD `LVM-Thin` Storage). This node hosts all corporate endpoints, Active Directory, perimeter firewall, and Threat Intelligence containers.

## 🌐 Network Topology & Segmentation (OPSEC Sanitized)
The local network is logically segmented using a virtualized **pfSense** firewall/router to isolate the SOC Lab (where attack simulations are executed) from the private home network while permitting encrypted outbound telemetry (HTTPS/443) to Microsoft Azure.

* **`vmbr0` (Home LAN - `<HOME_LAN_SUBNET>`):** The primary residential network with internet access and NAS backup storage.
* **`vmbr1` (SOC Lab LAN - `<SOC_LAB_SUBNET>`):** The isolated corporate sandbox environment. All traffic destined for `<HOME_LAN_SUBNET>` is explicitly dropped via top-priority pfSense firewall rules (*silent drop*), while Azure Monitor Agent (AMA) and Defender XDR telemetry flows securely to the cloud.

> <img width="872" height="383" alt="Homelab architecturev2" src="https://github.com/user-attachments/assets/b3567119-9a24-4d39-938a-d38a-d8588fa72ae4" />

## 🖥️ Virtual Machines Inventory (On-Premises Proxmox Node)

The following table details the virtual machine configurations hosted on the Proxmox VE hypervisor (IP addresses are represented using standardized OPSEC placeholders):

| VM ID | Hostname | OS | vCPU | RAM | Network (Bridge) | IP Placeholder | Role / Description |
|---|---|---|---|---|---|---|---|
| **101** | `pfSense-Router` | pfSense CE | 2 | 2 GB | `vmbr0`, `vmbr1` | `<HOME_WAN_IP>` / `<LAB_GATEWAY_IP>` | Perimeter Firewall/Router. Enforces LAN segmentation & RFC 1918 isolation. |
| **102** | `AD-Server-2025` | Windows Server 2025 | 4 | 12.5 GB | `vmbr1` | `<DC_IP>` | Domain Controller (`soclab.local`), DNS, Entra ID Connect, AMA & MDE sensor. |
| **104** | `Win11Victim` | Windows 11 25H2 | 4 | 6.5 GB | `vmbr1` | `<WIN11_VICTIM_IP>` | Domain-joined corporate endpoint (Intune MDM, MDE, AMA, AiTM Attack Target). |
| **105** | `CTI-Node` | Ubuntu Server 26.04 | 4 | 8 GB | `vmbr1` | `<CTI_NODE_IP>` | Docker host running **MISP Threat Intelligence**, **OWASP Juice Shop**, & AMA Syslog. |
| **103** | `Kali-Attacker` | Kali Linux 2026.2 | 4 | 7 GB | `vmbr1` | `<KALI_ATTACKER_IP>` | Red Team machine for credential, RDP, and web application attack simulations. |
| **106** | `TrueNAS` | TrueNAS SCALE | 4 | 12 GB | `vmbr0` | `<TRUENAS_IP>` | ZFS RAID storage server for snapshots, ISOs, and backups. |

## 📂 Repository Structure

* `/iac` – Declarative **Azure Bicep** templates (`landing-zone.bicep`, `sentinel-onboarding.bicep`) adhering to the Microsoft Cloud Adoption Framework (CAF).
* `/src` – Custom **Python 3** scripts automating Threat Intelligence (IOC) extraction from MISP REST API to Microsoft Sentinel in STIX 2.1 format.
* `/kql` – Custom **Kusto Query Language (KQL)** detection rules and Advanced Hunting queries for Microsoft Sentinel and Defender XDR.

## 🛠️ Key Technologies & Enterprise Stack
* **Cloud SIEM & XDR:** Microsoft Sentinel, Log Analytics Workspace, Microsoft Defender XDR, Microsoft Defender for Servers Plan 2, Azure Monitor Agent (AMA) with Data Collection Rules (DCR)
* **Identity & Access Management:** Active Directory Domain Services (AD DS), Microsoft Entra ID P2, Entra ID Protection, Conditional Access, Phishing-Resistant MFA (Passkeys / FIDO2)
* **Endpoint Management:** Microsoft Intune (MDM Auto-Enrollment & EDR Onboarding Policies)
* **Threat Intelligence:** MISP (Docker), Python REST API Connector, STIX 2.1, OSINT Feeds (CIRCL, Botvrij.eu)
* **Web Application Security:** Azure Application Gateway (WAF v2 in Prevention Mode), OWASP Juice Shop (Docker)
* **Infrastructure & Virtualization:** Proxmox VE (QEMU/KVM, LVM-Thin), Azure Bicep (IaC), pfSense Firewall

---
*Disclaimer & OPSEC Notice: This documentation is engineered for cybersecurity portfolio purposes following TLP:CLEAR sanitization standards. All internal RFC 1918 IP addresses, subnet CIDRs, and cloud tenant identifiers have been replaced with semantic placeholders (e.g., `<DC_IP>`, `<CTI_NODE_IP>`, `<SOC_LAB_SUBNET>`).*